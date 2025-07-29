# Benchmarking infrastructure for the Faster CPython project

This repository contains a number of GitHub Actions workflows to run benchmarks on a set of private, self-hosted, bare metal machines.

## The workflows

There is a single user-facing workflow, `benchmark.yml`, that [reuses](https://docs.github.com/en/actions/using-workflows/reusing-workflows) the other workflows, prefixed with `_`.

Unfortunately, it is not possible to select a self-hosted runner based on an input variable.
To get around this, some of the workflow files are generated from "templates" by the `install.py` script to work around limitations in the Github Actions workflow language.
("Templates" is probably overstating it -- it's just YAML with some sections repeated and modified.)

### benchmark.yml

This is the main user entry point.  See the [user documentation](bench_runner/templates/README.md) for information about the parameters it takes.

It kicks off one or two sets of benchmarking runs (depending on the value of `benchmark_base`) (`_benchmark.yml`), then generates the derived results (`_generate.yml`), and publishes public results, if any (`_publish.yml`).

### _benchmark.yml

This workflow manages building a specific revision of CPython, runs a complete set of benchmarks, and then commits the pyperformance-style `.json` file to this repo.
By default, both the `pyperformance` and `pyston` benchmarks suites are run, configured by the `benchmark.manifest` file.

There are separate jobs for each runner.
If the user chose to run on all runners, these jobs may run in parallel, but otherwise, each runner only handles one job at a time to get more accurate benchmarks.

There are additional parameters available to save time during debugging, but these are not exposed to the user since they create results that aren't useful for full comparisons:

- `pgo`: Build with PGO and LTO
- `dry_run`: Don't save the results to the repo

The implementation of this workflow (for everything but the CPython compilation itself) is in `bench_runner/scripts/run_benchmarks.py`.

### _pystats.yml

This workflow runs the benchmarks using a build with `--enable-pystats`, and then saves the results run through CPython's `Tools/scripts/summarize_stats.py` script.

Unlike the regular benchmarks, we don't care about timings, so this workflow is run in a cloud VM, on Linux only.

The implementation of this workflow (for everything but the CPython compilation itself) is in `bench_runner/scripts/run_benchmarks.py`.

### _generate.yml

This workflow reads the `.json` files created in the previous step and creates derived tables and plots, as well as indices of the results.

This is designed such that all of the derived data can be regenerated from the raw data at any time, so as we refine or add more analyses, we can regenerate these outputs without needing to recapture the raw data.
To regenerate all derived data, check the `force` checkbox when running this workflow.

Each result is compared against important "reference" versions, specified in the `bases.txt` file in this repository.
This would usually be the last two stable major releases.
To change the reference versions, just make sure the data set for the reference versions exist, then edit and commit `bases.txt` and run this workflow.
Additionally, if a benchmark has the `commit_merge_base` metadata entry, it is also compared against that commit hash, if the data exists.

Each comparison produces two files:

- A markdown table produced by `pyperf compare_to`.
- A set of violin plots showing the distribution of the difference in timings for each benchmark.

Additionally, indices are generated in `README.md` and `RESULTS.md`.
The latter only contains the most recent revision of each named Python version.

The implementation of this workflow is in `bench_runner/scripts/generate_results.py`.

### _publish.yml

This step mirrors the private `benchmarking` repo to the public `benchmarking-public` repo.
This needs a token with contents write access and workflow write access to the `benchmarking-public` repo called `BENCHMARK_MIRROR`.

### _weekly.yml

This does a benchmarking run automatically every Sunday.
It tests `python/cpython main` on all runners and then publishes the results.

## Results naming convention

Results are organized into directories.
Each directory contains results for a specific commit hash, but may contain results from multiple platforms.
The directories are named:

```text
bm-{date}-{version}-{cpython_hash}
```

- `date`: the commit date of the revision being benchmarked.
  This is an ISO date with the dashes removed.
  It is truncated 20 characters, since full SHAs can make the paths too long for Windows to handle.
- `version`: the version of CPython, as returned by `platform.python_version()`.
- `cpython_hash`: The first 8 characters of the git hash. (`fork`, `ref` and `version` can be strictly derived from the git hash, but are included for convenience).

Within each directory are files, each with the following root name:

```text
bm-{date}-{nickname}-{machine}-{fork}-{ref}-{version}-{cpython_hash}
```

In addition to the fields defined above, the filenames add:

- `nickname`: The unique nickname for the runner. See `runners.ini`.
- `machine`: CPU architecture, as returned by `platform.machine()`
- `fork`: the fork of CPython as requested to the benchmark job.
- `ref`: the branch, tag or SHA specified to run as requested to the benchmark job.

With this base, there are files with the following suffixes:

- `.json`: The raw results from `pyperformance`.
- `-vs-{base}.md`: A table comparing the results against the given base, as returned by `pyperf compare_to`.
- `-vs-{base}.svg`: A set of violin plots with the distribution of differences for each benchmark.
- `-pystats.json`: The raw results from a pystats run.
- `-pystats.md`: The results of a pystats run, summarized in human-readable form.

## Metadata

The following metadata fields are added to the raw results (in addition to those provided by `pyperformance`):

- `commit_id`: the git hash of the revision being benchmarked
- `commit_fork`: the fork of CPython that was requested
- `commit_branch`: the branch, tag or SHA requested
- `commit_date`: the commit date of the revision being benchmarked (in ISO format)
- `commit_merge_base`: the commit where the branch diverged from `upstream/main`
- `benchmark_hash`: a combined hash of the pyperformance and pyston benchmark suites.
  Used to confirm that two sets of benchmarks used the same benchmarking code.
- `github_actions_url`: the URL to the github action that produced the result. Useful for getting a full log of the run to debug issues.
