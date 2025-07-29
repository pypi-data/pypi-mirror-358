from svsdatasetio.getlabels import load_ph
import torch
import os
import typing
import torchaudio
import torchaudio.transforms as T
import torch.nn.functional as F

class DatasetSection:
    def __init__(self, waveform: torch.Tensor, melspec: torch.Tensor, ph: list[str], dur: list[int]):
        self.__waveform = waveform
        self.__melspec = melspec
        self.__ph = ph
        self.__dur = dur
    @property
    def waveform(self) -> torch.Tensor:
        return self.__waveform
    @property
    def melspec(self) -> torch.Tensor:
        return self.__melspec
    @property
    def phonemes(self) -> list[str]:
        return self.__ph[:]
    @property
    def duration(self) -> list[int]:
        return self.__dur[:]
    @property
    def labels(self) -> list[tuple[str, int]]:
        return list(zip(self.__ph, self.__dur))

class Dataset:
    def __init__(self, path: str):
        self.__datas: list[tuple[str, list[str], list[float]]] = []
        for filename in os.listdir(path):
            if not filename.lower().endswith(".wav"):
                continue
            w_path = os.path.join(path, filename)
            t_path = os.path.join(path, "TextGrid", filename[:-4]+".TextGrid")
            if not os.path.exists(t_path):
                continue
            ph, dur = load_ph(t_path)
            if ph is None or len(ph) == 0:
                continue
            self.__datas.append((w_path, ph, dur))
            self.__index = 0
    def __len__(self) -> int:
        return len(self.__datas)
    def __getitem__(self, index: int) -> DatasetSection:
        wavfile, phonemes, duration = self.__datas[index]
        waveform, sample_rate = torchaudio.load(wavfile)
        if sample_rate != 44100:
            waveform = T.Resample(sample_rate, 44100)(waveform)
        melspec = torch.log2(T.MelSpectrogram(
            sample_rate=44100,
            n_fft=2048,
            win_length=2048,
            hop_length=256,
            n_mels=128,
            power=1.0
        )(waveform)[0, :, :].clamp(min=1e-7))
        duration = torch.tensor([ n * (melspec.shape[-1] / sum(duration)) for n in duration ])
        ticking = torch.round(torch.cat([torch.tensor([0]), torch.cumsum(duration, dim=0)], dim=0))
        ticking[-1] = melspec.shape[-1]
        duration = torch.diff(ticking, dim=0)
        waveform = waveform[0, :]
        if waveform.shape[0] < melspec.shape[-1] * 256:
            waveform = F.pad(waveform[None, None, :], pad=(0, melspec.shape[-1] * 256 - waveform.shape[0]))[0, 0, :]
        if waveform.shape[0] > melspec.shape[-1] * 256:
            waveform = waveform[:melspec.shape[-1] * 256]
        return DatasetSection(waveform, melspec, phonemes, [ int(n) for n in duration ])
    def read(self) -> typing.Optional[DatasetSection]:
        if self.__index >= len(self.__datas):
            return None
        R = self.__getitem__(self.__index)
        self.__index += 1
        return R
    def seek(self, pos: int):
        if pos < 0:
            pos = 0
        if pos >= len(self.__index):
            pos = len(self.__index) - 1
        self.__index = pos
    def tell(self) -> int:
        return self.__index
    def __iter__(self):
        return DatasetIterator(self)

class DatasetIterator:
    def __init__(self, dataset: Dataset):
        self.__dataset = dataset
        self.__index = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.__index >= len(self.__dataset):
            raise StopIteration()
        index = self.__index
        self.__index += 1
        return self.__dataset[index]