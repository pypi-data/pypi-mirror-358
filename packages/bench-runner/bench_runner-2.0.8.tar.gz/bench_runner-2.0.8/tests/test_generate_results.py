import collections
import json
from pathlib import Path
import shutil


import pytest


from bench_runner.scripts import generate_results


DATA_PATH = Path(__file__).parent / "data"


def _copy_repo(tmp_path):
    repo_path = tmp_path / "repo"
    shutil.copytree(DATA_PATH, tmp_path / "repo")
    return repo_path


def _run_for_bases(bases, repo_path, force=False, has_base=[], check_readmes=True):
    results_path = repo_path / "results"

    generate_results._main(repo_path, force=force, bases=bases)

    for dirpath in results_path.iterdir():
        if not dirpath.is_dir():
            continue

        files_by_type = collections.Counter()
        for filepath in dirpath.iterdir():
            files_by_type[filepath.suffix] += 1
        assert files_by_type[".json"] == 1

        if any(base in dirpath.name for base in has_base):
            assert files_by_type[".md"] == 4
            assert files_by_type[".svg"] == 4
        elif any(base in dirpath.name for base in bases):
            assert files_by_type[".md"] in (2, 3)
            assert files_by_type[".svg"] in (1, 2)
        else:
            assert files_by_type[".md"] in (3, 4)
            assert files_by_type[".svg"] in (2, 3)

        # Make sure all files in the directory have a link
        contents = (dirpath / "README.md").read_text()
        assert contents.count("\n- [") in (
            len(list(dirpath.iterdir())),
            len(list(dirpath.iterdir())) - 1,
        )
        assert "## linux x86_64" in contents
        for base in bases:
            if base not in dirpath.name:
                assert f"### vs. {base}" in contents

    if check_readmes:
        contents = (repo_path / "README.md").read_text()
        assert contents.count("\n|") == 5

        contents = (repo_path / "RESULTS.md").read_text()
        assert contents.count("\n|") == 13


def test_main(tmp_path, monkeypatch):
    repo_path = _copy_repo(tmp_path)

    monkeypatch.chdir(repo_path)

    # Hack up so one of the results has an explicit commit_merge_base
    result_with_base = (
        repo_path
        / "results"
        / "bm-20221119-3.12.0a3+-b0e1f9c"
        / "bm-20221119-linux-x86_64-python-main-3.12.0a3+-b0e1f9c.json"
    )
    with open(result_with_base) as fd:
        contents = json.load(fd)
    contents["metadata"][
        "commit_merge_base"
    ] = "9d38120e335357a3b294277fd5eff0a10e46e043"
    with open(result_with_base, "w") as fd:
        json.dump(contents, fd)
    # End hack

    # Run twice to make sure there are no side effects of that
    _run_for_bases(["3.10.4", "3.11.0b3"], repo_path, has_base=["b0e1f9c"])
    _run_for_bases(["3.10.4", "3.11.0b3"], repo_path, has_base=["b0e1f9c"])


def test_change_bases(tmp_path, monkeypatch):
    repo_path = _copy_repo(tmp_path)
    monkeypatch.chdir(repo_path)

    _run_for_bases(["3.10.4", "3.11.0b3"], repo_path)
    contents = (repo_path / "README.md").read_text()
    assert "| vs. 3.10.4: | vs. 3.11.0b3: | vs. base: |" in contents

    _run_for_bases(["3.10.4", "3.11.0b2"], repo_path, force=True)
    contents = (repo_path / "README.md").read_text()
    assert "| vs. 3.10.4: | vs. 3.11.0b2: | vs. base: |" in contents
    assert "| vs. 3.10.4: | vs. 3.11.0b3: | vs. base: |" not in contents

    (
        repo_path
        / "results"
        / "bm-20221119-3.12.0a3+-b0e1f9c"
        / "bm-20221119-linux-x86_64-python-main-3.12.0a3+-b0e1f9c.json"
    ).unlink()

    with pytest.raises(ValueError):
        generate_results._main(repo_path, bases=[])


def test_fork_with_hyphen(tmp_path):
    repo_path = _copy_repo(tmp_path)

    # Hack up so one of the results has fork with a hyphen
    result = (
        repo_path
        / "results"
        / "bm-20221119-3.12.0a3+-b0e1f9c"
        / "bm-20221119-linux-x86_64-python-main-3.12.0a3+-b0e1f9c.json"
    )
    result_new = result.with_name(result.name.replace("python", "with%2dhyphen"))

    result.rename(result_new)

    with open(result_new) as fd:
        contents = json.load(fd)
    contents["metadata"]["fork"] = "with-hyphen"
    with open(result_new, "w") as fd:
        json.dump(contents, fd)
    # End hack

    _run_for_bases(["3.10.4", "3.11.0b3"], repo_path, check_readmes=False)

    contents = (repo_path / "RESULTS.md").read_text()
    assert contents.count("with-hyphen") == 1
    assert contents.count(" with%2dhyphen ") == 0
    assert (
        contents.count("with%252dhyphen-main-3.12.0a3%2B-b0e1f9c-vs-3.11.0b3.md") == 1
    )
