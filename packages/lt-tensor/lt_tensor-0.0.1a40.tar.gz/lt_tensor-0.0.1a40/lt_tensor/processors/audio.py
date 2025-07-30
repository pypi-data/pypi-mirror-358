__all__ = ["AudioProcessor", "AudioProcessorConfig"]
from lt_tensor.torch_commons import *
from lt_utils.common import *
import librosa
import torchaudio
import numpy as np
from lt_tensor.model_base import Model
from lt_utils.misc_utils import default
from lt_utils.type_utils import is_file, is_array
from lt_utils.file_ops import FileScan, get_file_name, path_to_str
from torchaudio.functional import detect_pitch_frequency
import torch.nn.functional as F
from librosa.filters import mel as _mel_filter_bank

DEFAULT_DEVICE = torch.tensor([0]).device

from lt_tensor.config_templates import ModelConfig


class AudioProcessorConfig(ModelConfig):
    sample_rate: int = 24000
    n_mels: int = 80
    n_fft: int = 1024
    win_length: int = 1024
    hop_length: int = 256
    f_min: float = 0
    f_max: Optional[float] = None
    center: bool = True
    mel_scale: Literal["htk", "slaney"] = "htk"
    std: int = 4
    mean: int = -4
    n_iter: int = 32
    window: Optional[Tensor] = None
    normalized: bool = False
    onesided: Optional[bool] = None
    n_stft: int = None
    mel_default: Literal["torch", "librosa"] = "librosa"

    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: int = 80,
        n_fft: int = 1024,
        win_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        f_min: float = 0,
        f_max: Optional[float] = None,
        center: bool = True,
        mel_scale: Literal["htk", "slaney"] = "htk",
        std: int = 4,
        mean: int = -4,
        normalized: bool = False,
        onesided: Optional[bool] = None,
        mel_default: Literal["torch", "librosa"] = "librosa",
        *args,
        **kwargs,
    ):
        settings = {
            "sample_rate": sample_rate,
            "n_mels": n_mels,
            "n_fft": n_fft,
            "win_length": win_length,
            "hop_length": hop_length,
            "f_min": f_min,
            "f_max": f_max,
            "center": center,
            "mel_scale": mel_scale,
            "std": std,
            "mean": mean,
            "normalized": normalized,
            "onesided": onesided,
            "mel_default": mel_default,
        }
        super().__init__(**settings)
        self.post_process()

    def post_process(self):
        self.n_stft = self.n_fft // 2 + 1
        # some functions needs this to be a non-zero or not None value.
        self.default_f_min = max(self.f_min, (self.sample_rate / (self.n_fft - 1)) * 2)
        self.default_f_max = min(
            default(self.f_max, self.sample_rate // 2), self.sample_rate // 2
        )
        self.hop_length = default(self.hop_length, self.n_fft // 4)
        self.win_length = default(self.win_length, self.n_fft)


def _comp_rms_helper(i: int, audio: Tensor, mel: Optional[Tensor]):
    if mel is None:
        return {"y": audio[i, :]}
    return {"y": audio[i, :], "S": mel[i, :, :]}


class AudioProcessor(Model):
    def __init__(
        self,
        config: Union[AudioProcessorConfig, Dict[str, Any]] = AudioProcessorConfig(),
    ):
        super().__init__()
        assert isinstance(config, (AudioProcessorConfig, dict))
        self.cfg = (
            config
            if isinstance(config, AudioProcessorConfig)
            else AudioProcessorConfig(**config)
        )
        self._mel_spec_torch = torchaudio.transforms.MelSpectrogram(
            sample_rate=self.cfg.sample_rate,
            n_mels=self.cfg.n_mels,
            n_fft=self.cfg.n_fft,
            win_length=self.cfg.win_length,
            hop_length=self.cfg.hop_length,
            center=self.cfg.center,
            f_min=self.cfg.f_min,
            f_max=self.cfg.f_max,
            mel_scale=self.cfg.mel_scale,
            normalized=self.cfg.normalized,
        )

        self.mel_lib_padding = (self.cfg.n_fft - self.cfg.hop_length) // 2
        self.register_buffer(
            "window",
            torch.hann_window(self.cfg.win_length),
        )
        self.register_buffer(
            "mel_filter_bank",
            torch.from_numpy(
                _mel_filter_bank(
                    sr=self.cfg.sample_rate,
                    n_fft=self.cfg.n_fft,
                    n_mels=self.cfg.n_mels,
                    fmin=self.cfg.f_min,
                    fmax=self.cfg.f_max,
                )
            ).float(),
        )

    def spectral_norm(self, x: Tensor, c: int = 1, eps: float = 1e-5) -> Tensor:
        return torch.log(torch.clamp(x, min=eps) * c)

    def spectral_de_norm(self, x: Tensor, c: int = 1) -> Tensor:
        return torch.exp(x) / c

    def log_norm(
        self,
        entry: Tensor,
        eps: float = 1e-5,
        mean: Optional[Number] = None,
        std: Optional[Number] = None,
    ) -> Tensor:
        mean = default(mean, self.cfg.mean)
        std = default(std, self.cfg.std)
        return (torch.log(eps + entry.unsqueeze(0)) - mean) / std

    def compute_mel(
        self,
        wave: Tensor,
        method: Optional[Literal["torch", "librosa"]] = None,
        apply_norm: bool = False,
        eps: Optional[float] = None,
        **kwargs,
    ) -> Tensor:
        method = default(method, self.cfg.mel_default)
        if method == "torch":
            return self.compute_mel_torch(
                wave,
                log_norm=apply_norm,
                eps=eps,
                mean=kwargs.get("mean", None),
                std=kwargs.get("std", None),
            )
        return self.compute_mel_librosa(
            wave,
            log_norm=apply_norm,
            eps=eps,
        )

    def compute_mel_torch(
        self,
        wave: Tensor,
        log_norm: bool = False,
        eps: Optional[float] = None,
        mean: Optional[Number] = None,
        std: Optional[Number] = None,
        *args,
        **kwargs,
    ) -> Tensor:
        """Returns: (M, T) or (B, M, T) if batched"""
        try:
            mel_tensor = self._mel_spec_torch.forward(wave.to(self.device))  # [M, T]

        except RuntimeError as e:
            mel_tensor = self._mel_spec_torch.forward(wave.to(self.device))  # [M, T]
        if log_norm:
            return self.log_norm(mel_tensor, eps, mean, std).squeeze()
        return mel_tensor.squeeze()

    def compute_mel_librosa(
        self,
        wave: Tensor,
        eps: float = 1e-5,
        spectral_norm: bool = False,
        *args,
        **kwargs,
    ) -> Tensor:
        if wave.ndim == 1:
            wave = wave.unsqueeze(0)
        wave = torch.nn.functional.pad(
            wave.unsqueeze(1),
            (self.mel_lib_padding, self.mel_lib_padding),
            mode="reflect",
        ).squeeze(1)
        spec = torch.stft(
            wave,
            self.cfg.n_fft,
            hop_length=self.cfg.hop_length,
            win_length=self.cfg.win_length,
            window=self.window,
            center=self.cfg.center,
            pad_mode="reflect",
            normalized=False,
            onesided=True,
            return_complex=True,
        )
        spec = torch.sqrt(torch.view_as_real(spec).pow(2).sum(-1) + 1e-12)
        try:
            results = torch.matmul(self.mel_filter_bank, spec)
        except RuntimeError:
            self.mel_filter_bank = self.mel_filter_bank.to(self.device)
            self.window = self.window.to(self.device)
            results = torch.matmul(self.mel_filter_bank, spec)
        if spectral_norm:
            return self.spectral_norm(results, eps=eps).squeeze()
        return results.squeeze()

    def compute_rms(
        self,
        audio: Optional[Union[Tensor, np.ndarray]] = None,
        mel: Optional[Tensor] = None,
        frame_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        center: Optional[int] = None,
    ) -> Tensor:
        assert any([audio is not None, mel is not None])
        rms_kwargs = dict(
            frame_length=default(frame_length, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            center=default(center, self.cfg.center),
        )

        if audio is None and mel is not None:
            return self.from_numpy(
                librosa.feature.rms(S=mel, **rms_kwargs)[0]
            ).squeeze()
        default_dtype = audio.dtype
        default_device = audio.device
        if audio.ndim > 1:
            B = audio.shape[0]
        else:
            B = 1
            audio = audio.unsqueeze(0)

        if mel is not None:
            if mel.ndim == 2:
                assert B == 1, "Batch from mel and audio must be the same!"
                mel = mel.unsqueeze(0)
            else:
                assert B == mel.shape[0], "Batch from mel and audio must be the same!"
            mel = self.to_numpy_safe(mel)
        audio = self.to_numpy_safe(audio)
        if B == 1:
            if mel is None:
                return self.from_numpy(
                    librosa.feature.rms(y=audio, **rms_kwargs)[0]
                ).squeeze()
            return self.from_numpy(
                librosa.feature.rms(y=audio, S=mel, **rms_kwargs)[0]
            ).squeeze()
        else:
            rms_ = []
            for i in range(B):
                _t = _comp_rms_helper(i, audio, mel)
                _r = librosa.feature.rms(**_t, **rms_kwargs)[0]
                rms_.append(_r)
            return self.from_numpy_batch(rms_, default_device, default_dtype).squeeze()

    def pitch_shift(
        self,
        audio: torch.Tensor,
        sample_rate: Optional[int] = None,
        n_steps: float = 2.0,
    ) -> Tensor:
        """
        Shifts the pitch of an audio tensor by `n_steps` semitones.

        Args:
            audio (torch.Tensor): Tensor of shape (B, T) or (T,)
            sample_rate (int, optional): Sample rate of the audio. Will use the class sample rate if unset.
            n_steps (float): Number of semitones to shift. Can be negative.

        Returns:
            torch.Tensor: Pitch-shifted audio.
        """
        src_device = audio.device
        src_dtype = audio.dtype
        audio = audio.squeeze()
        sample_rate = default(sample_rate, self.cfg.sample_rate)

        def _shift_one(wav):
            wav_np = self.to_numpy_safe(wav)
            shifted_np = librosa.effects.pitch_shift(
                wav_np, sr=sample_rate, n_steps=n_steps
            )
            return torch.from_numpy(shifted_np)

        if audio.ndim == 1:
            return _shift_one(audio).to(device=src_device, dtype=src_dtype)
        return torch.stack([_shift_one(a) for a in audio]).to(
            device=src_device, dtype=src_dtype
        )

    def compute_pitch(
        self,
        audio: Tensor,
        *,
        pad_mode: str = "constant",
        trough_threshold: float = 0.1,
        fmin: float = librosa.note_to_hz("C2"),
        fmax: float = librosa.note_to_hz("C7"),
        sr: Optional[float] = None,
        frame_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        center: Optional[bool] = None,
    ) -> Tensor:
        default_dtype = audio.dtype
        default_device = audio.device
        if audio.ndim > 1:
            B = audio.shape[0]
        else:
            B = 1
        sr = default(sr, self.cfg.sample_rate)
        frame_length = default(frame_length, self.cfg.n_fft)
        fmax = min(max(fmax, fmin + 1), sr // 2)
        hop_length = default(hop_length, self.cfg.hop_length)
        center = default(center, self.cfg.center)
        yn_kwargs = dict(
            fmin=fmin,
            fmax=fmax,
            frame_length=frame_length,
            sr=sr,
            hop_length=hop_length,
            center=center,
            trough_threshold=trough_threshold,
            pad_mode=pad_mode,
        )
        if B == 1:
            f0 = self.from_numpy(
                librosa.yin(self.to_numpy_safe(audio), **yn_kwargs),
                default_device,
                default_dtype,
            )

        else:
            f0_ = []
            for i in range(B):
                f0_.append(librosa.yin(self.to_numpy_safe(audio[i, :]), **yn_kwargs))
            f0 = self.from_numpy_batch(f0_, default_device, default_dtype)
        return f0.squeeze()

    def compute_pitch_torch(
        self,
        audio: Tensor,
        fmin: Optional[float] = None,
        fmax: Optional[float] = None,
        sr: Optional[float] = None,
        win_length: Optional[Number] = None,
        frame_length: Optional[Number] = None,
    ) -> Tensor:
        sr = default(sr, self.cfg.sample_rate)
        win_length = default(win_length, self.cfg.win_length)
        frame_length = default(frame_length, self.cfg.n_fft)
        fmin = default(fmin, self.calc_pitch_fmin(sr, frame_length))
        fmax = default(fmax, self.cfg.default_f_max)
        return detect_pitch_frequency(
            audio,
            sample_rate=sr,
            frame_time=frame_length,
            win_length=win_length,
            freq_low=fmin,
            freq_high=fmax,
        ).squeeze()

    def from_numpy(
        self,
        array: np.ndarray,
        device: Optional[torch.device] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> Tensor:
        converted = torch.from_numpy(array)
        if device is None:
            device = self.device
        return converted.to(device=device, dtype=dtype)

    def from_numpy_batch(
        self,
        arrays: List[np.ndarray],
        device: Optional[torch.device] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> Tensor:
        stacked = torch.stack([torch.from_numpy(x) for x in arrays])
        if device is None:
            device = self.device
        return stacked.to(device=device, dtype=dtype)

    def to_numpy_safe(self, tensor: Union[Tensor, np.ndarray]) -> np.ndarray:
        if isinstance(tensor, np.ndarray):
            return tensor
        return tensor.detach().to(DEFAULT_DEVICE).numpy(force=True)

    def interpolate(
        self,
        tensor: Tensor,
        target_len: int,
        mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
            "area",
            "nearest-exact",
        ] = "nearest",
        align_corners: Optional[bool] = None,
        scale_factor: Optional[list[float]] = None,
        recompute_scale_factor: Optional[bool] = None,
        antialias: bool = False,
    ) -> Tensor:
        """
        The modes available for upsampling are: `nearest`, `linear` (3D-only),
        `bilinear`, `bicubic` (4D-only), `trilinear` (5D-only)
        """
        tensor = tensor.squeeze()
        if tensor.ndim == 2:  # [1, T]
            tensor = tensor.unsqueeze(1)  # [1, 1, T]
        elif tensor.ndim == 1:
            tensor = tensor.unsqueeze(0).unsqueeze(0)  # [1, 1, T]
        return F.interpolate(
            tensor,
            size=target_len,
            mode=mode,
            align_corners=align_corners,
            scale_factor=scale_factor,
            recompute_scale_factor=recompute_scale_factor,
            antialias=antialias,
        )

    def istft_spec_phase(
        self,
        spec: Tensor,
        phase: Tensor,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        length: Optional[int] = None,
        center: bool = True,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
    ) -> Tensor:
        """Util for models that needs to reconstruct the audio using inverse stft"""
        window = (
            torch.hann_window(win_length, device=spec.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(spec.device)
        )
        return torch.istft(
            spec * torch.exp(phase * 1j),
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            length=length,
            return_complex=return_complex,
        )

    def istft(
        self,
        wave: Tensor,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        length: Optional[int] = None,
        center: bool = True,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
    ) -> Tensor:
        window = (
            torch.hann_window(win_length, device=wave.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(wave.device)
        )
        if not torch.is_complex(wave):
            wave = wave * 1j
        return torch.istft(
            wave,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            length=length,
            return_complex=return_complex,
        )

    def stft(
        self,
        wave: Tensor,
        center: bool = True,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = True,
    ) -> Tensor:

        window = (
            torch.hann_window(win_length, device=wave.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(wave.device)
        )

        results = torch.stft(
            input=wave,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            pad_mode="reflect",
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            return_complex=True,  # always, then if we need a not complex type we use view as real.
        )
        if not return_complex:
            return torch.view_as_real(results)
        return results

    def istft_norm(
        self,
        wave: Tensor,
        length: Optional[int] = None,
        center: bool = True,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
    ) -> Tensor:
        window = (
            torch.hann_window(win_length, device=wave.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(wave.device)
        )
        spectrogram = torch.stft(
            input=wave,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            pad_mode="reflect",
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            return_complex=True,
        )
        return torch.istft(
            spectrogram
            * torch.full(
                spectrogram.size(),
                fill_value=1,
                device=spectrogram.device,
            ),
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=self.window,
            length=length,
            center=center,
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            return_complex=return_complex,
        )

    def load_audio(
        self,
        path: PathLike,
        top_db: Optional[float] = None,
        mono: bool = True,
        istft_norm: bool = True,
        lib_norm: bool = False,
        *,
        sample_rate: Optional[float] = None,
        duration: Optional[float] = None,
        offset: float = 0.0,
        dtype: Any = np.float32,
        res_type: str = "soxr_hq",
        fix: bool = True,
        scale: bool = False,
        axis: int = -1,
        norm: Optional[float] = np.inf,
        norm_axis: int = 0,
        norm_threshold: Optional[float] = None,
        norm_fill: Optional[bool] = None,
        ref: float | Callable[[np.ndarray], Any] = np.max,
    ) -> Tensor:
        is_file(path, True)
        sample_rate = default(sample_rate, self.cfg.sample_rate)
        wave, sr = librosa.load(
            str(path),
            sr=sample_rate,
            mono=mono,
            offset=offset,
            duration=duration,
            dtype=dtype,
            res_type=res_type,
        )
        if sr != sample_rate:
            wave = librosa.resample(
                wave,
                orig_sr=sr,
                target_sr=sample_rate,
                res_type=res_type,
                fix=fix,
                scale=scale,
                axis=axis,
            )
        if top_db is not None:
            wave, _ = librosa.effects.trim(wave, top_db=top_db)
        if lib_norm:
            wave = librosa.util.normalize(
                wave,
                norm=norm,
                axis=norm_axis,
                threshold=norm_threshold,
                fill=norm_fill,
            )
        results = torch.from_numpy(wave).float().unsqueeze(0).to(self.device)
        if istft_norm:
            results = self.istft_norm(results)
        return torch.from_numpy(wave).float().unsqueeze(0).to(self.device)

    def find_audios(
        self,
        path: PathLike,
        additional_extensions: List[str] = [],
        maximum: int | None = None,
    ):
        extensions = [
            "*.wav",
            "*.aac",
            "*.m4a",
            "*.mp3",
            "*.ogg",
            "*.opus",
            "*.flac",
        ]
        extensions.extend(
            [x for x in additional_extensions if isinstance(x, str) and "*" in x]
        )
        return FileScan.files(
            path,
            extensions,
            maximum,
        )

    def audio_to_half(self, audio: Tensor):
        audio = self.to_numpy_safe(audio)
        data: np.ndarray = audio / np.abs(audio).max()
        data = (data * 32767.0).astype(np.int16)
        return self.from_numpy(data, dtype=torch.float16)

    def forward(
        self,
        x: Union[str, Path, Tensor],
        *,
        spectral_norm: bool = False,
        add_batch_to_all: bool = False,
        wave_batch_dim: bool = False,
        mel_batch_dim: bool = False,
        pitch_batch_dim: bool = False,
        rms_batch_dim: bool = False,
        spec_phase_batch_dim: bool = False,
    ):
        results = {
            "wave": None,
            "mel": None,
            "pitch": None,
            "rms": None,
            "spec": None,
            "phase": None,
        }
        results["wave"] = (
            x.squeeze()
            if isinstance(x, Tensor)
            else self.load_audio(x, istft_norm=True).squeeze()
        )
        results["mel"] = self.compute_mel_librosa(
            wave=(
                results["wave"]
                if results["wave"].ndim == 3
                else results["wave"].unsqueeze(0)
            ),
            spectral_norm=spectral_norm,
        ).squeeze()
        try:
            results["pitch"] = self.compute_pitch(results["wave"]).squeeze()
        except Exception as e:
            results["pitch"] = e
        try:
            results["rms"] = self.compute_rms(results["wave"], results["mel"]).squeeze()
        except Exception as e:
            results["rms"] = e
        try:
            sp_ph = self.stft(results["wave"], return_complex=False)
            spec, phase = sp_ph.split(1, -1)
            results["spec"] = spec.squeeze()
            results["phase"] = phase.squeeze()
        except Exception as e:
            results["spec"] = e
            results["phase"] = e

        if (add_batch_to_all or wave_batch_dim) and results["wave"].ndim == 1:
            results["wave"] = results["wave"].unsqueeze(0)
        if (add_batch_to_all or mel_batch_dim) and results["mel"].ndim == 2:
            results["mel"] = results["mel"].unsqueeze(0)
        if (
            isinstance(results["rms"], Tensor)
            and (add_batch_to_all or rms_batch_dim)
            and results["rms"].ndim == 1
        ):
            results["rms"] = results["rms"].unsqueeze(0)
        if (
            isinstance(results["pitch"], Tensor)
            and (add_batch_to_all or pitch_batch_dim)
            and results["pitch"].ndim == 1
        ):
            results["pitch"] = results["pitch"].unsqueeze(0)
        if (
            isinstance(results["spec"], Tensor)
            and (add_batch_to_all or spec_phase_batch_dim)
            and results["spec"].ndim == 2
        ):
            results["spec"] = results["spec"].unsqueeze(0)
            results["phase"] = results["phase"].unsqueeze(0)

        return results
