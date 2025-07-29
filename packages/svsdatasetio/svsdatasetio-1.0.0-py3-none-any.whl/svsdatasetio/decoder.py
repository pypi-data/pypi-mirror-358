import torch
import torchaudio
import torchaudio.transforms as T

def melspec2wave(melspec: torch.Tensor, n_iter: int=300) -> torch.Tensor:
    spec = T.InverseMelScale(n_stft=1025, n_mels=128, sample_rate=44100)(melspec[None, :, :].exp())
    wave = T.GriffinLim(
        n_fft=2048,
        n_iter=n_iter,
        win_length=2048,
        hop_length=256,
        power=1.0
    )(spec)
    return wave[0, :]

def melspec2wavfile(melspec: torch.Tensor, filename: str, n_iter: int=300):
    waveform = melspec2wave(melspec, n_iter=n_iter)
    torchaudio.save(filename, waveform[None, :], 44100)

def wavfile2melspec(wavfile: str) -> torch.Tensor:
    waveform, sample_rate = torchaudio.load(wavfile)
    if sample_rate != 44100:
        waveform = T.Resample(sample_rate, 44100)(waveform)
    return wav2melspec(waveform[0, :])

def wav2melspec(waveform: torch.Tensor):
    return torch.log2(T.MelSpectrogram(
        sample_rate=44100,
        n_fft=2048,
        win_length=2048,
        hop_length=256,
        n_mels=128,
        power=1.0
    )(waveform).clamp(min=1e-7))