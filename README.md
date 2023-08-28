# Cloudnet data submission tool
![Tests](https://github.com/actris-cloudnet/cloudnet-submit/actions/workflows/tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/cloudnet-submit.svg)](https://badge.fury.io/py/cloudnet-submit)

## Installation

### Linux/macOS
If you have `python` and `pip` installed (`python >= 3.8`),
run the command:
```sh
pip install cloudnet-submit
```

After that, you can use `cloudnet-submit` command to run the program.

### Windows
If you are using Windows Subsystem for Linux,
then the aforementioned Linux installation should work.

If you are using windows command prompt
and have `python` and `pip` installed,
you can install `cloudnet-submit` with `pip`:

```sh
pip install cloudnet-submit
```

Test if the `cloudnet-submit` command works:
```sh
cloudnet-submit --version
```

If not, you can use an alternative way to run the program:
```sh
python -m cloudnet_submit --version
```

## Getting started

### Configuration file

Generate a configuration file:
```sh
cloudnet-submit --generate-config
```

This will generate a file named `cloudnet-config.toml` in your working directory.

Update your submission credentials in the `user_account` section,
and update `site`, `instrument`, `instrument_pid` and `path_fmt` fields
to match your instrument/model setup. Remove unnecessary instrument and model sections.

You can find `instrument_pid`s from the
[list of instruments](https://instrumentdb.out.ocp.fmi.fi/).
If your instrument does not have one yet,
[fill the form](https://docs.google.com/forms/d/e/1FAIpQLSeY4nvAah-K5xPfF-VMhDbmmY9lq7BbtTDKTT9BZMqT7tC7zA/viewform)
first.


```toml
# cloudnet-config.toml
[user_account]
username       = "alice"
password       = "alicesSecretPassword"

[[instrument]]
site           = "hyytiala"
instrument     = "rpg-fmcw-94"
instrument_pid = "https://hdl.handle.net/21.12132/3.191564170f8a4686"
path_fmt       = "/data/hyytiala/rpg-fmcw-94/%Y/%m/%y%m%d_*_P10_ZEN.LV1"

[[instrument]]
# you can have additional sections for the same instrument
# e.g. for different path
site           = "hyytiala"
instrument     = "rpg-fmcw-94"
instrument_pid = "https://hdl.handle.net/21.12132/3.191564170f8a4686"
path_fmt       = "/home/alice/hyytiala/rpg-fmcw-94/%y%m%d_*_P09_ZEN.LV0"

[[instrument]]
site           = "granada"
instrument     = "chm15k"
instrument_pid = "https://hdl.handle.net/21.12132/3.77a75f3b32294855"
path_fmt       = "/data/granada/chm/%Y-%m/%Y%m%d_Granada_CHM170119_*.nc"

[[model]]
site           = "hyytiala"
model          = "ecmwf"
path_fmt       = "/data/hyytiala/ecmwf/%Y/%Y%m%d_hyytiala_ecmwf.nc"

# You can use proxies (optional)
[network.proxies]
http  = "http://10.10.1.10:3128"
https = "http://10.10.1.10:1080"
# Alternatively, You can define proxies as environment variables
# HTTP_PROXY and HTTPS_PROXY
# see: https://requests.readthedocs.io/en/latest/user/advanced/#proxies
```

`cloudnet-submit` will look for files specified in the `path_fmt` field
for a given measurement date.

Use the following format codes:

| Directive | Meaning                            |     Example     |
|-----------|------------------------------------|:---------------:|
| `%Y`      | Year with century                  | 0001, ..., 2022 |
| `%y`      | Year without century (zero-padded) |   00, ..., 22   |
| `%m`      | Month (zero-padded)                |   01, ..., 12   |
| `%d`      | Day (zero-padded)                  |   01, ..., 31   |

You can also use wildcard character `*` in `path_fmt` field.

By default, `cloudnet-submit` expects the `cloudnet-config.toml` file to be
in your working directory.
You can also use `--config` to specify another location for the config file:
```sh
cloudnet-submit --config /path/to/your/config.toml
```

### Usage

By default, `cloudnet-submit` submits data from the past three days.

Use `--dry-run` to list files that would be submitted:
```sh
cloudnet-submit --dry-run
```

Submit data to the Cloudnet data portal:
```sh
cloudnet-submit
```

You can also set the number of days to be submitted (including today):
```sh
cloudnet-submit --last-ndays 5
```

You can also specify a date you want to submit:
```sh
cloudnet-submit --date 2022-06-21
```

Or a list of dates:
```sh
cloudnet-submit --date 2022-06-21 2022-05-01
```

Or a range of dates:

```sh
cloudnet-submit --from-date 2022-05-01 --to-date 2022-06-24
```

See all the options:
```sh
cloudnet-submit --help
```

## Feedback and contact
- Bugs, feature requests, documentation: [Create an issue](https://github.com/actris-cloudnet/cloudnet-submit/issues/new/choose) on Github
- Or just [send us mail](mailto:actris-cloudnet@fmi.fi) :)
