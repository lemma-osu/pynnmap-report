import os

import pandas as pd
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import black, yellow

from pynnmap.parser import xml_stand_metadata_parser as xsmp

from pynnmap_report.report import report_formatter
from pynnmap_report.report import chart_func as cf
from pynnmap_report.report import utilities


def get_stylesheet():
    # Add some fonts
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont('Trebuchet', 'trebuc.ttf'))
    pdfmetrics.registerFont(TTFont('TrebuchetBold', 'trebucbd.ttf'))
    pdfmetrics.registerFont(TTFont('TrebuchetItalic', 'trebucit.ttf'))
    pdfmetrics.registerFont(TTFont('TrebuchetBoldItalic', 'trebucbi.ttf'))

    styles = {
        'default': ParagraphStyle(
            'default',
            fontName='Trebuchet',
            fontSize=12,
            leading=12,
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=0,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            bulletFontName='Trebuchet',
            bulletFontSize=10,
            bulletIndent=0,
            textColor=black,
            backColor=None,
            wordWrap=None,
            borderWidth=0,
            borderPadding=0,
            borderColor=None,
            borderRadius=None,
            allowWidows=1,
            allowOrphans=0,
            textTransform=None,
            endDots=None,
            splitLongWords=1,
        ),
    }

    styles['title'] = ParagraphStyle(
        'title',
        parent=styles['default'],
        fontName='TrebuchetBold',
        fontSize=14,
    )

    styles['alert'] = ParagraphStyle(
        'alert',
        parent=styles['default'],
        textColor=yellow
    )
    return styles


class AttributeAccuracyFormatter(report_formatter.ReportFormatter):
    def __init__(self, parameter_parser):
        super(AttributeAccuracyFormatter, self).__init__()
        pp = parameter_parser
        self.stand_metadata_file = pp.stand_metadata_file
        self.observed_file = pp.stand_attribute_file
        self.predicted_file = pp.independent_predicted_file
        self.id_field = pp.plot_id_field
        self.stylesheet = get_stylesheet()
        self.riemann_dir = pp.riemann_output_folder
        self.k = pp.k
        self.image_files = []

    def _get_riemann_fn(self, resolution, observed=True):
        if observed:
            return '{root}/hex_{res}/hex_{res}_observed_mean.csv'.format(
                root=self.riemann_dir,
                res=resolution
            )
        else:
            return '{root}/hex_{res}/hex_{res}_predicted_k{k}_mean.csv'.format(
                root=self.riemann_dir,
                res=resolution,
                k=self.k
            )

    def run_formatter(self):
        # Read in the stand attribute metadata
        mp = xsmp.XMLStandMetadataParser(self.stand_metadata_file)
        attrs = utilities.get_continuous_attrs(mp)
        flowables = []
        for attr in attrs:
            page = self.build_flowable_page(attr)
            flowables.extend(page)
        return flowables

    def clean_up(self):
        for fn in self.image_files:
            if os.path.exists(fn):
                os.remove(fn)

    def build_flowable_page(self, attr):
        scatter_fn = self.build_scatterplot_from_data(attr, kde=True)
        riemann_10_fn = self.build_riemann_scatterplot_from_data(attr, 10)
        riemann_30_fn = self.build_riemann_scatterplot_from_data(attr, 30)
        riemann_50_fn = self.build_riemann_scatterplot_from_data(attr, 50)

        # Push these filenames to the image_files list so that they
        # are deleted when report has been written
        self.image_files.extend((
            scatter_fn, riemann_10_fn, riemann_30_fn, riemann_50_fn
        ))

        title = attr.field_name + ' (' + attr.units + ')'
        table_style = [
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (-1, -1), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]
        default_style = self.stylesheet['default']
        title_style = self.stylesheet['title']

        return [
            Paragraph(title, title_style),
            Spacer(1, 0.1 * inch),
            Paragraph(attr.short_description, default_style),
            Spacer(1, 0.2 * inch),
            Paragraph('Local Accuracy', default_style),
            Spacer(1, 0.17 * inch),
            Table([[
                Image(scatter_fn, width=3.2 * inch, height=3.2 * inch),
                Image(scatter_fn, width=3.2 * inch, height=3.2 * inch),
            ]], style=table_style, hAlign='LEFT'),
            Spacer(1, 0.10 * inch),
            Paragraph('Regional Accuracy', default_style),
            Spacer(1, 0.17 * inch),
            Image('./histo.png', width=7.5 * inch, height=2.5 * inch),
            Spacer(1, 0.10 * inch),
            Paragraph('Accuracy Across Scales', default_style),
            Spacer(1, 0.17 * inch),
            Table([[
                Image(riemann_10_fn, width=2.4 * inch, height=2.4 * inch),
                Image(riemann_30_fn, width=2.4 * inch, height=2.4 * inch),
                Image(riemann_50_fn, width=2.4 * inch, height=2.4 * inch),
            ]], style=table_style, hAlign='LEFT'),
            PageBreak()
        ]

    def build_scatterplot_from_data(self, attr, kde=False):
        a = attr.field_name
        output_fn = '{}.png'.format(a.lower())
        obs_df = pd.read_csv(self.observed_file, usecols=(self.id_field, a))
        prd_df = pd.read_csv(self.predicted_file, usecols=(self.id_field, a))
        merged_df = utilities.build_paired_dataframe(obs_df, prd_df, self.id_field, a)
        cf.draw_scatterplot(merged_df, attr, output_file=output_fn, kde=kde)
        return output_fn

    def build_riemann_scatterplot_from_data(self, attr, resolution, kde=False):
        a = attr.field_name
        id_field = 'HEX_{}_ID'.format(resolution)
        output_fn = 'hex_{}_{}.png'.format(resolution, a.lower())
        observed_file = self._get_riemann_fn(resolution, observed=True)
        predicted_file = self._get_riemann_fn(resolution, observed=False)
        obs_df = pd.read_csv(observed_file, usecols=(id_field, a))
        prd_df = pd.read_csv(predicted_file, usecols=(id_field, a))
        merged_df = utilities.build_paired_dataframe(obs_df, prd_df, id_field, a)
        cf.draw_scatterplot(merged_df, attr, output_file=output_fn, kde=kde)
        return output_fn
