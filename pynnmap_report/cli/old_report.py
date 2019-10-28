import click

from pynnmap.parser import parameter_parser_factory as ppf
from pynnmap_report.report import old_lemma_accuracy_report as lar


@click.command(short_help='Run accuracy assessment report on model output')
@click.argument(
    'parameter-file',
    type=click.Path(exists=True),
    required=True)
def old_report(parameter_file):
    p = ppf.get_parameter_parser(parameter_file)

    # Create the AA report if desired
    if p.accuracy_assessment_report:
        aa_report = lar.LemmaAccuracyReport(p)
        aa_report.create_accuracy_report()
