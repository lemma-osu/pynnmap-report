"""
LEMMA GNN accuracy report with one page per attribute
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.pdfgen.canvas import Canvas

from .config import GNN_RELEASE_VERSION
from .styles.fonts import FONTS
from .introduction_formatter import IntroductionFormatter
from .attribute_accuracy_formatter import AttributeAccuracyFormatter
from .categorical_accuracy_formatter import CategoricalAccuracyFormatter
from .species_accuracy_formatter import SpeciesAccuracyFormatter
from .data_dictionary_formatter import DataDictionaryFormatter
from .references_formatter import ReferencesFormatter


class PageNumCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        page = f"Page {self._pageNumber} of {page_count}"
        self.setFont(FONTS["Open-Sans"]["regular"], 9)
        release = f"LEMMA GNN Release {GNN_RELEASE_VERSION}"
        self.drawString(0.5 * inch, 0.25 * inch, release)
        self.drawRightString(8.0 * inch, 0.25 * inch, page)


class LemmaAccuracyReport:
    """
    LEMMA GNN accuracy report with one page per attribute
    """

    def __init__(self, parameter_parser):
        self.parameter_parser = parameter_parser
        self.story = []

    def create_accuracy_report(self):
        """
        Run the report and save to PDF file
        """
        parser = self.parameter_parser

        # Set up the document template
        doc = BaseDocTemplate(
            parser.accuracy_assessment_report, pagesize=letter
        )

        # Add the page template
        doc.addPageTemplates(
            [
                PageTemplate(
                    id="portrait",
                    frames=[
                        Frame(
                            0.5 * inch,
                            0.5 * inch,
                            7.5 * inch,
                            10.2 * inch,
                            leftPadding=0,
                            bottomPadding=0,
                            rightPadding=0,
                            topPadding=0,
                            id=None,
                        ),
                    ],
                ),
            ]
        )

        # Make a list of formatters which are separate subsections of the
        # report
        formatters = [
            IntroductionFormatter(self.parameter_parser),
            AttributeAccuracyFormatter(self.parameter_parser),
            CategoricalAccuracyFormatter(self.parameter_parser),
            SpeciesAccuracyFormatter(self.parameter_parser),
            DataDictionaryFormatter(self.parameter_parser),
            ReferencesFormatter(),
        ]
        for formatter in formatters:
            sub_story = formatter.run_formatter()
            if sub_story is not None:
                self.story.extend(sub_story[:])
                del sub_story

        # Write out the story
        doc.build(self.story, canvasmaker=PageNumCanvas)

        # Clean up if necessary for each formatter
        for formatter in formatters:
            formatter.clean_up()
