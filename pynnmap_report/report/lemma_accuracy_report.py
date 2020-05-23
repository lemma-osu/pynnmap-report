from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame

from pynnmap_report.report.attribute_accuracy_formatter import (
    AttributeAccuracyFormatter,
)


class LemmaAccuracyReport:
    def __init__(self, parameter_parser):
        self.parameter_parser = parameter_parser
        self.story = []

    def create_accuracy_report(self):
        parser = self.parameter_parser

        # Set up the document template
        doc = BaseDocTemplate(
            parser.accuracy_assessment_report, pagesize=letter
        )

        # Add the page template
        doc.addPageTemplates(
            [
                PageTemplate(
                    frames=[
                        Frame(
                            0.5 * inch,
                            0.4 * inch,
                            7.5 * inch,
                            10.2 * inch,
                            leftPadding=0,
                            bottomPadding=0,
                            rightPadding=0,
                            topPadding=0,
                            id=None,
                        ),
                    ]
                ),
            ]
        )

        # Make a list of formatters which are separate subsections of the
        # report
        formatters = [
            AttributeAccuracyFormatter(self.parameter_parser),
        ]
        for formatter in formatters:
            sub_story = formatter.run_formatter()
            if sub_story is not None:
                self.story.extend(sub_story[:])
                del sub_story

        # Write out the story
        doc.build(self.story)

        # Clean up if necessary for each formatter
        for formatter in formatters:
            formatter.clean_up()
