# winzy-selected-file

[![PyPI](https://img.shields.io/pypi/v/winzy-selected-file.svg)](https://pypi.org/project/winzy-selected-file/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/winzy-selected-file?include_prereleases&label=changelog)](https://github.com/sukhbinder/winzy-selected-file/releases)
[![Tests](https://github.com/sukhbinder/winzy-selected-file/workflows/Test/badge.svg)](https://github.com/sukhbinder/winzy-selected-file/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/winzy-selected-file/blob/main/LICENSE)

Get selected files as a text file on mac os

## Installation

First [install winzy](https://github.com/sukhbinder/winzy) by typing

```bash
pip install winzy
```

Then install this plugin in the same environment as your winzy application.
```bash
winzy install winzy-selected-file
```
## Usage

To get help type ``winzy  sfiles --help``

## Demo
![Demo of winzy sfiles](https://raw.githubusercontent.com/sukhbinder/winzy-selected-file/refs/heads/main/demo-selected-files.gif)

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd winzy-selected-file
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
