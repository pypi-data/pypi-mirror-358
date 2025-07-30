<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Hacking on grab-bin-dist

## Running linters and unit tests

The source of truth for the linters and unit tests configuration for
this project is kept in the `pyproject.toml` file.
A `tox.ini` file is provided; its contents has been automatically
generated from those definitions.

### Using uvoxen

The preferred way to run the test suite is to use
[the uvoxen tool][ringlet-uvoxen] directly:

``` sh
uvoxen uv run
```

### Using tox-stages

If no changes have been made to the `tool.uvoxen` section or its subsections,
[the tox-stages tool][ringlet-test-stages] can be run directly using
the supplied `tox.ini` file and the `tool.test-stages` section in
the `pyproject.toml` file:

``` sh
tox-stages run
```

After any changes to the `tool.uvoxen` section or its subsections,
the Tox configuration can be regenerated and then `tox-stages` can be run
[the tox-stages tool][ringlet-test-stages] can be run:

``` sh
uvoxen tox generate
tox-stages run
```

### Using tox directly

If no changes have been made to the `tool.uvoxen` section or its subsections,
Tox can be run directly using the supplied `tox.ini` file:

``` sh
tox run-parallel
```

After any changes to the `tool.uvoxen` section or its subsections,
the Tox configuration can be regenerated and then Tox can be run in
a single step:

``` sh
uvoxen tox run
```

[ringlet-uvoxen]: https://devel.ringlet.net/devel/uvoxen/ "uvoxen: generate test configuration and run tests"
[ringlet-test-stages]: https://devel.ringlet.net/devel/test-stages/ "tox-stages: run Tox tests in groups, stopping on errors"
