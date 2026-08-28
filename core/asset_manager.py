# core/asset_manager.py

import pygame
import os


class AssetManager:
    """Loads and caches images/sounds once.
    Returns procedural fallbacks if missing.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._instance._images = {}
            cls._instance._sounds = {}
            cls._instance._fonts = {}

            cls._instance.base = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

        return cls._instance

    # ------------------------------------------------------------------
    # IMAGES
    # ------------------------------------------------------------------

    def get_image(self, rel_path: str, size=None) -> pygame.Surface:

        key = (rel_path, size)

        if key not in self._images:

            # IMPORTANT:
            # Your project folder is named "assests"
            full = os.path.join(
                self.base,
                "assests",
                rel_path
            )

            print("Trying to load image:")
            print(full)

            if os.path.exists(full):

                try:
                    img = pygame.image.load(full)

                    if pygame.display.get_surface():
                        img = img.convert_alpha()

                    print("IMAGE LOADED:", full)

                except Exception as e:

                    print("IMAGE ERROR:", e)

                    img = self._make_placeholder(
                        size or (32, 32)
                    )

            else:

                print("IMAGE NOT FOUND:", full)

                img = self._make_placeholder(
                    size or (32, 32)
                )

            if size:
                img = pygame.transform.smoothscale(
                    img,
                    size
                )

            self._images[key] = img

        return self._images[key]

    # ------------------------------------------------------------------
    # PLACEHOLDER
    # ------------------------------------------------------------------

    def _make_placeholder(self, size) -> pygame.Surface:

        surf = pygame.Surface(
            size,
            pygame.SRCALPHA
        )

        surf.fill(
            (200, 0, 200, 180)
        )

        return surf

    # ------------------------------------------------------------------
    # SOUNDS
    # ------------------------------------------------------------------

    def get_sound(self, rel_path: str) -> pygame.mixer.Sound | None:

        if rel_path in self._sounds:
            return self._sounds[rel_path]

        full = os.path.join(
            self.base,
            "assests",
            "sounds",
            rel_path
        )

        if os.path.exists(full):

            try:
                snd = pygame.mixer.Sound(full)
                self._sounds[rel_path] = snd
                return snd

            except Exception:
                pass

        self._sounds[rel_path] = None
        return None

    # ------------------------------------------------------------------
    # FONTS
    # ------------------------------------------------------------------

    def get_font(
        self,
        name: str | None,
        size: int
    ) -> pygame.font.Font:

        key = (name, size)

        if key not in self._fonts:

            paths_to_try = []

            if name:
                paths_to_try.append(
                    os.path.join(
                        self.base,
                        "assests",
                        "fonts",
                        name
                    )
                )

            try:

                self._fonts[key] = pygame.font.Font(
                    paths_to_try[0]
                    if paths_to_try
                    and os.path.exists(paths_to_try[0])
                    else None,
                    size
                )

            except Exception:

                self._fonts[key] = pygame.font.SysFont(
                    "arial",
                    size
                )

        return self._fonts[key]


assets = AssetManager()