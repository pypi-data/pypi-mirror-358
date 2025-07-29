import stat
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import rich.repr
from bytesize import ByteSize
from rich import print

from damply import __version__
from damply.cache_dir import get_cache_dir
from damply.logging_config import logger
from damply.utils import (
	collect_suffixes,
	count_files,
	find_readme,
	get_directory_size,
	parse_readme,
)


@dataclass
class DirectoryAudit:
	path: Path
	owner: str
	group: str
	full_name: str
	permissions: str
	last_modified: datetime
	last_changed: datetime
	readme_path: Path | None = field(default=None)
	metadata: dict[str, str] = field(default_factory=dict, init=False)

	# lazy evaluated because expensive
	size: ByteSize | None = field(default=None, init=False)
	file_count: int | None = field(default=None, init=False)
	file_types: list[str] | None = field(default=None, init=False)

	last_computed: str | None = field(default=None, init=False, repr=False)

	def __post_init__(self) -> None:
		# parse readme file if it exists
		if not self.readme_path:
			return
		self.metadata = parse_readme(self.readme_path)

	@classmethod
	def from_path(cls, path: Path) -> 'DirectoryAudit':
		# resolve ~ and expand environment variables and canonicalize the path
		path = path.expanduser().resolve()
		if not path.exists():
			msg = f'The path {path} does not exist.'
			raise FileNotFoundError(msg)
		elif not path.is_dir():
			msg = f'The path {path} is not a directory.'
			raise NotADirectoryError(msg)

		stats = path.stat()

		try:
			from grp import getgrgid
			from pwd import getpwuid

			pwuid_name = getpwuid(stats.st_uid).pw_name
			pwuid_gecos = getpwuid(stats.st_uid).pw_gecos
			group_name = getgrgid(stats.st_gid).gr_name
		except ImportError:
			pwuid_name = 'Unknown'
			pwuid_gecos = 'Unknown'
			group_name = 'Unknown'
		except KeyError:
			pwuid_name = 'Unknown'
			pwuid_gecos = 'Unknown'
			group_name = 'Unknown'

		toronto_tz = ZoneInfo('America/Toronto')
		audit = DirectoryAudit(
			path=path,
			owner=pwuid_name,
			group=group_name,
			full_name=pwuid_gecos,
			permissions=stat.filemode(stats.st_mode),
			last_modified=datetime.fromtimestamp(stats.st_mtime, tz=toronto_tz),
			last_changed=datetime.fromtimestamp(stats.st_ctime, tz=toronto_tz),
			readme_path=find_readme(path),
		)
		return audit

	def compute_details(self, show_progress: bool = True, force: bool = False) -> None:
		"""Compute size and file count, using cache if available and up-to-date.

		Args:
		    show_progress: Whether to show progress bars during computation
		    force: If True, recompute regardless of cache
		"""
		# Check if we have cached data and whether it's still valid
		if force:
			logger.debug('Force recompute requested, ignoring cache.')
			# delete the cache if it exists
			cache_path = self._get_cache_path()
			if cache_path.exists():
				logger.debug(f'Deleting cache file: {cache_path}')
				cache_path.unlink()

			# remove cached values
			self.size = None
			self.file_count = None
			self.file_types = None
		elif self._get_from_cache():
			logger.debug('Cache loaded successfully.')
			return
		else:
			logger.debug('Cache miss.')

		# Compute the values and cache them
		self.compute_size(show_progress=show_progress)
		self.compute_file_count(show_progress=show_progress)
		self.compute_file_types(show_progress=show_progress)

		self.last_computed = datetime.now(ZoneInfo('America/Toronto')).strftime(
			'%Y-%m-%d %H:%M:%S'
		)
		self._save_to_cache()

	def compute_file_count(self, show_progress: bool = True) -> int:
		"""Count files in the directory and return the count."""
		if self.file_count is None:
			self.file_count = count_files(
				directory=self.path, show_progress=show_progress
			)
		return self.file_count

	def compute_file_types(self, show_progress: bool = True) -> set[str]:
		"""Get unique file types in the directory."""
		if self.file_types is None:
			self.file_types = collect_suffixes(
				directory=self.path, show_progress=show_progress
			)
		return self.file_types

	def compute_size(self, show_progress: bool = True) -> ByteSize:
		if self.size is None:
			self.size = get_directory_size(
				directory=self.path, show_progress=show_progress
			)
		return self.size

	def _get_cache_path(self) -> Path:
		"""Get the path for the cache file for this directory."""
		cache_dir = get_cache_dir() / 'directory_audits'
		cache_dir.mkdir(parents=True, exist_ok=True)

		# Create a unique filename based on the path
		path_str = str(self.path.absolute())
		import hashlib

		path_hash = hashlib.md5(path_str.encode()).hexdigest()
		return cache_dir / f'{path_hash}.json'

	def _save_to_cache(self) -> None:
		"""Save the current state to cache."""
		cache_path = self._get_cache_path()
		import json

		# Create a dict with all the necessary data
		cache_data = {
			'path': str(self.path.absolute()),
			'last_computed': self.last_computed,
			'size': str(self.size) if self.size is not None else None,
			'file_count': self.file_count,
			'file_types': self.file_types if self.file_types else None,
			'last_modified': self.last_modified.isoformat()
			if self.last_modified
			else None,
			# 'last_accessed': self.last_accessed.isoformat()
			# if self.last_accessed
			# else None,
			'last_changed': self.last_changed.isoformat()
			if self.last_changed
			else None,
			'damply_version': __version__,  # Save the current version
		}

		with cache_path.open('w', encoding='utf-8') as f:
			json.dump(cache_data, f)

	def _get_from_cache(self) -> bool:  # noqa: PLR0911
		"""
		Try to load data from cache if it's newer than the last modified date.

		Returns:
		    bool: True if cache was loaded successfully, False otherwise
		"""
		cache_path = self._get_cache_path()
		if not cache_path.exists():
			return False

		import json

		try:
			with cache_path.open('r', encoding='utf-8') as f:
				cache_data = json.load(f)

			from packaging import version

			# Check version compatibility
			cached_version = cache_data.get('damply_version', None)
			if cached_version is None:
				return False
			# Only invalidate cache on major version changes
			current_major = version.parse(__version__).major
			cached_major = version.parse(cached_version).major
			if cached_major < current_major:
				logger.debug(
					f'Cache major version {cached_version} is older than current version {__version__}.'
				)
				# Delete the outdated cache
				cache_path.unlink()
				return False

			# Check if the cache is for the same path
			# this would be wild to not be the same right now
			if cache_data.get('path') != str(self.path.absolute()):
				return False

			# Check if the directory has been modified since the cache was created
			cached_last_modified = datetime.fromisoformat(
				cache_data.get('last_modified')
			)

			# Ensure we're comparing datetimes with the same timezone awareness
			if (
				cached_last_modified.tzinfo is None
				and self.last_modified.tzinfo is not None
			):
				# Convert naive to aware using the same timezone as self.last_modified
				cached_last_modified = cached_last_modified.replace(
					tzinfo=self.last_modified.tzinfo
				)
			elif (
				cached_last_modified.tzinfo is not None
				and self.last_modified.tzinfo is None
			):
				# Convert self.last_modified to aware using cached timezone
				self.last_modified = self.last_modified.replace(
					tzinfo=cached_last_modified.tzinfo
				)

			if self.last_modified > cached_last_modified:
				return False

			# Load the cached values
			if cache_data.get('size') is not None:
				self.size = ByteSize(cache_data['size'])
			self.file_count = cache_data.get('file_count')
			self.last_computed = cache_data.get('last_computed')
			self.file_types = cache_data.get('file_types', set())
		except (json.JSONDecodeError, KeyError, ValueError) as e:
			logger.debug(f'Error loading cache: {e}')
			# If anything goes wrong, delete cache and recompute
			if cache_path.exists():
				cache_path.unlink()
			return False
		else:
			return True

	def __rich_repr__(self) -> rich.repr.Result:
		yield 'path', self.path.absolute()
		yield 'owner', self.owner
		yield 'group', self.group
		yield 'full_name', self.full_name
		yield 'permissions', self.permissions
		# yield 'last_accessed', self.last_accessed.date() if self.last_accessed else None
		yield 'last_modified', self.last_modified.date() if self.last_modified else None
		yield 'last_changed', self.last_changed.date() if self.last_changed else None
		yield 'size', self.size if self.size is not None else 'Not computed yet'
		yield (
			'file_count',
			self.file_count if self.file_count is not None else 'Not computed yet',
		)
		yield (
			'file_types',
			self.file_types if self.file_types is not None else 'Not computed yet',
		)
		yield 'readme_path', self.readme_path if self.readme_path else 'No README found'
		yield (
			'metadata',
			self.metadata if self.metadata else 'No metadata found in README',
		)

	def to_dict(self) -> dict:
		result = {}
		for k, v in asdict(self).items():
			if k.startswith('_'):
				continue

			# Convert datetime to date for display purposes
			if isinstance(v, datetime):
				result[k] = v.date()
			else:
				result[k] = v
		return result

	def to_json(self, indent: int = 4) -> str:
		import json

		return json.dumps(self.to_dict(), default=str, indent=indent)


if __name__ == '__main__':
	from rich import print

	audit = DirectoryAudit.from_path(
		Path('/cluster/projects/radiomics/Projects/testimgtools_benchmark/results')
	)
	print(audit)
	audit.compute_details(show_progress=True, force=True)

	print('*' * 20)
	print(audit.to_dict())
	print('*' * 20)
	print(audit.to_json())

	print('*' * 20)
	print(f'Size: {audit.size:.2f:GB}')

	print('*' * 20)
	print(audit.to_dict())
