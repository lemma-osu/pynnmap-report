"""
Paragraph, table and document styles used in report creation
"""
from reportlab import platypus as p
from reportlab.lib import colors, pagesizes, units as u

from reportlab.pdfgen import canvas


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
