import json
import random
import threading
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

import numpy as np
import sounddevice as sd
import soundfile as sf
from importlib import resources
from pynput import keyboard, mouse
from tqdm import tqdm


class TqdmSound:
    """
    Manages sound playback for progress bars without unsafe threading or I/O in callbacks.

    Attributes:
        theme: Sound theme directory name.
        volume: Normalized foreground volume [0-1].
        background_volume: Normalized background volume [0-1].
        activity_mute_seconds: Seconds after activity to mute.
        dynamic_settings_file: Optional Path to a JSON file controlling mute.
    """

    def __init__(
        self,
        theme: str = "ryoji_ikeda",
        volume: int = 100,
        background_volume: int = 50,
        activity_mute_seconds: Optional[int] = 0,
        dynamic_settings_file: Optional[str] = None,
    ) -> None:
        """
        Initialize the TqdmSound manager.

        Args:
            theme: Name of the theme folder under sounds/.
            volume: Foreground volume percentage (0-100).
            background_volume: Background volume percentage (0-100).
            activity_mute_seconds: Mute duration after user input (sec).
            dynamic_settings_file: Path to JSON file with {"is_muted": true/false}.

        Raises:
            ValueError: If volume parameters out of range.
            FileNotFoundError: If sound files or theme missing.
        """
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")
        if not 0 <= background_volume <= 100:
            raise ValueError("Background volume must be between 0 and 100")

        self.volume = volume / 100
        self.background_volume = background_volume / 100
        self.theme = theme
        self.activity_mute_seconds = activity_mute_seconds

        if dynamic_settings_file:
            settings_path = Path(dynamic_settings_file)
            if not settings_path.exists():
                raise FileNotFoundError(f"Dynamic settings file does not exist: {settings_path}")
            self.dynamic_settings_file: Optional[Path] = settings_path
        else:
            self.dynamic_settings_file = None


        self.sounds: Dict[str, Tuple[np.ndarray, int]] = {}
        self.click_sounds: list[Tuple[np.ndarray, int]] = []
        self.bg_data: Optional[np.ndarray] = None
        self.bg_samplerate: Optional[int] = None
        self.bg_stream: Optional[sd.OutputStream] = None

        self._load_sounds()

        self.last_activity_time: float = time.time()
        self.mouse_listener: Any
        self.keyboard_listener: Any
        self._setup_activity_monitors()

        self._muted: bool = False
        self._stop_flag: bool = False
        self._mute_thread: Optional[threading.Thread] = None
        self._start_mute_watcher()

        self._bg_started: bool = False
        self._bg_pos: int = 0

    def __del__(self) -> None:
        self.close()

    def _load_sounds(self) -> None:
        """
        Load click effects, fixed tones, and background into memory as NumPy arrays.

        Raises:
            FileNotFoundError: If expected files/directories are missing.
        """
        base = Path(resources.files("tqdm_sound")).joinpath("sounds", self.theme)
        if not base.exists():
            raise FileNotFoundError(f"Theme directory {base} not found")

        for click_file in base.glob("click_*.wav"):
            data, sr = sf.read(str(click_file), dtype="float32")
            self.click_sounds.append((data, sr))

        file_mapping = {
            "start": "start_tone.wav",
            "semi_major": "semi_major.wav",
            "mid": "mid_tone.wav",
            "end": "end_tone.wav",
            "program_end": "program_end_tone.wav",
            "background": "background_tone.wav",
        }
        for name, filename in file_mapping.items():
            path = base / filename
            if not path.exists():
                raise FileNotFoundError(f"Missing sound file: {path}")

            data, sr = sf.read(str(path), dtype="float32")
            if name == "background":
                self.bg_data = data
                self.bg_samplerate = sr
            else:
                self.sounds[name] = (data, sr)

    def _setup_activity_monitors(self) -> None:
        """
        Launch listeners to reset activity timestamp on mouse/keyboard events.
        """
        self.mouse_listener = mouse.Listener(
            on_move=self._update_activity,
            on_click=self._update_activity,
            on_scroll=self._update_activity,
        )
        self.keyboard_listener = keyboard.Listener(on_press=self._update_activity)
        self.mouse_listener.start()
        self.keyboard_listener.start()

        if self.activity_mute_seconds:
            # allow immediate sound if starting muted
            self.last_activity_time = time.time() - self.activity_mute_seconds

    def _update_activity(self, *args: Any, **kwargs: Any) -> None:
        """
        Record the time of latest user interaction.
        """
        self.last_activity_time = time.time()

    def _compute_muted_state(self) -> bool:
        """
        Determine mute state, preferring dynamic_settings_file over activity timeout.

        Returns:
            True if muted, False otherwise.
        """
        # 1) dynamic settings override
        if self.dynamic_settings_file and self.dynamic_settings_file.exists():
            try:
                cfg = json.loads(self.dynamic_settings_file.read_text())
                if "is_muted" in cfg:
                    return bool(cfg["is_muted"])
                return False
            except Exception:
                raise "Config error"

        # 2) activity-based mute
        if self.activity_mute_seconds and (time.time() - self.last_activity_time) < self.activity_mute_seconds:
            return True

        # 3) default unmuted
        return False

    def _check_muted_flag(self) -> None:
        """
        Background thread: update self._muted every 100ms.
        """
        while not self._stop_flag:
            self._muted = self._compute_muted_state()
            time.sleep(0.1)

    def _start_mute_watcher(self) -> None:
        """
        Start the thread watching for mute changes.
        """
        self._mute_thread = threading.Thread(target=self._check_muted_flag, daemon=True)
        self._mute_thread.start()

    def _stop_mute_watcher(self) -> None:
        """
        Stop and join the mute watcher thread.
        """
        self._stop_flag = True
        if self._mute_thread:
            self._mute_thread.join(timeout=0.5)

    def set_volume(
        self,
        volume: float,
        mute: bool = False,
        background_volume: Optional[float] = None,
    ) -> None:
        """
        Update normalized volumes, with optional mute.

        Args:
            volume: Foreground volume (0-1).
            mute: If True, silence all.
            background_volume: Background volume override (0-1).
        """
        self.volume = 0.0 if mute else volume
        if background_volume is not None:
            self.background_volume = 0.0 if mute else background_volume

    def _play(
        self,
        data: np.ndarray,
        samplerate: int,
        override_volume: Optional[float] = None,
    ) -> None:
        """
        Play a buffer via sounddevice, respecting mute and volume.
        """
        if self._muted:
            return
        vol = self.volume if override_volume is None else override_volume
        if vol <= 0:
            return
        sd.play(data * vol, samplerate)

    def _mix_background_chunk(self, frames: int) -> np.ndarray:
        """
        Create a background audio chunk of length frames.
        """
        if self.bg_data is None or self.bg_samplerate is None:
            return np.zeros((frames,))
        length = len(self.bg_data)
        if self._bg_pos + frames <= length:
            chunk = self.bg_data[self._bg_pos : self._bg_pos + frames]
        else:
            first_part = self.bg_data[self._bg_pos : length]
            second_part = self.bg_data[0 : frames - (length - self._bg_pos)]
            chunk = np.concatenate((first_part, second_part), axis=0)
        self._bg_pos = (self._bg_pos + frames) % length
        return chunk * self.background_volume  # type: ignore

    def _start_background_loop(self) -> None:
        """
        Start continuous background playback via callback.
        """
        if self._bg_started or self.bg_data is None or self.bg_samplerate is None:
            return
        self._bg_started = True
        self._bg_pos = 0
        channels = (
            self.bg_data.shape[1]
            if hasattr(self.bg_data, "ndim") and self.bg_data.ndim > 1
            else 1
        )
        def callback(outdata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
            if self._muted or self.background_volume <= 0:
                outdata.fill(0)
                return
            chunk = self._mix_background_chunk(frames)
            if channels > 1 and chunk.ndim == 1:
                chunk = np.tile(chunk[:, None], (1, channels))
            outdata[:] = chunk
        self.bg_stream = sd.OutputStream(
            samplerate=self.bg_samplerate, channels=channels, callback=callback
        )
        self.bg_stream.start()

    def _stop_background(self) -> None:
        """
        Stop background playback and reset state.
        """
        if self.bg_stream:
            self.bg_stream.stop()
            self.bg_stream.close()
        self._bg_started = False

    def play_sound(self, sound_name: str) -> None:
        """
        Play a named tone or start background loop.

        Args:
            sound_name: 'start', 'semi_major', 'mid', 'end', 'program_end', or 'background'.
        """
        if sound_name == "background":
            self._start_background_loop()
            return
        if self._muted:
            return
        pair = self.sounds.get(sound_name)
        if not pair:
            return
        data, sr = pair
        self._play(data, sr)

    def play_random_click(self) -> None:
        """
        Play one randomly chosen click effect.
        """
        if self._muted or not self.click_sounds:
            return
        data, sr = random.choice(self.click_sounds)
        self._play(data, sr)

    def play_final_end_tone(self, volume: Optional[int] = None) -> None:
        """
        Play the program_end tone optionally at a different volume.

        Args:
            volume: Override foreground volume percent.
        """
        if self._muted:
            return
        pair = self.sounds.get("program_end")
        if not pair:
            return
        data, sr = pair
        vol = volume / 100 if volume is not None else self.volume
        self._play(data, sr, override_volume=vol)

    def progress_bar(
        self,
        iterable: Iterable,
        desc: str,
        volume: Optional[int] = 100,
        background_volume: Optional[int] = 80,
        end_wait: float = 0.04,
        ten_percent_ticks: bool = False,
        play_end_sound: bool = True,
        all_ticks_semi_major_tone: bool = False,
        **tqdm_kwargs: Any,
    ) -> "SoundProgressBar":
        """
        Wrap an iterable in a sound-enabled tqdm and return the bar.

        Args:
            iterable: Any iterable to track.
            desc: Progress description.
            volume: Foreground volume percent override.
            background_volume: Background volume percent override.
            end_wait: Delay after completion (sec).
            ten_percent_ticks: Enable ticks every 10%.
            play_end_sound: Plays a final tone at the end.
            all_ticks_semi_major_tone: Play 'semi_major' on every tick instead of random clicks.
            **tqdm_kwargs: Additional tqdm args.

        Returns:
            SoundProgressBar instance.
        """
        vol = volume / 100 if volume is not None else self.volume
        bg = background_volume / 100 if background_volume is not None else self.background_volume
        self.set_volume(vol, False, bg)
        try:
            total = len(iterable)  # type: ignore[arg-type]
        except (TypeError, AttributeError):
            total = None
        common: Dict[str, Any] = {
            "iterable": iterable,
            "desc": desc,
            "total": total,
            "volume": vol,
            "background_volume": bg,
            "end_wait": end_wait,
            "ten_percent_ticks": ten_percent_ticks,
            "play_end_sound": play_end_sound,
            "all_ticks_semi_major_tone": all_ticks_semi_major_tone,
            "sound_manager": self,
        }
        common.update(tqdm_kwargs)
        return SoundProgressBar(**common)

    def close(self) -> None:
        """
        Stop listeners, background loop, and clean up.
        """
        if hasattr(self, "mouse_listener") and self.mouse_listener.running:
            self.mouse_listener.stop()
        if hasattr(self, "keyboard_listener") and self.keyboard_listener.running:
            self.keyboard_listener.stop()
        self._stop_background()
        self._stop_mute_watcher()


class SoundProgressBar(tqdm):
    """
    tqdm subclass that triggers sounds at progress<br/>milestones.
    """

    def __init__(
        self,
        iterable: Iterable,
        desc: str,
        total: Optional[int] = None,
        volume: float = 1.0,
        background_volume: float = 1.0,
        end_wait: float = 0.04,
        ten_percent_ticks: bool = False,
        play_end_sound: bool = True,
        sound_manager: TqdmSound = None,
        all_ticks_semi_major_tone: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the SoundProgressBar.

        Args:
            iterable: Iterable to wrap.
            desc: Description text.
            total: Total count for tqdm (optional).
            volume: Foreground volume (0-1).
            background_volume: Background volume (0-1).
            end_wait: Delay after finish (sec).
            ten_percent_ticks: Toggle 10% ticks.
            play_end_sound: Play end tone.
            sound_manager: TqdmSound instance for playback.
            all_ticks_semi_major_tone: Play semi_major on every iteration.
            **kwargs: Other tqdm parameters.
        """
        self.sound_manager = sound_manager
        self.volume = volume
        self.background_volume = background_volume
        self.end_wait = end_wait
        self.ten_percent_ticks = ten_percent_ticks
        self.play_end_sound = play_end_sound
        self.all_ticks_semi_major_tone = all_ticks_semi_major_tone
        self.mid_played = False
        self._played_milestones: set[int] = set()
        super().__init__(iterable=iterable, desc=desc, total=total, **kwargs)

    def _update_volume(self) -> None:
        """Sync mute state to volumes."""
        is_muted = self.sound_manager._muted
        self.sound_manager.set_volume(self.volume, is_muted, self.background_volume)

    def _play_start_sequence(self) -> None:
        """Play the start tone and background loop."""
        self.sound_manager.play_sound("start")
        self.sound_manager.play_sound("background")
        self._played_milestones = {0}

    def _play_iteration_milestones(self, index: int) -> None:
        """
        On each iteration, play either semi_major or a random click,
        plus midpoint and 10% milestones.
        """
        self._update_volume()
        if self.all_ticks_semi_major_tone:
            self.sound_manager.play_sound("semi_major")
        else:
            self.sound_manager.play_random_click()
        if not self.total:
            return
        pct = int((index + 1) / self.total * 100)
        if not self.mid_played and pct >= 50:
            self.sound_manager.play_sound("mid")
            self.mid_played = True
            self._played_milestones.add(50)
        if self.ten_percent_ticks:
            tick = (pct // 10) * 10
            if tick not in self._played_milestones and pct >= tick:
                self.sound_manager.play_sound("semi_major")
                self._played_milestones.add(tick)

    def _play_end_sequence(self) -> None:
        """Play the end tone and stop background loop."""
        if self.play_end_sound:
            # bug
            if not self.sound_manager._muted:
                self.sound_manager.play_sound("end")

        time.sleep(self.end_wait)
        self.sound_manager._stop_background()

    def __iter__(self) -> Iterator:
        """
        Iterate with sound callbacks:
          - start tone
          - background drone
          - click per iteration or semi_major
          - mid-tone at 50%
          - optional ticks every 10%
          - end tone and stop drone
        """
        self._play_start_sequence()
        try:
            for i, item in enumerate(super().__iter__()):
                self._play_iteration_milestones(i)
                yield item
        finally:
            self._play_end_sequence()
