import os
import re

from reportlab import platypus as p
from reportlab.lib import colors
from reportlab.lib import units as u

# Import the report styles
from pynnmap_report.report import report_styles
styles = report_styles.get_report_styles()


class ReportFormatter(object):
    # Set up an enumeration for the different pages
    (TITLE, PORTRAIT, LANDSCAPE) = ('title', 'portrait', 'landscape')

    def __init__(self):
        pass

    @staticmethod
    def _make_page_break(story, orientation):
        story.append(p.NextPageTemplate(orientation))
        story.append(p.PageBreak())
        return story

    @staticmethod
    def _make_title(title_str):
        para = p.Paragraph(title_str, styles['section_style'])
        t = p.Table([[para]], colWidths=[7.5 * u.inch])
        t.setStyle(
            p.TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (-1, -1), '#957348'),
                ('ALIGNMENT', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ]))
        return t

    @staticmethod
    def _make_figure_table(image_files):
        # Add the images to a list of lists
        cols = 2
        table = []
        row = []
        for (i, fn) in enumerate(image_files):
            row.append(p.Image(fn, 3.4 * u.inch, 3.0 * u.inch))
            if (i % cols) == (cols - 1):
                table.append(row)
                row = []

        # Determine if there are any images left to print
        if len(row) != 0:
            for i in range(len(row), cols):
                row.append(p.Paragraph('', styles['body_style']))
            table.append(row)

        # Style this into a reportlab table and add to the story
        width = 3.75 * u.inch
        t = p.Table(table, colWidths=[width, width])
        t.setStyle(
            p.TableStyle([
                ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 6.0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6.0),
            ]))
        return t

    @staticmethod
    def txt_to_html(in_str):
        replace_list = {
            '>': '&gt;',
            '<': '&lt;',
        }
        for i in replace_list:
            in_str = re.sub(i, replace_list[i], in_str)
        return in_str

    def run_formatter(self):
        raise NotImplementedError

    def clean_up(self):
        raise NotImplementedError
