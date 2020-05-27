"""
Paragraph styles used in report creation
"""
from reportlab.lib import enums, units as u
from reportlab.lib.styles import ParagraphStyle

from .fonts import FONTS


def get_garamond_styles(font_dict):
    regular, bold = font_dict["regular"], font_dict["bold"]
    lead_multiplier = 1.20
    styles = dict()
    styles["body_style"] = ParagraphStyle(
        name="Normal",
        fontName=regular,
        fontSize=11.5,
        leading=11.5 * lead_multiplier,
        alignment=enums.TA_LEFT,
    )

    styles["body_style_right"] = ParagraphStyle(
        name="BodyRight", parent=styles["body_style"], alignment=enums.TA_RIGHT,
    )

    styles["body_style_center"] = ParagraphStyle(
        name="BodyCenter",
        parent=styles["body_style"],
        alignment=enums.TA_CENTER,
    )

    styles["body_style_10"] = ParagraphStyle(
        name="BodySmall",
        parent=styles["body_style"],
        fontSize=10,
        leading=10 * lead_multiplier,
    )

    styles["body_style_9"] = ParagraphStyle(
        name="Body9",
        parent=styles["body_style"],
        fontSize=9,
        leading=9 * lead_multiplier,
    )

    styles["body_style_10_right"] = ParagraphStyle(
        name="BodySmallRight",
        parent=styles["body_style_10"],
        alignment=enums.TA_RIGHT,
    )

    styles["body_style_10_center"] = ParagraphStyle(
        name="BodySmallCenter",
        parent=styles["body_style_10"],
        alignment=enums.TA_CENTER,
    )

    styles["indented"] = ParagraphStyle(
        name="Indented", parent=styles["body_style"], leftIndent=24,
    )

    styles["contact_style"] = ParagraphStyle(
        name="Contact", parent=styles["body_style"], fontSize=10,
    )

    styles["contact_style_right"] = ParagraphStyle(
        name="ContactRight",
        parent=styles["contact_style"],
        alignment=enums.TA_RIGHT,
    )

    styles["contact_style_right_bold"] = ParagraphStyle(
        name="ContactRightBold",
        parent=styles["contact_style_right"],
        fontName=bold,
    )

    styles["heading_style"] = ParagraphStyle(
        name="Heading",
        parent=styles["body_style"],
        fontName=bold,
        fontSize=16,
        leading=16 * lead_multiplier,
    )

    styles["code_style"] = ParagraphStyle(
        name="Code",
        parent=styles["body_style"],
        fontSize=7,
        leading=7 * lead_multiplier,
    )

    styles["code_style_right"] = ParagraphStyle(
        name="CodeRight", parent=styles["code_style"], alignment=enums.TA_RIGHT,
    )

    styles["title_style"] = ParagraphStyle(
        name="Title",
        parent=styles["body_style"],
        fontName=bold,
        fontSize=18,
        leading=18 * lead_multiplier,
        leftIndent=1.7 * u.inch,
    )

    styles["sub_title_style"] = ParagraphStyle(
        name="Subtitle",
        parent=styles["title_style"],
        fontName=regular,
        fontSize=14,
        leading=14 * lead_multiplier,
    )

    styles["section_style"] = ParagraphStyle(
        name="Section",
        parent=styles["title_style"],
        alignment=enums.TA_CENTER,
        leftIndent=0.0,
    )

    return styles


def get_open_sans_styles(font_dict):
    regular, bold = font_dict["regular"], font_dict["bold"]
    lead_multiplier = 1.40
    styles = dict()
    styles["body_style"] = ParagraphStyle(
        name="Normal",
        fontName=regular,
        fontSize=10.0,
        leading=10.0 * lead_multiplier,
        alignment=enums.TA_LEFT,
    )

    styles["body_style_right"] = ParagraphStyle(
        name="BodyRight", parent=styles["body_style"], alignment=enums.TA_RIGHT,
    )

    styles["body_style_center"] = ParagraphStyle(
        name="BodyCenter",
        parent=styles["body_style"],
        alignment=enums.TA_CENTER,
    )

    styles["body_style_10"] = ParagraphStyle(
        name="BodySmall",
        parent=styles["body_style"],
        fontSize=10,
        leading=10 * lead_multiplier,
    )

    styles["body_style_9"] = ParagraphStyle(
        name="Body9",
        parent=styles["body_style"],
        fontSize=9,
        leading=9 * lead_multiplier,
    )

    styles["body_style_10_right"] = ParagraphStyle(
        name="BodySmallRight",
        parent=styles["body_style_10"],
        alignment=enums.TA_RIGHT,
    )

    styles["body_style_10_center"] = ParagraphStyle(
        name="BodySmallCenter",
        parent=styles["body_style_10"],
        alignment=enums.TA_CENTER,
    )

    styles["indented"] = ParagraphStyle(
        name="Indented", parent=styles["body_style"], leftIndent=24,
    )

    styles["contact_style"] = ParagraphStyle(
        name="Contact", parent=styles["body_style"], fontSize=9,
    )

    styles["contact_style_right"] = ParagraphStyle(
        name="ContactRight",
        parent=styles["contact_style"],
        alignment=enums.TA_RIGHT,
    )

    styles["contact_style_right_bold"] = ParagraphStyle(
        name="ContactRightBold",
        parent=styles["contact_style_right"],
        fontName=bold,
    )

    styles["heading_style"] = ParagraphStyle(
        name="Heading",
        parent=styles["body_style"],
        fontName=bold,
        fontSize=14,
        leading=14 * lead_multiplier,
    )

    styles["code_style"] = ParagraphStyle(
        name="Code",
        parent=styles["body_style"],
        fontSize=7,
        leading=7 * lead_multiplier,
    )

    styles["code_style_right"] = ParagraphStyle(
        name="CodeRight", parent=styles["code_style"], alignment=enums.TA_RIGHT,
    )

    styles["title_style"] = ParagraphStyle(
        name="Title",
        parent=styles["body_style"],
        fontName=bold,
        fontSize=18,
        leading=18 * lead_multiplier,
        # leftIndent=1.7 * u.inch,
    )

    styles["sub_title_style"] = ParagraphStyle(
        name="Subtitle",
        parent=styles["title_style"],
        fontName=regular,
        fontSize=12,
        leading=12 * lead_multiplier,
    )

    styles["section_style"] = ParagraphStyle(
        name="Section",
        parent=styles["title_style"],
        alignment=enums.TA_CENTER,
        leftIndent=0.0,
    )

    styles["body_16"] = ParagraphStyle(
        "body_16",
        parent=styles["body_style"],
        fontName=bold,
        fontSize=16,
        leading=16,
    )

    styles["body_9"] = ParagraphStyle(
        "body_9", parent=styles["body_style"], fontSize=9, leading=9,
    )

    styles["body_11"] = ParagraphStyle(
        "body_11", parent=styles["body_style"], fontSize=11, leading=11,
    )

    styles["subheading"] = ParagraphStyle(
        "subheading",
        parent=styles["body_style"],
        fontSize=10,
        alignment=enums.TA_CENTER,
    )

    styles["error_matrix"] = ParagraphStyle(
        "error_matrix",
        parent=styles["body_style"],
        fontSize=7,
        leading=7,
        alignment=enums.TA_RIGHT,
    )

    styles["error_matrix_center"] = ParagraphStyle(
        "error_matrix_center",
        parent=styles["error_matrix"],
        alignment=enums.TA_CENTER,
    )

    styles["error_matrix_rot"] = ParagraphStyle(
        "error_matrix_rot",
        parent=styles["error_matrix"],
        alignment=enums.TA_LEFT,
    )

    return styles


def get_paragraph_styles(font_family):
    """
    Build custom paragraph and table styles and return to caller
    """
    family = FONTS[font_family]
    style_dict = {
        "Garamond": get_garamond_styles,
        "Open-Sans": get_open_sans_styles,
    }
    return (style_dict[font_family])(family)
