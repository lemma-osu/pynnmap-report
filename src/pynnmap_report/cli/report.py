"""
Report generation CLI program
"""
import click

from pynnmap.parser import parameter_parser_factory as ppf

from ..report import lemma_accuracy_report as lar


@click.command(short_help="Run accuracy assessment report on model output")
@click.argument("parameter-file", type=click.Path(exists=True), required=True)
def report(parameter_file):
    """
    Generate accuracy assessment report from parameter file
    """
    params = ppf.get_parameter_parser(parameter_file)
    if params.accuracy_assessment_report:
        aa_report = lar.LemmaAccuracyReport(params)
        aa_report.create_accuracy_report()
