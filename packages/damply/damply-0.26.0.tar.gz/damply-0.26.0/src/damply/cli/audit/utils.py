from pathlib import Path
from typing import Union


class InvalidProjectGroupError(ValueError):
	"""Raised when the project group is not 'bhklab' or 'radiomics'."""


class OutsideProjectPathError(ValueError):
	"""Raised when the source directory is not within the expected project base path."""


def get_project_group(source_dir: Union[str, Path]) -> str:
	"""Extract the project group from the source directory path.

	Args:
	    source_dir: Path to the source directory.

	Returns:
	    The project group name ('bhklab' or 'radiomics').

	Raises:
	    InvalidProjectGroupError: If the group is not bhklab or radiomics.
	    OutsideProjectPathError: If the path doesn't start with /cluster/projects.

	Examples:
	    >>> get_project_group('/cluster/projects/bhklab/rawdata/CCLE')
	    'bhklab'

	    >>> get_project_group(Path('/cluster/projects/radiomics/PublicDataSets'))
	    'radiomics'
	"""
	source_path = Path(source_dir).resolve()
	parts = source_path.parts

	if len(parts) < 4 or parts[1] != 'cluster' or parts[2] != 'projects':
		msg = (
			'Input directory must start with /cluster/projects/bhklab '
			'or /cluster/projects/radiomics.'
		)
		raise OutsideProjectPathError(msg)

	project_group = parts[3]
	if project_group not in {'bhklab', 'radiomics'}:
		msg = (
			f"Invalid project group '{project_group}'. Must be 'bhklab' or 'radiomics'."
		)
		raise InvalidProjectGroupError(msg)

	return project_group


def get_parents_path(project_group: str, source_dir: Union[str, Path]) -> str:
	"""Compute the relative path from the project root to the source directory.

	Args:
	    project_group: 'bhklab' or 'radiomics'.
	    source_dir: Full path to the source directory.

	Returns:
	    A string path relative to the group root.

	Raises:
	    OutsideProjectPathError: If the path is not under the group base path.

	Examples:
	    >>> get_parents_path('bhklab', '/cluster/projects/bhklab/rawdata/CCLE')
	    'rawdata/CCLE'
	"""
	base_path = Path(f'/cluster/projects/{project_group}').resolve()
	source_path = Path(source_dir).resolve()

	try:
		return str(source_path.relative_to(base_path))
	except ValueError as e:
		msg = f'{source_path} is not within {base_path}'
		raise OutsideProjectPathError(msg) from e
