"""CLI tool to take a list of group names on the system, get their users, and print a table.

i.e given groups 'bhklab, radiomics, bhklab_icb' it will print a table of users in those groups.
columns would be:

- username
- realname
- userid
- bhklab
- radiomics
- bhklab_icb

and then in each row, it will have a 1 if the user is in that group, and a 0 if not.

"""

from typing import TYPE_CHECKING, Sequence

import click

from damply import logger

if TYPE_CHECKING:
	import pandas as pd

DEFAULT_GROUPS = [
	'bhklab',
	'radiomics',
	'ega',
	'bhklab_icb',
	'bhklab_pmcc_gyn_autosegmentation',
	'bhklab_pmcc_gyn_gu',
	'pmdatascience',
]


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
	'--additional-groups',
	'-a',
	'additional_groups',
	help='Additional comma separated groups to the default list.',
	default=None,
)
@click.option(
	'--keep-extra-groups',
	'-k',
	'keep_extra_groups',
	is_flag=True,
	default=False,
	help='Keep columns for groups not explicitly requested.',
)
@click.option(
	'--csv',
	is_flag=True,
	default=False,
	help='Output the table as a CSV file instead of printing it, useful for further processing or > into files.',
)
@click.argument('group_names', nargs=-1, required=False)
def groups_table(
	group_names: list[str] | None = None,
	additional_groups: str | None = None,
	keep_extra_groups: bool = False,
	csv: bool = False,
) -> None:
	"""
	Generate a user-group membership table from group names.

	This CLI tool takes one or more Unix/Linux group names, collects their member users,
	enriches that information with full user metadata (UID, real name, etc.), and outputs
	a formatted table where each row represents a user and each group has its own column.

	By default, the tool uses a set of lab-specific groups but can be customized to include
	others. The resulting table indicates with a 1 or 0 whether a user is a member of each group.

	Default groups are: bhklab, radiomics, bhklab_icb, bhklab_pmcc_gyn_autosegmentation, bhklab_pmcc_gyn_gu.

	\b
	Examples
	--------
	Basic usage with default group set:

	    $ groups-table

	Include extra groups beyond the default:

	    $ groups-table --additional-groups ega,cbmp

	Fully custom group list (ignores defaults):

	    $ groups-table bhklab radiomics cbmp

	Keep other group columns found in users' metadata:

	    $ groups-table bhklab radiomics --keep-extra-groups

	Export as CSV:

	    $ groups-table bhklab radiomics --csv > output.csv

	\b
	Notes
	-----
	This tool requires access to system group/user information, and may rely on NSS/SSSD/LDAP to
	resolve group memberships. If some groups are not enumerable, users in those groups may be
	resolved indirectly by collecting members from requested groups.
	"""
	logger.debug('Starting groups_table CLI tool...')
	from itertools import chain

	from rich import print

	from damply.admin import GroupInfo, UserInfo

	if not group_names:
		group_names = DEFAULT_GROUPS

	if additional_groups:
		group_names.extend(additional_groups.split(','))

	logger.debug('Fetching group information...')
	group_info_db = [GroupInfo.from_group_name(group) for group in group_names]

	all_usernames = sorted(set(chain.from_iterable(g.members for g in group_info_db)))

	user_info_db: list[UserInfo]
	logger.debug('Fetching user information...')
	user_info_db = [UserInfo.from_username(username) for username in all_usernames]

	# print([u.to_dict() for u in user_info_db])
	user_dicts = [u.to_dict() for u in user_info_db]

	group_data_df = build_group_membership_table(
		user_dicts=user_dicts,
		requested_groups=group_names,
		keep_extra_groups=keep_extra_groups,
	)

	if csv:
		logger.debug('Outputting table as CSV...')
		# print the csv to stdout
		print(group_data_df.to_csv(index=False))
	else:
		# Pretty-print the DataFrame using Rich
		from rich.console import Console
		from rich.table import Table

		console = Console()
		table = Table(show_lines=True)
		for col in group_data_df.columns:
			table.add_column(str(col))

		for _, row in group_data_df.iterrows():
			table.add_row(*[str(x) for x in row])

		console.print(table)


def build_group_membership_table(
	user_dicts: list[dict],
	requested_groups: Sequence[str],
	keep_extra_groups: bool = False,
) -> 'pd.DataFrame':
	"""
	Processes a list of user dictionaries to create a table showing which
	users belong to which groups.
	Each group becomes a column with binary (0/1) values indicating membership.

	Parameters
	----------
	user_dicts : list[dict]
	    List of user dictionaries containing user metadata and group memberships.
	    Each dict must have 'name', 'realname', 'uid', 'default_group' and optional 'groups' keys.
	requested_groups : Sequence[str]
	    Sequence of group names to include in the output table.
	keep_extra_groups : bool, default=False
	    If True, includes all groups found in user_dicts in addition to requested_groups.
	    If False, only includes requested_groups.
	Returns
	-------
	pd.DataFrame
	    DataFrame with user metadata columns (name, realname, uid, default_group) and
	    binary group membership columns (1 for membership, 0 for non-membership).
	"""
	import pandas as pd

	all_requested_groups = set(requested_groups)

	logger.debug('Building group membership table...')

	# Start with the base user metadata
	base_df = pd.DataFrame(user_dicts)
	base_df = base_df[['name', 'realname', 'uid', 'default_group']]

	# Build group presence DataFrame
	group_flags_df = pd.DataFrame.from_records(
		[
			{**{g: 1 for g in user.get('groups', [])}, 'name': user['name']}
			for user in user_dicts
		]
	).fillna(0)

	# Merge without duplicating base metadata
	group_data_df = base_df.merge(group_flags_df, on='name', how='left').fillna(0)

	# Identify group columns (exclude base ones)
	group_cols = [
		c
		for c in group_data_df.columns
		if c not in {'name', 'realname', 'uid', 'default_group'}
	]

	# Ensure binary (int) for group flags
	group_data_df[group_cols] = group_data_df[group_cols].astype(int)

	# Control which group columns to keep
	if not keep_extra_groups:
		cols = ['name', 'realname', 'uid', 'default_group'] + sorted(
			all_requested_groups
		)
	else:
		requested = [g for g in requested_groups if g in group_cols]
		others = sorted(set(group_cols) - set(requested))
		cols = ['name', 'realname', 'uid', 'default_group'] + requested + others

	group_data_df = group_data_df[cols]

	return group_data_df
