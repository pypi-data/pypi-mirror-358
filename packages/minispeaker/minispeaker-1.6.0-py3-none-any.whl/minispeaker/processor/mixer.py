# Typing
from typing_extensions import List, Callable, Dict
from minispeaker.tracks import Track
from minispeaker.asyncsync import Event
from numpy.typing import DTypeLike
from numpy import ndarray
from miniaudio import PlaybackCallbackGeneratorType

# Main dependencies
import numpy as np


# `master_mixer` was written with explicit parameter support via Claude Onus 4 and modified+tested for correctness
def master_mixer(
    tracks: Dict[str, Track],
    stopped: Event,
    paused: Callable[[], bool],
    muted: Callable[[], bool],
    volume: Callable[[], float],
    dtype: DTypeLike,
) -> PlaybackCallbackGeneratorType:
    """Audio processor that merges multiple audio stream with master controls.

    Args:
        tracks (Dict[str, Track]): Multiple audio streams represented as a dictionary of `Track`s.
        stopped (Event): When `master_mixer` should end.
        paused (Callable[[], bool]): When `paused` is evaluated to `True`, no audio streams will continue.
        muted (Callable[[], bool]): When `muted` is evaluated to `True`, all audio streams will continue but will play no sound.
        volume (Callable[[], float]): Master volume.
        dtype (DTypeLike): SampleFormat equivalent of the underlying audio streams.

    Returns:
        PlaybackCallbackGeneratorType: A miniaudio compatible generator.

    Yields:
        Iterator[PlaybackCallbackGeneratorType]: Miniaudio compatible audio data.
    """
    num_frames = yield b""

    while not stopped.is_set():
        if not paused():
            chunks: List[ndarray] = []
            volumes: List[float] = []

            for track in list(tracks.values()):
                if not track.paused:
                    try:
                        chunks.append(track.chunk(num_frames))
                        volumes.append(track.volume)
                    except StopIteration:
                        continue
            if muted() or not chunks:
                yield 0
            else:
                audio = (volume() * np.average(chunks, axis=0, weights=volumes)).astype(
                    dtype
                )
                yield audio
