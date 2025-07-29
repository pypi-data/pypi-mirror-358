import click

from damply import __version__
from damply.cli.audit import audit, collect_audits, full_audit
from damply.cli.groups_table import groups_table
from damply.cli.project import project
from damply.cli.whose import whose
from damply.plot import plot


@click.group(
	context_settings={'help_option_names': ['-h', '--help']}, no_args_is_help=True
)
@click.version_option(__version__, prog_name='damply')
def cli() -> None:
	"""
	A tool to interact with systems implementing the
	Data Management Plan (DMP) standard.

	This tool is meant to allow sys-admins to easily query and audit the metadata of their
	projects.

	To enable logging, set the env variable `DAMPLY_LOG_LEVEL`.
	"""
	pass


cli.add_command(groups_table)
cli.add_command(whose)
cli.add_command(project)
cli.add_command(audit)
cli.add_command(full_audit)
cli.add_command(collect_audits)
cli.add_command(plot)
