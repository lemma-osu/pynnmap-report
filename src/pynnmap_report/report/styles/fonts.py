from reportlab import rl_config
from reportlab.lib import fonts
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..config import FontConfig


def register_font(font_name, file_name):
    """
    Register a font with reportlab
    """
    pdfmetrics.registerFont(TTFont(font_name, file_name))
    return font_name


def register_custom_font(font_family, font_name, file_name, bold, italic):
    """
    Register a font from a file into the specified family using the
    specified font name.  Upon success, the registered font_name is returned
    """
    rl_config.warnOnMissingFontGlyphs = 0
    register_font(font_name, file_name)
    fonts.addMapping(font_family, bold, italic, font_name)
    return font_name


def load_fonts():
    return {
        "Garamond": {
            "regular": register_custom_font(
                "Garamond",
                "Garamond",
                FontConfig.GARAMOND["regular_fn"],
                False,
                False,
            ),
            "bold": register_custom_font(
                "Garamond",
                "Garamond-Bold",
                FontConfig.GARAMOND["bold_fn"],
                True,
                False,
            ),
            "italic": register_custom_font(
                "Garamond",
                "Garamond-Italic",
                FontConfig.GARAMOND["italic_fn"],
                False,
                True,
            ),
        },
        "Trebuchet": {
            "regular": register_font("Trebuchet", "trebuc.ttf"),
            "bold": register_font("Trebuchet-Bold", "trebucbd.ttf"),
            "italic": register_font("Trebuchet-Italic", "trebucit.ttf"),
            "bold_italic": register_font(
                "Trebuchet-Bold-Italic", "trebucbi.ttf"
            ),
        },
        "Open-Sans": {
            "regular": register_custom_font(
                "Open-Sans",
                "Open-Sans",
                FontConfig.OPEN_SANS["regular_fn"],
                False,
                False,
            ),
            "bold": register_custom_font(
                "Open-Sans",
                "Open-Sans-Bold",
                FontConfig.OPEN_SANS["bold_fn"],
                True,
                False,
            ),
            "italic": register_custom_font(
                "Open-Sans",
                "Open-Sans-Italic",
                FontConfig.OPEN_SANS["italic_fn"],
                False,
                True,
            ),
            "bold_italic": register_custom_font(
                "Open-Sans",
                "Open-Sans-Bold-Italic",
                FontConfig.OPEN_SANS["bold_italic_fn"],
                True,
                True,
            ),
        },
    }


FONTS = load_fonts()
