"""helper function to find and parse the README file in a directory.

The README can either be in the root OR in a subdirectory called 'docs'.

also a fun
"""

import re
from pathlib import Path

from damply.logging_config import logger


def find_readme(directory: Path) -> Path | None:
	"""Find any README file in the given directory or its 'docs' subdirectory."""

	readmes = [
		f for f in directory.glob('readme*', case_sensitive=False) if f.is_file()
	] + [
		f
		for f in (directory / 'docs').glob('readme*', case_sensitive=False)
		if f.is_file()
	]

	if not readmes:
		return None

	if len(readmes) == 1:
		return readmes[0]

	# if there are multiple readmes, just prefer the the first one
	logger.warning(
		f'Found {len(readmes)} README files in {directory}. '
		'Returning the first one found. '
	)
	return readmes[0]


def parse_readme(
	readme: Path,
	pattern: re.Pattern[str] = re.compile(r'^#([A-Z]+): (.+)$'),
) -> dict[str, str]:
	"""Parse the README file and return its content as a string."""
	current_field = None
	current_value = []
	content_lines = []  # everything else that is not a field
	metadata = {}
	with readme.open(mode='r') as file:
		for line in file:
			if line.strip() == '' and current_field:
				# End current field on double newline
				metadata[current_field] = ' '.join(current_value).strip()
				current_field = None
				current_value = []
			else:
				match = pattern.match(line.strip())
				if match:
					if current_field:
						metadata[current_field] = ' '.join(current_value).strip()
					current_field, current_value = (
						match.groups()[0],
						[match.groups()[1]],
					)
				elif current_field:
					current_value.append(line.strip())
				else:
					content_lines.append(line.strip())

		if current_field:
			metadata[current_field] = ' '.join(current_value).strip()

	# were gonna ignore the content lines for now
	# metadata['content'] = '\n'.join(content_lines).strip()
	return metadata


if __name__ == '__main__':
	import click

	@click.command()
	@click.argument(
		'directory', type=click.Path(exists=True, file_okay=False, dir_okay=True)
	)
	def main(directory: str) -> None:
		"""Find and parse the README file in the given directory."""
		readme_path = find_readme(Path(directory))
		if readme_path:
			metadata = parse_readme(readme_path)
			for _key, _value in metadata.items():
				pass
		else:
			pass

	main()
