import textgrid
import typing

def load_ph(tg_file: str) -> typing.Union[tuple[None, None], tuple[list[str], list[float]]]:
    tg = textgrid.TextGrid()
    tg.read(tg_file)
    T = None
    for tier in tg.tiers:
        if isinstance(tier, textgrid.IntervalTier) and tier.name == "phones":
            T = tier
            break
    if T is None:
        return (None, None)
    phonemes = []
    duration = []
    for line in T.intervals:
        if isinstance(line, textgrid.Interval):
            phonemes.append(line.mark)
            duration.append(line.duration())
    return phonemes, duration