# audio/audio_manager.py
import pygame
import os

class AudioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._music_vol  = 0.5
            cls._instance._sfx_vol    = 0.7
            cls._instance._sounds     = {}
            cls._instance._cur_music  = None
            cls._instance.base = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets", "sounds")
        return cls._instance

    def play_music(self, filename: str, loops=-1, fade_ms=800):
        path = os.path.join(self.base, filename)
        if not os.path.exists(path):
            return
        if self._cur_music == filename:
            return
        self._cur_music = filename
        try:
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._music_vol)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
        except Exception:
            pass

    def stop_music(self, fade_ms=400):
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception:
            pass
        self._cur_music = None

    def play_sfx(self, filename: str, volume: float | None = None):
        if filename not in self._sounds:
            path = os.path.join(self.base, filename)
            if os.path.exists(path):
                try:
                    self._sounds[filename] = pygame.mixer.Sound(path)
                except Exception:
                    self._sounds[filename] = None
            else:
                self._sounds[filename] = None
        snd = self._sounds.get(filename)
        if snd:
            snd.set_volume(volume if volume is not None else self._sfx_vol)
            snd.play()

    def set_music_vol(self, v: float):
        self._music_vol = max(0.0, min(1.0, v))
        try:
            pygame.mixer.music.set_volume(self._music_vol)
        except Exception:
            pass

    def set_sfx_vol(self, v: float):
        self._sfx_vol = max(0.0, min(1.0, v))

audio = AudioManager()
