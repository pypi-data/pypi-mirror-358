<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# grab-bin-dist - pack downloaded software into a binary archive

\[[Home][ringlet-home] | [GitLab][gitlab] | [PyPI][pypi] | [ReadTheDocs][readthedocs]\]

## Overview

The `grab-bin-dist` library provides a minimal framework for starting up
a clean-environment Docker container, fetch something from a remote site,
prepare it in custom ways, and then create a tarball that is suitable for
use as a source archive for e.g. Debian packaging.

## Usage

The `grab-bin-dist` library is designed for use in two steps: prepare
an isolated environment (e.g. a Docker container) and then run the "worker"
tool inside that environment.

### Prepare the runtime configuration

Most of the `grab-bin-dist` functions expect a `Config` object:

``` py
from grab_bin_dist import defs as grab_defs
from grab_bin_dist import util as grab_util

grab_cfg: Final = grab_defs.Config(
    additional_packages=["git", "xz-utils"],
    log=grab_util.build_logger(name="grab-something", quiet=False, verbose=True),
    utf8_env=grab_util.get_utf8_env(),
)
```

The `additional_packages` field is used by the `Container.bootstrap()` method
discussed in the next section.

### Bootstrap the Docker container

The first part of the actual work done by `grab-bin-dist` is spawning a container,
making sure there is a suitable Python interpreter there, preparing a virtual
environment, and installing the current Python package - the one that uses
the `grab-bin-dist` functions - within it.
The latter part expects that the current working directory contains a Python
source project, complete with `pyproject.toml` and the Python module source code.
The `bootstrap()` method will bind-mount the current directory within
the newly-spawned container and then run `python3 -m pip install`
(or `uv pip install`) within the virtual environment.
This will allow the later invocation of functions and tools from the current
Python project within the container to perform the actual "fetch and pack up" work.

``` py
from grab_bin_dist import rdocker as grab_rdocker

workdir: Final = pathlib.Path.cwd() / "work"
grab_util.prepare_workdir(grab_cfg, workdir)

cont: Final = grab_rdocker.Container.bootstrap(
    grab_cfg,
    "debian:bookworm",
    slug="grab-something",
    workdir=workdir,
)
```

The `workdir` parameter  points to a directory that will be bind-mounted within
the spawned container and its mount path will later be passed through
environment variables to the worker process.
This is the directory where the worker process is supposed to store the result of
its application-specific actions, e.g. a tarball containing the packed-up data.

### Run the worker process within the container

The virtual environment set up by the `bootstrap()` method is used to spawn
a Python interpreter to execute either a Python module (e.g. one defined in
the current Python project that was installed within the environment) or
a Python command-line program.

``` py
cont.run_python(
    "grab_something.worker",
    [
        *(["-q"] if quiet else []),
        *(["-v"] if verbose else []),
        "pack-it-up",
    ],
)
```

### Do the work within the container

The worker process can examine its environment settings and figure out where to
place the resulting artifacts, e.g. the packed-up tarball.

``` py
from grab_bin_dist import worker as grab_worker

if not grab_worker.is_in_container(grab_cfg):
    sys.exit("Why are we here?")

worker_cfg: Final = grab_worker.build_config("grab-something")

# Perform some preparation while still running as root.
with tempfile.TemporaryDirectory(prefix="grab-something.") as tempd_obj:
    tempd: Final = pathlib.Path(tempd_obj)
    os.chown(tempd, worker_cfg.orig_uid, worker_cfg.orig_gid)

    # Drop privileges so the result file will be owned by the account that
    # the parent process is running under outside the container.
    # This step is not mandatory; `install_file()` may be used directly.
    worker.setuid_if_needed(worker_cfg)

    # Perform the actual work
    destdir, version = fetch_and_pack_stuff_in(tempd)

    # Prepare the meta information about the packed-up things
    # (assuming a `something-0.1.3/Linux/x86_64/usr/bin/something` directory layout)
    mach: Final = platform.machine()
    system: Final = platform.system()
    worker.store_meta(
        worker_cfg,
        destdir,
        packages=[
            grab_defs.MetaPackage(
                name="something",
                version=version,
                mach=mach,
                system=system,
                subdir=pathlib.Path(system) / mach,
            ),
        ],
    )

    # Pack stuff up
    tarball: Final = destdir.parent / f"{destdir.name}.tar.xz"
    subprocess.check_call(
        ["tar", "caf", tarball, "--owner", "root", "--group", "root", "--", destdir.name],
        cwd=destdir.parent,
    )

    # Copy the result tarball to the bind-mounted work directory.
    shutil.move(tarball, worker_cfg.workdir / tarball.name))

    # ...or, if still running as root, make sure the file ownership is correct.
    grab_worker.install_file(
        worker_cfg,
        tarball,
        worker_cfg.workdir / tarball.name,
        owner=worker_cfg.orig_uid,
        group=worker_cfg.orig_gid,
        mode=0o644,
    )
```

### Make sure things seem right outside the container

``` py
archive: Final = grab_util.find_single_file(
    workdir,
    lambda path: path.name.endswith(".tar.xz"),
    lambda other_paths: RuntimeError(repr(other_paths)),
)
meta: Final = grab_util.extract_meta(grab_cfg, archive)
match meta.packages:
    case [pkg] if pkg.name == "something":
        pass

    case other_pkgs:
        sys.exit("Expected a single fetched package, got {other_pkgs!r}")

print(f"Everything seems fine, fetched {archive}")
```

## Contact

The `grab-bin-dist` library was written by [Peter Pentchev][roam].
It is developed in [a GitLab repository][gitlab].
This documentation is hosted at [Ringlet][ringlet-home] with a copy at [ReadTheDocs][readthedocs].

[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[gitlab]: https://gitlab.com/ppentchev/grab-bin-dist "The grab-bin-dist GitLab repository"
[pypi]: https://pypi.org/project/grab-bin-dist/ "The grab-bin-dist Python Package Index page"
[readthedocs]: https://grab-bin-dist.readthedocs.io/ "The grab-bin-dist ReadTheDocs page"
[ringlet-home]: https://devel.ringlet.net/sysutils/grab-bin-dist/ "The Ringlet grab-bin-dist homepage"
