# Changelog

## 2.1.2 (Jul, 14th 2024)

* really drop python<=3.7 support by @kloczek in https://github.com/xlwings/jsondiff/pull/78
* Added docstrings by @payam54 in https://github.com/xlwings/jsondiff/pull/79
* remove last bits of python2 support by @corytodd in https://github.com/xlwings/jsondiff/pull/80

## 2.1.1 (Jun, 28th 2024)

Fix pypi release readme formatting

## 2.1.0 (Jun, 28th 2024)

Minimal conversion to pytest+hypothesis by @mgorny in #52
Added simple equality operator for class Symbol by @GregoirePelegrin in #55
jsondiff: fix symbol equality by @corytodd in #61
ci: add pytest workflow by @corytodd in #63
setup.py: migrate to pyproject.toml by @corytodd in #65
fix: better diffing of empty containers by @corytodd in #64
add rightonly jsondiff syntax by @ramwin in #60
Introduce YAML support by @corytodd in #67
packaging: revert to requirements files by @corytodd in #69
cli: handle deserialization errors by @corytodd in #72
ci: upload to pypi on github release by @corytodd in #77

## 2.0.0 (Apr, 10th 2022)

remove deprecated jsondiff entrypoint

## 1.3.1 (Jan 24th, 2022)

Optionally allow different escape_str than '$'
clarified the readme, closes #23

## 1.3.0 (Dec, 21st 2019)

Add license to setup.py
Refactor recursive list-diff helper method to be iterative

## v1.2.0 (Jun 23rd, 2019)

Deprecate the jsondiff command due to conflicts with json-patch

## v1.1.2 (Oct, 8th 2017)

README: disable incorrect syntax highlight for usage message
Maintaining consistency in checking type of object
make generate_readme.py compatible with python3

## v1.1.1 (Mar, 26th 2016)

Exclude tests from installation

## v1.1.0 (Dec, 5th 2016)

Added command line client

## v1.0.0 (Oct, 19th 2016)

Stable release

## v0.2.0 (Dec, 15th 2015)

Changed syntax

## v0.1.0 (Oct, 19th 2015)

First release