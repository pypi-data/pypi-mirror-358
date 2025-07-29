import os
from pathlib import Path

import click
import pandas as pd
import plotly.graph_objects as go
from bytesize import ByteSize

from damply.logging_config import logger


@click.command(no_args_is_help=True)
@click.argument(
	'file_path', type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
	'--threshold_gb',
	default=1,
	help='Minimum size in GB to include in the plot.',
	show_default=True,
	type=int,
)
@click.option(
	'--max-depth-from-root',
	'--max_depth',
	'max_depth_from_root',
	help='Maximum depth from project group root to include in the plot.'
	' i.e /cluster/project/bhklab/rawdata/CCLE/rnaseq is depth 6',
	default=0,
)
def plot(file_path: Path, threshold_gb: int, max_depth_from_root: int) -> None:  # noqa: PLR0915
	"""
	Damply plot from collect-audit csv file.
	FILE_PATH: Path to the CSV file containing directory information.
	"""
	try:
		audit_summary = load_and_filter_audit(
			file_path, threshold_gb, max_depth_from_root
		)
	except ValueError as e:
		logger.exception(
			'Error loading or filtering audit summary. '
			'Please check the input file and try again.'
		)
		raise click.ClickException(str(e)) from e

	all_paths = audit_summary['path'].tolist()

	# get all the common root
	common_root = Path(os.path.commonpath(all_paths))

	logger.info(f'Common root: {common_root}')

	# Add a column for "parent_path"
	# we have parent, but want the full path
	audit_summary['parent_path'] = audit_summary['path'].apply(
		lambda x: str(Path(x).parent) if x != common_root else common_root
	)

	# Esentially get a full list of all possible paths from the root to the leaves
	all_possible_nodes = sorted(
		set([common_root]).union(
			*[permutate_path(Path(path), stop_at=common_root) for path in all_paths]
		),
		key=lambda x: str(x),
	)

	# save to file
	output_path = file_path.with_suffix('.all_paths.csv')
	all_possible_nodes_df = pd.DataFrame(
		{
			'path': [str(node) for node in all_possible_nodes],
			'parent_path': [str(node.parent) for node in all_possible_nodes],
		}
	)
	all_possible_nodes_df.to_csv(output_path, index=False)
	logger.info(f'All possible nodes saved to {output_path}')

	# get rows that are not in the audit summary
	# these will need to be computed from all the children
	missing_nodes = all_possible_nodes_df[
		~all_possible_nodes_df['path'].isin(audit_summary['path'])
	]

	# Ensure that for all paths in all_possible_nodes,
	# their parent is also in the list, at a lower index level
	# since its sorted, and permutated, this MUST be true
	for path in all_possible_nodes:
		if path == common_root:
			continue
		parent_path = path.parent
		if parent_path not in all_possible_nodes:
			logger.error(
				f'Parent path {parent_path} of {path} is not in the list of all possible nodes.'
			)
		elif all_possible_nodes.index(parent_path) > all_possible_nodes.index(path):
			logger.error(
				f'Parent path {parent_path} of {path} is at a higher index than the child path.'
			)

	# Now we can just build the sankey diagram from the audit summary
	# and the missing nodes, which will be computed from the children
	logger.info('Building Sankey diagram...')

	for row in missing_nodes.itertuples(index=False):
		# For each missing node, we need to compute the size and file count
		# from the children of this node in the audit summary
		children = audit_summary[audit_summary['parent_path'] == row.path]
		if children.empty:
			logger.warning(f'No children found for missing node: {row.path}')
			continue

		size = children['size'].sum()

		# Add the computed values to the audit summary
		asd = {
			'path': row.path,
			'parent_path': row.parent_path,
			'name': Path(row.path).name,
			'size': size,  # Convert GB to bytes
			'size_gb': ByteSize(size).GB,
			'file_count': children['file_count'].sum(),
		}

		# add row
		audit_summary = pd.concat(
			[audit_summary, pd.DataFrame([asd])], ignore_index=True
		)

	# Add root node row
	root_size = audit_summary[audit_summary['parent_path'] == common_root.as_posix()][
		'size'
	].sum()

	root_row = {
		'path': str(common_root),
		'parent_path': str(common_root.parent),
		'name': common_root.name,
		'size': root_size,  # Convert GB to bytes
		'size_gb': ByteSize(root_size).GB,
		'file_count': audit_summary.query('parent_path == @common_root')[
			'file_count'
		].sum(),
	}
	audit_summary = pd.concat(
		[audit_summary, pd.DataFrame([root_row])], ignore_index=True
	)

	# re-sort
	audit_summary = audit_summary.sort_values('path', key=lambda x: x.str.len())
	audit_summary = audit_summary.reset_index(drop=True)

	# Add color and label columns
	audit_summary = add_color_and_label_columns(audit_summary)

	logger.info('Creating Sankey diagram...')
	# Map path to index
	path_to_index = {row.path: idx for idx, row in audit_summary.iterrows()}

	# Create link list from parent_path → path
	sources = []
	targets = []
	values = []

	for row in audit_summary.itertuples(index=False):
		if row.parent_path not in path_to_index or row.path not in path_to_index:
			logger.warning(f'Skipping: {row.parent_path} → {row.path}')
			continue

		sources.append(path_to_index[row.parent_path])
		targets.append(path_to_index[row.path])
		values.append(
			row.size_gb or 0.1
		)  # Fallback to 0.1 to keep zero-size links visible

	# Create Sankey figure
	fig = go.Figure(
		go.Sankey(
			node=dict(
				label=audit_summary['label'].tolist(),
				pad=15,
				thickness=20,
				color=audit_summary['color'].tolist(),  # Add colors
			),
			link=dict(
				source=sources,
				target=targets,
				value=values,
				color=audit_summary['color']
				.iloc[targets]
				.tolist(),  # Color links based on target node color
			),
		)
	)

	# Save figure
	output_path = file_path.with_suffix('.sankey.html')
	fig.write_html(output_path)
	logger.info(f'Sankey diagram saved to {output_path}')


def permutate_path(
	path: Path,
	stop_at: Path = Path('/'),
) -> list[Path]:
	"""
	Given a path, return all possible paths from the root to the path
	"""
	assert path.is_absolute(), 'The path must be absolute'

	nodes = []
	while path != stop_at:
		nodes.append(path)
		path = path.parent
	return nodes


def add_color_and_label_columns(audit_summary: pd.DataFrame) -> pd.DataFrame:
	"""
	Add color and label columns to the audit summary dataframe.

	Args:
	    audit_summary: DataFrame with size information

	Returns:
	    pd.DataFrame: DataFrame with added color and label columns
	"""
	# Compute min and max sizes for color normalization
	max_size = audit_summary['size'].max()
	min_size = audit_summary['size'].min()

	logger.info(f'Creating color column with {max_size=} and {min_size=}...')

	# Normalize size to range [0, 1]
	audit_summary['normalized_size'] = (
		(audit_summary['size'] - min_size) / (max_size - min_size)
		if max_size > min_size
		else 0
	)

	# Create a color scale from green to red based on normalized size
	audit_summary['color'] = audit_summary['normalized_size'].apply(
		lambda x: f'rgba({int(255 * (1 - x))}, {int(255 * x)}, 0, 0.8)'
	)

	# Create label column with name and size
	audit_summary['label'] = audit_summary.apply(
		lambda row: f'{row["name"]} ({ByteSize(row["size"]):.0f:GB})'
		if pd.notna(row['size'])
		else row['name'],
		axis=1,
	)

	logger.info('Color and label columns created.')
	return audit_summary


def load_and_filter_audit(
	file_path: Path, threshold_gb: int, max_depth_from_root: int
) -> pd.DataFrame:
	"""
	Load audit CSV and filter by size threshold.

	Args:
	    file_path: Path to the CSV file
	    threshold_gb: Minimum size in GB to include
	    max_depth_from_root: Maximum depth from project group root to include in the plot

	Returns:
	    pd.DataFrame: Filtered audit summary

	Raises:
	    ValueError: If duplicate paths are found
	"""
	audit_summary = pd.read_csv(file_path)
	logger.info(f'Loaded audit summary from {file_path}')
	logger.info(f'Number of rows in audit summary: {len(audit_summary)}')

	unique_parents = audit_summary['parent'].unique()
	logger.info(f'Number of unique parents: {len(unique_parents)}')

	# Filter out rows with size_gb less than threshold
	audit_summary = audit_summary[
		audit_summary['size'].apply(lambda x: ByteSize(x).GB) >= threshold_gb
	]

	logger.info(
		f'Filtered audit summary to {len(audit_summary)} rows with size >= {threshold_gb} GB'
	)

	if max_depth_from_root > 0:
		# Filter rows based on depth from root
		audit_summary = audit_summary[
			audit_summary['path'].apply(
				lambda x: len(Path(x).relative_to(Path(x).anchor).parts)
				<= max_depth_from_root
			)
		]

		logger.info(
			f'Filtered to {len(audit_summary)} rows with depth <= {max_depth_from_root}'
		)

	all_paths = audit_summary['path'].tolist()

	# Check for duplicates
	if len(all_paths) != len(set(all_paths)):
		duplicates = audit_summary[audit_summary.duplicated('path', keep=False)]
		logger.error(
			'Duplicate paths found in the audit summary.'
			' Please ensure all paths are unique.'
		)
		logger.error(
			f'Duplicate paths:\n{duplicates[["path", "name"]].to_string(index=False)}'
		)
		msg = 'Duplicate paths found in audit summary'
		raise ValueError(msg)

	return audit_summary


if __name__ == '__main__':
	plot()
