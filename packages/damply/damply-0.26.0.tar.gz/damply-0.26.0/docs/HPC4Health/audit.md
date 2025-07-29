# Auditing the DMP on HPC4Health

??? note "What is HPC4Health?"
    The [High Performance Computing for Health (HPC4Health / H4H)](https://bhklab.github.io/HPC4Health/) is a computing cluster operated at the University Health Network. The audit functionality of `damply` was specifically developed for usage by the BHKLab on H4H. The following instructions will not work unless you have access to the BHKLab project folders on H4H.

Damply comes equipped with ability to audit your DMP setup to track things like memory usage and metadata. This functionality is to be used for managing the `bhklab` and `radiomics` project directories on H4H.

## Installing Damply for the Command Line

1. `salloc` onto the [build node](https://bhklab.github.io/HPC4Health/setup/02_ssh_into_h4h/?h=build#remote-access-nodes:~:text=Remote%20Access%20Nodes-,%F0%9F%94%97,-Here%20is%20a) on H4H.

2. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/), which is a tool that will make any python package tools available globally without messing around with virtual environments or `base` conda environments.

3. Install Damply by running
    ```bash
    uv tool install --refresh --force --upgrade damply
    ```

Now you can use `damply` from the command line on any node on HPC4Health, including the login node. 

```console
$ which damply
~/.local/bin/damply
$ damply --help

Usage: damply [OPTIONS] COMMAND [ARGS]...

  A tool to interact with systems implementing the Data Management Plan (DMP)
  standard.

  This tool is meant to allow sys-admins to easily query and audit the
  metadata of their projects.

  To enable logging, set the env variable `DAMPLY_LOG_LEVEL`.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  audit         Audit all subdirectories and aggregate damply output into...
  full-audit    Run a full audit for the specified project group.
  groups-table  Generate a user-group membership table from group names.
  project       Display information about the current project.
  whose         Print the owner of the file or directory.
```

## Audit

!!! info "TLDR pipeline"
    1. Run `damply full-audit bhklab` to submit a bunch of jobs to the cluster
    2. Wait for the jobs to finish
    3. Run `damply collect-audits bhklab` to collect the results and save csv to <filepath>
    4. Run `damply plot <filepath>` to create a damply plot html file
    5. `scp` the html file to your local machine and open it in Chrome

### Full Audit

The basic audit batch submissions have been embedded into the `damply` CLI tool.

```console
$ damply full-audit --help
Usage: damply full-audit [OPTIONS] PROJECT_GROUP

  Run a full audit for the specified project group.

  This will essentially, submit a bunch of sbatch jobs to the cluster for all
  the directories in the project group.

Options:
  -f, --force-compute-details  Force the computation of details for the
                               directory and subdirectories regardless of
                               cache.
```

**Step 1**: `salloc` into a compute node. This does not need a lot of compute power.

```bash
salloc -c 1 --mem=256 --time=0:15:0
```

**Step 2**: Run the `full-audit` command. This will submit a bunch of jobs, that will run `damply audit` on all the subdirectories. See the [source code](https://github.com/bhklab/damply/blob/94e704e2ae8846161359604e42e185d08ef0ee8b/src/damply/cli/audit/main.py#L141) for the details of how it chooses the directories to audit.

=== "bhklab"
    ```bash
    damply full-audit bhklab
    ```

=== "radiomics"
    ```bash
    damply full-audit radiomics
    ```

The results will be stored in:

=== "bhklab"
    ```console
    /cluster/projects/bhklab/admin/audit/...
    ```

=== "radiomics"
    ```console
    /cluster/projects/radiomics/admin/audit/...
    ```

!!! info

    Damply uses caching to avoid recomputing the same metadata for directories that have not changed.
    This means that jobs that dont need recomputation will run in a few seconds, while jobs that need
    recomputation can take up to an hour or more, depending on the size of the directory and the number
    of files in it.

    If you want to force the recomputation of the metadata, you can use the `--force-compute-details` flag


### Collecting Results

After all the jobs have finished, we need to collect the results.

```console
$ damply collect-audits --help

Usage: damply collect-audits [OPTIONS] PROJECT_GROUP

  Collect audits for a project group (after full-audit).

  keep_children: If

Options:
  -f, --force      Force collection even if summary exists
  --keep-children  Only collect source directories (aka higher level
                   directories only)
  -h, --help       Show this message and exit.
```

Run the command:
=== "bhklab"
    ```bash
    damply collect-audits bhklab
    ```

=== "radiomics"
    ```bash
    damply collect-audits radiomics
    ```


This will collect all the audit results from the subdirectories and aggregate them into a single CSV file.
The results will be stored in:

=== "bhklab"
    ```console
    /cluster/projects/bhklab/admin/audit/results/<date>/
    ```

=== "radiomics"
    ```console
    /cluster/projects/radiomics/admin/audit/results/<date>/
    ```

### Plotting Results

Run the command:

```console
damply plot /cluster/projects/bhklab/admin/audit/results/<date>/<path_to_csv>
```