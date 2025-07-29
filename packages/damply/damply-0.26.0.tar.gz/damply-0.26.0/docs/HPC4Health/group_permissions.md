# Group Permissions

## Get Group membership table

```console

$ damply groups-table -h
Usage: damply groups-table [OPTIONS] [GROUP_NAMES]...

  Generate a user-group membership table from group names.

  This CLI tool takes one or more Unix/Linux group names, collects their
  member users, enriches that information with full user metadata (UID, real
  name, etc.), and outputs a formatted table where each row represents a user
  and each group has its own column.

  By default, the tool uses a set of lab-specific groups but can be customized
  to include others. The resulting table indicates with a 1 or 0 whether a
  user is a member of each group.

  Default groups are: bhklab, radiomics, bhklab_icb,
  bhklab_pmcc_gyn_autosegmentation, bhklab_pmcc_gyn_gu.

  Examples
  --------
  Basic usage with default group set:

      $ damply groups-table

  Include extra groups beyond the default:

      $ damply groups-table --additional-groups ega,cbmp

  Fully custom group list (ignores defaults):

      $ damply groups-table bhklab radiomics cbmp

  Keep other group columns found in users' metadata:

      $ damply groups-table bhklab radiomics --keep-extra-groups

  Export as CSV:

      $ damply groups-table bhklab radiomics --csv > output.csv

  Notes
  -----
  This tool requires access to system group/user information, and may rely on NSS/SSSD/LDAP to
  resolve group memberships. If some groups are not enumerable, users in those groups may be
  resolved indirectly by collecting members from requested groups.

Options:
  -a, --additional-groups TEXT  Additional comma separated groups to the
                                default list.
  -k, --keep-extra-groups       Keep columns for groups not explicitly
                                requested.
  --csv                         Output the table as a CSV file instead of
                                printing it, useful for further processing or
                                > into files.
  -h, --help                    Show this message and exit.
```

!!! example "Example Output"
    ```console
    $ damply groups-table fakegroup
    ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃ name       ┃ realname           ┃ uid   ┃ default_group ┃ othergroup ┃
    ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │ smithj     │ John Smith         │ 11111 │ fakegroup     │ 1          │
    ├────────────┼────────────────────┼───────┼───────────────┼────────────┤
    │ doej       │ Jane Doe           │ 22222 │ fakegroup     │ 0          │
    └────────────┴────────────────────┴───────┴───────────────┴────────────┘
    ```

## Who owns a directory or file?

```console
$ damply whose --help
Usage: damply whose [OPTIONS] [PATH]

  Print the owner of the file or directory.

Options:
  -j, --json  Output in JSON format.
  -h, --help  Show this message and exit.
```
!!! example "Example Output"
    ```console
    $ damply whose /cluster/projects/bhklab/projects/radiogenomics
    Path: /cluster/projects/bhklab/projects/radiogenomics
    Username: t138199uhn
    UID: 90715
    Real Name: Jackie Yang Chen
    ```


## Deleting directories that we don't have Write permissions to

1. Get the full path of the directory you want to delete

    ```console
    /cluster/projects/bhklab/Users/jsmith
    ```

2. Email Zhibin Lu to request he either delete the directory or transfer ownership to you.