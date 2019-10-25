from pynnmap_report.report import report_formatter


class RiemannAccuracyFormatter(report_formatter.ReportFormatter):

    def __init__(self, parameters):
        super(RiemannAccuracyFormatter, self).__init__()
        pass

    def run_formatter(self):
        print('Formatting Riemann accuracy')

    def clean_up(self):
        pass
