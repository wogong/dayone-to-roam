# Day One to Roam Research

This is a simple exporter script for `DayOne.app (Version 2)`.

Each entry in `journal_name.json` will be exported as Roam Research pages.

## Requirements

Currently, the script runs with Python3.6, and is tested on macOS and Ubuntu 16.04.

* Python 3.6 or higher.
    * You may need Homebrew, Anaconda, or pyenv to use the latest version of python.
* Python packages
    * See requirements.txt

## Install

Just copy `dayone-to-roam.py` to somewhere, or clone this repository.

```sh
$ git clone https://github.com/wogong/dayone-to-roam
$ cd dayone-to-roam
```

## Usage

- Your journal file should be exported by DayOne.app as 'JSON in Zip' and extracted into certain directory, for example:

```sh
<some_dir>
    -- journal_name.json        JSON file exported from DayOne.app
```
- Define `EMAIL` and `HEADLINE` in dayone-to-roam.py

- Then run this script from your terminal.

```sh
# Show help (long-form only)
$ python dayone-to-roam.py --help
    Usage: dayone2md.py JSONPATH

    Convert *.json exported by DayOne2.app to Roam Research

    Options:
    --help       Show this message and exit.

# Convert
$ python dayone-to-roam.py export_dir/Journal.json
```

## Note

1. This repository is modified from [dayone2md](https://github.com/tuxedocat/dayone2md)
2. Roam Research json format details see [here](https://roamresearch.com/#/app/help/page/RxZF78p60)
3. I don't handle the dayone journal metadata except create and update time, while other metadata can be handled easily.
4. Note that every journal item in Day One will be imported as Daily Notes in Roam Research, with content under HEADLINE as you defined before.
