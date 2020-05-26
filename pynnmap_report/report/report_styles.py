"""
Paragraph, table and document styles used in report creation
"""
from reportlab import platypus as p
from reportlab import rl_config
from reportlab.lib import colors, enums, fonts, pagesizes, units as u

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas

from .config import FontConfig


def register_custom_font(font_family, font_name, file_name, bold, italic):
    """
    Register a font from a file into the specified family using the
    specified font name.  Upon success, the registered font_name is returned
    """
    rl_config.warnOnMissingFontGlyphs = 0
    pdfmetrics.registerFont(TTFont(font_name, file_name))
    fonts.addMapping(font_family, bold, italic, font_name)
    return font_name


def get_report_styles():
    """
    Build custom paragraph and table styles and return to caller
    """
    try:
        normal_font = register_custom_font(
            "Garamond",
            "Garamond",
            FontConfig.GARAMOND["regular_fn"],
            False,
            False,
        )
        bold_font = register_custom_font(
            "Garamond",
            "Garamond-Bold",
            FontConfig.GARAMOND["bold_fn"],
            True,
            False,
        )
    except (FileNotFoundError, TTFError):
        normal_font = "Helvetica"
        bold_font = "Helvetica-Bold"

    lead_multiplier = 1.20
    styles = dict()
    styles["body_style"] = ParagraphStyle(
        name="Normal",
        fontName=normal_font,
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
        fontName=bold_font,
    )

    styles["heading_style"] = ParagraphStyle(
        name="Heading",
        parent=styles["body_style"],
        fontName=bold_font,
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
        fontName=bold_font,
        fontSize=18,
        leading=18 * lead_multiplier,
        leftIndent=1.7 * u.inch,
    )

    styles["sub_title_style"] = ParagraphStyle(
        name="Subtitle",
        parent=styles["title_style"],
        fontName=normal_font,
        fontSize=14,
        leading=14 * lead_multiplier,
    )

    styles["section_style"] = ParagraphStyle(
        name="Section",
        parent=styles["title_style"],
        alignment=enums.TA_CENTER,
        leftIndent=0.0,
    )

    styles["default_table_style"] = p.TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]
    )
    return styles


def _do_nothing(_canvas, _doc):
    """
    No-op on page transition
    """


def _set_background(canvas_, portrait_):
    """
    Set the background based on the orientation of the page
    """
    canvas_.setStrokeColor(colors.black)
    canvas_.setLineWidth(1)
    canvas_.setFillColor("#e6ded5")
    width = 7.5 * u.inch if portrait_ else 10.0 * u.inch
    height = 10.0 * u.inch if portrait_ else 7.5 * u.inch
    canvas_.roundRect(
        0.5 * u.inch,
        0.5 * u.inch,
        width,
        height,
        0.15 * u.inch,
        stroke=1,
        fill=1,
    )


def title(canvas_, _doc):
    """
    Create the title page which has the LEMMA logo on it
    """
    canvas_.saveState()
    _set_background(canvas_, portrait_=True)
    lemma_img = (
        "L:/resources/code/models/accuracy_assessment/report/images/"
        "lemma_logo.gif"
    )
    canvas_.drawImage(
        lemma_img,
        0.5 * u.inch,
        7.5 * u.inch,
        width=7.5 * u.inch,
        height=3 * u.inch,
        mask="auto",
    )
    canvas_.restoreState()


def portrait(canvas_, _doc):
    """
    Create a portrait page with custom background
    """
    canvas_.saveState()
    _set_background(canvas_, portrait_=True)
    canvas_.restoreState()


def landscape(canvas_, _doc):
    """
    Create a landscape page with custom background
    """
    canvas_.saveState()
    _set_background(canvas_, portrait_=False)
    canvas_.restoreState()


class GnnDocTemplate(p.BaseDocTemplate):
    """
    Base template for GNN report including custom pages for portrait and
    landscape orientations and title page
    """

    def __init__(self, fn, **kwargs):
        super().__init__(fn, **kwargs)
        self.pagesize = [8.5 * u.inch, 11.0 * u.inch]

        self.on_title = kwargs.get("on_title", _do_nothing)
        self.on_portrait = kwargs.get("on_portrait", _do_nothing)
        self.on_landscape = kwargs.get("on_landscape", _do_nothing)

    def build(
        self, flowables, filename, canvasmaker=canvas.Canvas,
    ):

        # Recalculate in case we changed margins, sizes, etc
        self._calc()

        frame_portrait = p.Frame(
            0.75 * u.inch,
            0.60 * u.inch,
            7.00 * u.inch,
            9.80 * u.inch,
            id="portrait_frame",
        )

        frame_landscape = p.Frame(
            0.75 * u.inch,
            0.50 * u.inch,
            9.50 * u.inch,
            7.40 * u.inch,
            id="landscape_frame",
        )

        self.addPageTemplates(
            [
                p.PageTemplate(
                    id="title",
                    frames=frame_portrait,
                    onPage=self.on_title,
                    pagesize=pagesizes.portrait(pagesizes.letter),
                ),
                p.PageTemplate(
                    id="portrait",
                    frames=frame_portrait,
                    onPage=self.on_portrait,
                    pagesize=pagesizes.portrait(pagesizes.letter),
                ),
                p.PageTemplate(
                    id="landscape",
                    frames=frame_landscape,
                    onPage=self.on_landscape,
                    pagesize=pagesizes.landscape(pagesizes.letter),
                ),
            ]
        )

        super().build(flowables, filename=filename, canvasmaker=canvasmaker)
