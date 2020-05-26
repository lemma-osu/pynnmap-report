from reportlab import platypus as p
from reportlab import rl_config
from reportlab.lib import colors, enums, fonts, pagesizes, units as u

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas


def get_report_styles():

    # Output container for all derived styles
    report_styles = {}

    # Register additional font support
    rl_config.warnOnMissingFontGlyphs = 0
    pdfmetrics.registerFont(TTFont("Garamond", "C:/windows/fonts/gara.ttf"))
    pdfmetrics.registerFont(
        TTFont("Garamond-Bold", "C:/windows/fonts/garabd.ttf")
    )
    pdfmetrics.registerFont(
        TTFont("Garamond-Italic", "C:/windows/fonts/garait.ttf")
    )

    fonts.addMapping("Garamond", 0, 0, "Garamond")
    fonts.addMapping("Garamond", 0, 1, "Garamond-Italic")
    fonts.addMapping("Garamond", 1, 0, "Garamond-Bold")
    fonts.addMapping("Garamond", 1, 1, "Garamond-Italic")

    lead_multiplier = 1.20

    body_style = ParagraphStyle(
        name="Normal",
        fontName="Garamond",
        fontSize=11.5,
        leading=11.5 * lead_multiplier,
        alignment=enums.TA_LEFT,
    )
    report_styles["body_style"] = body_style

    body_style_right = ParagraphStyle(
        name="BodyRight", parent=body_style, alignment=enums.TA_RIGHT,
    )
    report_styles["body_style_right"] = body_style_right

    body_style_center = ParagraphStyle(
        name="BodyCenter", parent=body_style, alignment=enums.TA_CENTER,
    )
    report_styles["body_style_center"] = body_style_center

    body_style_10 = ParagraphStyle(
        name="BodySmall",
        parent=body_style,
        fontSize=10,
        leading=10 * lead_multiplier,
    )
    report_styles["body_style_10"] = body_style_10

    body_style_9 = ParagraphStyle(
        name="Body9",
        parent=body_style,
        fontSize=9,
        leading=9 * lead_multiplier,
    )
    report_styles["body_style_9"] = body_style_9

    body_style_10_right = ParagraphStyle(
        name="BodySmallRight", parent=body_style_10, alignment=enums.TA_RIGHT,
    )
    report_styles["body_style_10_right"] = body_style_10_right

    body_style_10_center = ParagraphStyle(
        name="BodySmallCenter", parent=body_style_10, alignment=enums.TA_CENTER,
    )
    report_styles["body_style_10_center"] = body_style_10_center

    indented = ParagraphStyle(
        name="Indented", parent=body_style, leftIndent=24,
    )
    report_styles["indented"] = indented

    contact_style = ParagraphStyle(
        name="Contact", parent=body_style, fontSize=10,
    )
    report_styles["contact_style"] = contact_style

    contact_style_right = ParagraphStyle(
        name="ContactRight", parent=contact_style, alignment=enums.TA_RIGHT,
    )
    report_styles["contact_style_right"] = contact_style_right

    contact_style_right_bold = ParagraphStyle(
        name="ContactRightBold",
        parent=contact_style_right,
        fontName="Garamond-Bold",
    )
    report_styles["contact_style_right_bold"] = contact_style_right_bold

    heading_style = ParagraphStyle(
        name="Heading",
        parent=body_style,
        fontName="Garamond-Bold",
        fontSize=16,
        leading=16 * lead_multiplier,
    )
    report_styles["heading_style"] = heading_style

    code_style = ParagraphStyle(
        name="Code", parent=body_style, fontSize=7, leading=7 * lead_multiplier,
    )
    report_styles["code_style"] = code_style

    code_style_right = ParagraphStyle(
        name="CodeRight", parent=code_style, alignment=enums.TA_RIGHT,
    )
    report_styles["code_style_right"] = code_style_right

    title_style = ParagraphStyle(
        name="Title",
        parent=body_style,
        fontName="Garamond-Bold",
        fontSize=18,
        leading=18 * lead_multiplier,
        leftIndent=1.7 * u.inch,
    )
    report_styles["title_style"] = title_style

    sub_title_style = ParagraphStyle(
        name="Subtitle",
        parent=title_style,
        fontName="Garamond",
        fontSize=14,
        leading=14 * lead_multiplier,
    )
    report_styles["sub_title_style"] = sub_title_style

    section_style = ParagraphStyle(
        name="Section",
        parent=title_style,
        alignment=enums.TA_CENTER,
        leftIndent=0.0,
    )
    report_styles["section_style"] = section_style

    default_table_style = p.TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 1, colors.white),
            ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]
    )
    report_styles["default_table_style"] = default_table_style

    return report_styles


def _do_nothing(_canvas, _doc):
    pass


def _set_background(canvas_, portrait_):
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
    canvas_.saveState()
    _set_background(canvas_, portrait_=True)
    canvas_.restoreState()


def landscape(canvas_, _doc):
    canvas_.saveState()
    _set_background(canvas_, portrait_=False)
    canvas_.restoreState()


class GnnDocTemplate(p.BaseDocTemplate):
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
