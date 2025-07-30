# grebakker

[![License: GPL](https://img.shields.io/badge/License-GPL-green.svg)](https://github.com/dkrajzew/grebakker/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/grebakker.svg)](https://pypi.python.org/pypi/grebakker)
![test](https://github.com/dkrajzew/grebakker/actions/workflows/test.yml/badge.svg)
[![Downloads](https://pepy.tech/badge/grebakker)](https://pepy.tech/project/grebakker)
[![Downloads](https://static.pepy.tech/badge/grebakker/week)](https://pepy.tech/project/grebakker)
[![Coverage Status](https://coveralls.io/repos/github/dkrajzew/grebakker/badge.svg?branch=main)](https://coveralls.io/github/dkrajzew/grebakker?branch=main)
[![Documentation Status](https://readthedocs.org/projects/grebakker/badge/?version=latest)](https://grebakker.readthedocs.io/en/latest/?badge=latest)
[![Dependecies](https://img.shields.io/badge/dependencies-none-green)](https://img.shields.io/badge/dependencies-none-green)


[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=GVQQWZKB6FDES)

#

__grebakker__ - a backup solution for hackers (just for the acronym :-) )

## Introduction

__grebakker__ is a script that backups files and folders. __grebakker__ uses json to define what should be backupped and how - copied or compressed. The json files can reference each other. __grebakker__ does not need any external applications, libraries, or modules besides plain Python.

__grebakker__ is in a very early development stage. I use it successfully, but there are different things that should be streamlined. It (currently) only supports complete backups, no incremental backups etc. **I would be glad to get any feedback on or contribution to this.**


## Usage

Generate a backup definition of what to do in json and store it in the folder as ```grebakker.json```:

```js
{
    "destination": "d/",
    "copy": [ 
        "document.pdf",
        "old_backups"
    ],
    "compress": [
        "repository",
        { "name": "current", "exclude": ["venv"] }
    ],
    "subfolders": [ "attic" ]
}
```

Then run __grebakker__:

```cmd
python src\grebakker.py backup f:\backup\2025_05 d:\
```

That's all... Your files and folders are backupped to the subfolder ```d/``` of the ___destination folder___ ```f:\backup\2025_05``` - the file ```document.pdf``` and the folder ```old_backups``` are copied to the destination ```f:\backup\2025_05\d```, the folder ```repository``` and ```current``` are compressed (excluding the sub-folder ```venv``` in ```current```) and stored in ```f:\backup\2025_05\d``` as well. __grebakker__ continues with backupping using a backup definition stored in the sub-folder ```attic```.


## Documentation

__grebakker__ is meant to be run on the command line. The documentation consists of a [user manual](usage.md) and a [man-page like call documentation](cmd.md) (yet incomplete). The [glossary](glossary.md) may be of help.

If you want to contribute, you may check the [API documentation](api_grebakker.md) or visit [grebakker on github](https://github.com/dkrajzew/grebakker) where besides the code you may find the [grebakker issue tracker](https://github.com/dkrajzew/grebakker/issues) or [discussions about grebakker](https://github.com/dkrajzew/grebakker/discussions).

Additional documentation includes a page with relevant [links](links.md) or the [ChangeLog](changes.md).


## Installation

You may install the latest release using pip:

```console
python -m pip install grebakker
```

Or download the [latest release](https://github.com/dkrajzew/grebakker/releases/tag/0.2.0) from github. You may as well clone or download the [grebakker git repository](https://github.com/dkrajzew/grebakker.git). There is also a page about [installing grebakker](install.md) which lists further options.


## Changes

### Version 0.2.0 (24.06.2025)

* an initial version

The complete [ChangeLog](https://grebakker.readthedocs.io/en/latest/changes) is included in [the __grebakker__ documentation pages](https://grebakker.readthedocs.io/en/latest/).


## License

__grebakker__ is licensed under the [GPLv3](license.md).


## Background

I backup all my projects frequently. Being bored of doing it manually, I wrote __grebakker__ for doing it for me.


## Status &amp; Contributing

__grebakker__ is in an early development stage. I suppose I will extend it in the future, but I am not under pressure.

Let me know if you need something by [adding an issue](https://github.com/dkrajzew/grebakker/issues) or by dropping me a mail. I am very interested in opinions, ideas, etc.



