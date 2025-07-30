# tests/test_tqdm_sound.py

import json
import time
import pytest
from tqdm_sound.tqdm_sound import TqdmSound, SoundProgressBar

class DummyManager:
    def __init__(self):
        # record of all calls for assertions
        self.calls = []
        # needed by SoundProgressBar._update_volume()
        self._muted = False
        # placeholders for volume values
        self.volume = 1.0
        self.background_volume = 1.0

    def set_volume(self, volume, mute, background_volume=None):
        # mimic TqdmSound.set_volume behavior
        self._muted = mute
        self.volume = 0.0 if mute else volume
        if background_volume is not None:
            self.background_volume = 0.0 if mute else background_volume

    def play_sound(self, name):
        self.calls.append(("sound", name))

    def play_random_click(self):
        self.calls.append(("random_click", None))

    def _stop_background(self):
        self.calls.append(("stop_background", None))


def test_set_volume_mute_and_unmute():
    ts = TqdmSound(theme="ryoji_ikeda")
    ts.set_volume(volume=0.7, mute=True, background_volume=0.4)
    assert ts.volume == 0.0
    assert ts.background_volume == 0.0

    ts.set_volume(volume=0.3, mute=False, background_volume=0.2)
    assert ts.volume == 0.3
    assert ts.background_volume == 0.2


def test_invalid_volume_parameters():
    with pytest.raises(ValueError):
        TqdmSound(volume=-1)
    with pytest.raises(ValueError):
        TqdmSound(background_volume=101)


def test_missing_theme_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        TqdmSound(theme="this_theme_does_not_exist")


def test_compute_muted_state_dynamic_overrides_activity(tmp_path):
    cfg = tmp_path / "settings.json"
    cfg.write_text(json.dumps({"is_muted": True}))
    ts = TqdmSound(activity_mute_seconds=5, dynamic_settings_file=str(cfg))
    assert ts._compute_muted_state() is True

    cfg.write_text(json.dumps({"is_muted": False}))
    assert ts._compute_muted_state() is False


def test_compute_muted_state_activity_timeout():
    ts = TqdmSound(activity_mute_seconds=1)
    ts.last_activity_time = time.time()
    assert ts._compute_muted_state() is True

    ts.last_activity_time = time.time() - 5
    assert ts._compute_muted_state() is False


def test_iteration_sound_sequence_and_end_behavior():
    dummy = DummyManager()
    data = [0, 1, 2, 3]
    bar = SoundProgressBar(
        iterable=data,
        desc="test",
        total=len(data),
        ten_percent_ticks=False,
        play_end_sound=True,
        all_ticks_semi_major_tone=False,
        sound_manager=dummy,
    )

    result = list(bar)
    assert result == data

    # start sequence
    assert dummy.calls[0] == ("sound", "start")
    assert dummy.calls[1] == ("sound", "background")

    # one click per iteration
    assert sum(1 for c in dummy.calls if c[0] == "random_click") == len(data)

    # midpoint at 50%
    assert sum(1 for c in dummy.calls if c == ("sound", "mid")) == 1

    # end and stop background
    assert dummy.calls[-2] == ("sound", "end")
    assert dummy.calls[-1] == ("stop_background", None)


def test_all_ticks_semi_major_tone_flag():
    dummy = DummyManager()
    data = [0, 1, 2, 3]
    bar = SoundProgressBar(
        iterable=data,
        desc="semi-test",
        total=len(data),
        ten_percent_ticks=False,
        play_end_sound=False,
        all_ticks_semi_major_tone=True,
        sound_manager=dummy,
    )

    _ = list(bar)
    semi_calls = [c for c in dummy.calls if c == ("sound", "semi_major")]
    assert len(semi_calls) == len(data)
