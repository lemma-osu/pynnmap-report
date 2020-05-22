from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame

from pynnmap_report.report import accuracy_report
from pynnmap_report.report import attribute_accuracy_formatter as aa_formatter


class LemmaAccuracyReport(accuracy_report.AccuracyReport):
    def __init__(self, parameter_parser):
        super(LemmaAccuracyReport, self).__init__(parameter_parser)

    def create_accuracy_report(self):
        p = self.parameter_parser

        # Set up the document template
        doc = BaseDocTemplate(p.accuracy_assessment_report, pagesize=letter)

        # Add the page template
        doc.addPageTemplates(
            [
                PageTemplate(
                    frames=[
                        Frame(
                            0.5 * inch,
                            0.5 * inch,
                            7.5 * inch,
                            10.0 * inch,
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
        formatters = []

        f = aa_formatter.AttributeAccuracyFormatter(self.parameter_parser)
        formatters.append(f)

        # Run each instance's formatter
        for f in formatters:
            sub_story = f.run_formatter()
            if sub_story is not None:
                self.story.extend(sub_story[:])
                del sub_story

        # Write out the story
        doc.build(self.story)

        # Clean up if necessary for each formatter
        for f in formatters:
            f.clean_up()
