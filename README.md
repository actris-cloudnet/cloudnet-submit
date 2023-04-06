# ACTRIS Cloudnet data submission tool
![Tests](https://github.com/actris-cloudnet/cloudnet-submit/actions/workflows/tests.yml/badge.svg)

## Installation

### Linux/MacOS
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

This will generate a `cloudnet-config.toml` file in your working directory.



Update your submission credentials in the `user_account` section,
and update `site`, `instrument`, `instrument_pid` and `path_fmt` fields
to match your instrument/model setup. Remove unnecessary instrument and model sections.


```toml
# cloudnet-config.toml
[user_account]
username       = "alice"
password       = "alicesSecretPassword"

[[instrument]]
site           = "hyytiala"
instrument     = "rpg-fmcw-94"
instrument_pid = "https://hdl.handle.net/21.12132/3.191564170f8a4686"
path_fmt       = "/home/alice/data/hyytiala/rpg-fmcw-94/%Y/%m/%Y%m%d_hyytiala.nc"

[[instrument]]
# you can have additional sections for the same instrument
# e.g. for different path
site           = "hyytiala"
instrument     = "rpg-fmcw-94"
instrument_pid = "https://hdl.handle.net/21.12132/3.191564170f8a4686"
path_fmt       = "/home/another-path/data/hyytiala/rpg-fmcw-94/%Y/%m/%Y%m%d_hyytiala.nc"

[[instrument]]
site           = "granada"
instrument     = "chm15k"
path_fmt       = "/home/alice/data/granada/chm/%Y-%m/chm_grandada_%Y-%m-%d-*.nc"

[[model]]
site           = "hyytiala"
model          = "ecmwf"
path_fmt       = "/home/alice/data/hyytiala/ecmwf/%Y/%Y%m%d_hyytiala_ecmwf.nc"


# You can use proxies (optional)
[network.proxies]
http = "http://10.10.1.10:3128"
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
You can also use `--config` flag to define another location and name of the config file:
```sh
cloudnet-submit --config /path/to/your/config.toml
```

### Usage

By default, `cloudnet-submit` submits data from the past three days.

Use `--dry-run` to list files that would be submitted:
```sh
cloudnet-submit --dry-run
```

Submit data to the Cloudnet dataportal:
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
cloudnet-submit --date 2022-06-21 2022-05-1
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
