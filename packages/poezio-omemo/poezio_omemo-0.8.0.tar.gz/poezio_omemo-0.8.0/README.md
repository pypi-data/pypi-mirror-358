[![PyPI](https://img.shields.io/pypi/v/poezio-omemo.svg)](https://pypi.org/project/poezio-omemo/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/poezio-omemo.svg)](https://pypi.org/project/poezio-omemo/)

# poezio-omemo - OMEMO plugin for Poezio #


This is a [Poezio](https://poez.io) plugin providing OMEMO support.
It's distributed separately for licensing reasons.

This plugin is very much **alpha**.
It handles encryption and decryption of OMEMO messages, but doesn't display the encryption state of messages, and neither does it have a way to do manual trust management.

## OMEMO Protocol Version Support ##

Currently supports OMEMO in the `eu.siacs.conversations.axolotl` namespace.
Support for OMEMO in the `omemo:2` namespace will be added as soon as Slixmpp gains support for [XEP-0420: Stanza Content Encryption](https://xmpp.org/extensions/xep-0420.html).

## Trust ##

Internally supports both [Blind Trust Before Verification](https://gultsch.de/trust.html) and manual trust management, however the UI does not currently offer a way to manage trust manually.
This means that for now, all devices are always trusted blindly.

## Installation ##

#### Arch Linux (AUR) ####

Packages for Arch Linux are available on AUR:
- [poezio-omemo](https://aur.archlinux.org/packages/poezio-omemo>), or
- [poezio-omemo-git](https://aur.archlinux.org/packages/poezio-omemo-git)

#### Debian ####

A [Request for packaging](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1007175) has been posted, but so far, Debian has not packaged poezio-omemo yet..

#### Everything else (pip/uv) ####

For all other cases, the plugin can be installed and made available to Poezio by adding one of the following at the end of Poezio's `update.sh` script:

##### For the latest release: #####

```
uv pip install poezio-omemo
```

##### For the latest commit on the main branch: #####

```
uv pip install git+https://codeberg.org/poezio/poezio-omemo
```

##### For your local clone of this repository: #####

```
uv pip install /path/to/your/clone
```

After adding that line, you might have to create a local commit in your clone of Poezio using:

```
git add update.sh && git commit -m "Install poezio-omemo in update.sh"
```

You should now be able to use `./update.sh` and `./launch.sh` as usual.

## Common Issues ##

This plugin is **NOT** to be placed in the Poezio plugin folder, doing so may shadow the OMEMO library and render it inaccessible from Poezio.
This module declares itself via `pkg_resources` under the `poezio_plugins` group.

Other possible issues when loading the plugin may be that the OMEMO library is incorrectly setup.

In a Python interpreter:

```Python
>>> # Is the backend OMEMO library is reachable? (success: no error, no output)
>>> import omemo
>>> # Is poezio-omemo reachable? (success: no error, no output)
>>> import poezio_omemo
>>> # Is the module probably declared in plugin entries? (success: true)
>>> import pkg_resources
>>> "omemo" in map(lambda e: e.name, pkg_resources.iter_entry_points("poezio_plugins"))
```

If this doesn't yield any error and Poezio still can't load the plugin, try starting it with a debug file (`-d poezio.log`) and join our [channel](xmpp:poezio@muc.poez.io?join).

## Use in Poezio ##

Once installed (see the [Installation](#installation) section), you can add `omemo` in the `plugin_autoload` configuration.
See the [Poezio documentation](https://doc.poez.io/plugins/index.html#plugin-autoload) for more information about autoloading plugins.
To load it manually in Poezio, type `/load omemo`.

## Type Checks and Linting ##

poezio-omemo uses [mypy](http://mypy-lang.org/) for static type checks and both [pylint](https://pylint.pycqa.org/en/latest/) and [Flake8](https://flake8.pycqa.org/en/latest/) for linting. All checks can be run locally with the following commands:

```sh
$ pip install --upgrade .[lint]
$ mypy poezio_omemo/
$ pylint poezio_omemo/
$ flake8 poezio_omemo/
```

## Note on the Underlying OMEMO Library ##

The underlying library [python-omemo](https://github.com/Syndace/python-omemo) has not undergone any security audits.
If you have the knowledge, any help is welcome.

Please take this into consideration when using this library.
