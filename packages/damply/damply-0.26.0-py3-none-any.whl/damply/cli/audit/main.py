import datetime
import json
import sys
import traceback
from pathlib import Path

import click

from damply import __version__ as damply_version
from damply.logging_config import logger
from damply.project import DirectoryAudit

from .utils import (
	InvalidProjectGroupError,
	OutsideProjectPathError,
	get_parents_path,
	get_project_group,
)


@click.option(
	'--force-compute-details',
	'-f',
	'compute_details',
	help='Force the computation of details for the directory and subdirectories regardless of cache.',
	is_flag=True,
	default=False,
	show_default=True,
)
@click.argument(
	'directory', type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.command('audit')
def audit(directory: Path, compute_details: bool) -> None:
	"""Audit all subdirectories and aggregate damply output into a single JSON.

	Unlike the 'damply proejct' command, this will by default, try to compute
	details, using cache if it exists. If you want to force the computation
	of details for the directory and subdirectories, use the --force-compute-details
	flag. This will ignore any cached results and recompute everything.

	"""

	# resolve the directory to scan
	directory = directory.expanduser().resolve().absolute()

	logger.info(f'Starting audit for directory: {directory}')

	now = datetime.datetime.now()
	timestamp = now.strftime('%Y-%m-%dT%H-%M-%S')
	date = now.strftime('%Y-%m-%d')

	try:
		project_group = get_project_group(directory)
		relative_path = get_parents_path(project_group, directory)
	except (InvalidProjectGroupError, OutsideProjectPathError) as e:
		click.echo(f'Error: {e}', err=True)
		sys.exit(1)

	results_dir = Path(
		f'/cluster/projects/{project_group}/admin/audit/results/{date}/{relative_path}'
	)
	results_dir / 'audit.json'

	logger.debug(
		f'Creating results directory: {results_dir} '
		f'for project group: {project_group}, relative path: {relative_path}'
	)
	results_dir.mkdir(parents=True, exist_ok=True)
	output_file = results_dir / 'audit.json'

	# Initialize combined results
	results = {
		'audit_date': timestamp,
		'source_directory': {},
		'directories': {},
		'damply_version': damply_version,
	}

	def safe_audit(path: Path) -> dict:
		try:
			logger.info(f'Auditing: {path}')
			audit_obj = DirectoryAudit.from_path(path)
			audit_obj.compute_details(show_progress=True, force=compute_details)
			return {
				'status': 'ok',
				'data': audit_obj.to_dict(),
			}
		except Exception as e:
			etype = type(e).__name__
			emsg = str(e)
			stack = traceback.format_exc(limit=5)  # limit frames if needed
			logger.exception(f'Failed audit: {path}')

			return {
				'status': 'error',
				'error': f'{etype}: {emsg}',
				'traceback': stack,
			}

	# Audit subdirectories
	for subdir in sorted(directory.iterdir()):
		if subdir.is_dir():
			results['directories'][subdir.name] = safe_audit(subdir)

	# count number of errors
	logger.info(f'Total directories audited: {len(results["directories"])}')
	error_count = sum(
		1 for result in results['directories'].values() if result['status'] == 'error'
	)
	if error_count > 0:
		logger.error(f'Total errors encountered: {error_count}')

	# Audit the main source directory
	results['source_directory'] = safe_audit(directory)

	# Save combined results
	output_file.write_text(json.dumps(results, default=str, indent=2))
	logger.info(f'Audit results saved to: {output_file}')


@click.command('full-audit')
@click.argument('project_group')
@click.option(
	'--force-compute-details',
	'-f',
	'compute_details',
	help='Force the computation of details for the directory and subdirectories regardless of cache.',
	is_flag=True,
	default=False,
	show_default=True,
)
@click.option(
	'--sbatch-time',
	'-t',
	'job_time',
	help='Time limit for each sbatch job (default: 01:00:00)',
	default='01:00:00',
	show_default=True,
)
def full_audit(project_group: str, compute_details: bool, job_time: str) -> None:
	"""Run a full audit for the specified project group.

	This will essentially, submit a bunch of sbatch jobs to the cluster
	for all the directories in the project group.
	"""
	run_full_audit(project_group, compute_details=compute_details, job_time=job_time)


# Setup some assumptions about project groups and directories

VALID_PROJECT_GROUPS = {'bhklab', 'radiomics'}


def run_full_audit(
	project_group: str, compute_details: bool = False, job_time: str = '01:00:00'
) -> None:
	"""Run a full audit for the specified project group.

	NOTE: THIS IS MEANT TO BE USED ON A COMPUTE NODE! NOT THE LOGIN NODE!

	This will essentially, submit a bunch of sbatch jobs to the cluster
	for all the directories in the project group.
	"""

	if project_group not in VALID_PROJECT_GROUPS:
		msg = f'Invalid project group: {project_group}. Valid groups are: {", ".join(VALID_PROJECT_GROUPS)}'
		raise InvalidProjectGroupError(msg)

	# Define the base directory for the project group
	root = Path(f'/cluster/projects/{project_group}')

	# do we have access to the base directory?
	if not root.exists() or not root.is_dir():
		msg = f'Base directory {root} does not exist or is not a directory.'
		msg += ' Are you sure you are running this on a compute node?'
		raise OutsideProjectPathError(msg)

	logger.info(f'Starting full audit for project group: {project_group}')
	# Get all directories in the project group
	directories = get_directories(root)
	logger.debug(
		f'Found {len(directories)} directories in project group {project_group}'
	)

	# get relative path for the log directory
	try:
		get_parents_path(project_group, root)
	except (InvalidProjectGroupError, OutsideProjectPathError) as e:
		click.echo(f'Error: {e}', err=True)
		sys.exit(1)

	now = datetime.datetime.now()
	date = now.strftime('%Y-%m-%d')
	log_dir_base = (
		Path(f'/cluster/projects/{project_group}/admin/audit/logs') / f'{date}'
	)

	compute_details_arg = '--force-compute-details' if compute_details else ''

	import subprocess

	for directory in directories:
		rel_path = get_parents_path(project_group, directory)
		job_name = rel_path.replace('/', '_').replace(' ', '_')
		log_dir = log_dir_base / rel_path
		log_dir.mkdir(parents=True, exist_ok=True)
		cmd = [
			'sbatch',
			'--job-name',
			job_name,
			'--output',
			str(log_dir / f'{job_name}_%j.out'),
			'--time',
			job_time,
			'--mem',
			'4G',
			'--wrap',
			f'DAMPLY_LOG_LEVEL=DEBUG damply audit {directory} {compute_details_arg}',
		]
		logger.debug(f'Submitting job with command: {cmd}')

		try:
			result = subprocess.run(cmd, check=True, capture_output=True, text=True)
			logger.info(f'Job submitted successfully: {result.stdout.strip()}')
		except subprocess.CalledProcessError as e:
			logger.error(f'Failed to submit job for {directory}: {e.stderr.strip()}')
			continue


def get_directories(root: Path) -> list[Path]:
	from itertools import product

	############################################################################
	# bhklab is simple:
	############################################################################
	if root.name == 'bhklab':
		# get the first level of directories in the root
		dirs = [d for d in root.glob('*/*') if d.is_dir()]
		# sort the directories by name
		dirs.sort(key=lambda x: str(x))
		logger.info(f'Found {len(dirs)} directories in {root}')
		return dirs

	############################################################################
	# radiomics is more complex:
	############################################################################
	# get the first level of directories in the root
	parents = ['InternalDatasets', 'PublicDatasets']

	one_level_dirs = [d for d in root.iterdir() if d.is_dir() and d.name not in parents]

	# we will do more complex matching for internal and public datasets
	mids = ['srcdata', 'procdata']
	disease_sites = [
		'Abdomen',
		'Brain',
		'Breast',
		'HeadNeck',
		'Lung',
		'MultiSite',
		'Pelvis',
		'PhantomData',
	]
	matches = [
		root / parent / mid / ds
		for parent, mid, ds in product(parents, mids, disease_sites)
		if (root / parent / mid / ds).is_dir()
		and not (root / parent / mid / ds).is_symlink()
	]

	# now get one level directories that are not symlinks
	# matches = [d for d in one_level_dirs.iterdir() if not d.is_symlink()]
	for subdir in [*one_level_dirs, *matches]:
		if subdir.is_symlink():
			logger.warning(f'Skipping symlinked directory: {subdir}')
			continue
		try:
			matches += [
				d for d in subdir.iterdir() if d.is_dir() and not d.is_symlink()
			]
		except PermissionError:
			logger.warning(f'Permission denied for directory: {subdir}. Skipping.')
			continue

	# sort the matches by name
	matches.sort(key=lambda x: str(x))
	return matches
