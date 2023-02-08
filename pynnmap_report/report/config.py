"""
Specialized configuration parameters
"""
import os

GNN_RELEASE_VERSION = "2023.1"


class FontConfig:  # pylint: disable=too-few-public-methods
    """
    Path parameters for fonts
    """

    FONT_PATH = "C:/windows/fonts"
    GARAMOND = {
        "regular_fn": os.path.join(FONT_PATH, "gara.ttf"),
        "bold_fn": os.path.join(FONT_PATH, "garabd.ttf"),
        "italic_fn": os.path.join(FONT_PATH, "garait.ttf"),
    }

    FONT_PATH = "C:/Users/gregorma/AppData/Roaming/Monotype/skyfonts-google"
    OPEN_SANS = {
        "regular_fn": os.path.join(FONT_PATH, "open sans regular.ttf"),
        "bold_fn": os.path.join(FONT_PATH, "open sans 600.ttf"),
        "italic_fn": os.path.join(FONT_PATH, "open sans italic.ttf"),
        "bold_italic_fn": os.path.join(FONT_PATH, "open sans 600italic.ttf"),
    }
