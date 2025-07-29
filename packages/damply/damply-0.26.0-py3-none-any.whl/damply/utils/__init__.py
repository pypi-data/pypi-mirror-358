from __future__ import annotations

import subprocess
from pathlib import Path

from bytesize import ByteSize
from rich.progress import Progress, SpinnerColumn, TextColumn

from .find_readme import find_readme, parse_readme

__all__ = [
	'get_directory_size',
	'count_files',
	'collect_suffixes',
	'find_readme',
	'parse_readme',
]


def get_directory_size(directory: Path, show_progress: bool = True) -> ByteSize:
	if show_progress:
		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			transient=True,  # This makes the progress bar disappear after completion
		) as progress:
			task = progress.add_task(
				f'Calculating size of {str(directory.absolute())}...', total=None
			)
			result = subprocess.run(
				['du', '-s', '-B 1', str(directory)],
				capture_output=True,
				text=True,
				check=True,
			)
			progress.update(task, completed=True)
	else:
		result = subprocess.run(
			['du', '-s', '-B 1', str(directory)],
			capture_output=True,
			text=True,
			check=True,
		)

	size_ = ByteSize(int(result.stdout.split()[0]))
	return size_


def count_files(directory: Path, show_progress: bool = True) -> int:
	count = 0

	with Progress(
		SpinnerColumn(),
		TextColumn('[progress.description]{task.description}'),
		transient=True,
		disable=not show_progress,
	) as progress:
		task = progress.add_task(
			f'Counting files in {str(directory.absolute())}...', total=None
		)

		for path in directory.rglob('*'):
			if path.is_file():
				count += 1

		progress.update(task, completed=True)

	return count


def collect_suffixes(directory: Path, show_progress: bool = True) -> list[str]:
	suffixes: set[str] = set()

	with Progress(
		SpinnerColumn(),
		TextColumn('[progress.description]{task.description}'),
		transient=True,
		disable=not show_progress,
	) as progress:
		task = progress.add_task(
			f'Collecting file extensions in {str(directory.absolute())}...', total=None
		)

		for path in directory.rglob('*'):
			if (
				path.is_file()
				and not path.name.startswith('.')
				and path.suffixes
				and len(path.suffixes) <= 3  # 4 suffixes is crazy
			):
				valid_suffixes = [
					suffix
					for suffix in path.suffixes
					if not any(
						c.isdigit() for c in suffix
					)  # ignore suffixes with digits
				]
				suffixes.add(''.join(valid_suffixes))

		progress.update(task, completed=True)

	return list(suffixes)


if __name__ == '__main__':
	import sys

	if len(sys.argv) != 2:
		sys.exit(1)
	directory_path = Path(sys.argv[1])
	if not directory_path.is_dir():
		sys.exit(1)
	size = get_directory_size(directory_path, show_progress=True)
