# ACTRIS Cloudnet data submission tool
![Tests](https://github.com/actris-cloudnet/cloudnet-submit/actions/workflows/tests.yml/badge.svg)

## Installation

```sh
pip install cloudnet-submit
```

## Getting started

Generate a configuration file:
```sh
cloudnet-submit-generate-config
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
site           = "granada"
instrument     = "chm15k"
path_fmt       = "/home/alice/data/granada/chm/%Y-%m/chm_grandada_%Y-%m-%d-*.nc"

[[model]]
site           = "hyytiala"
model          = "ecmwf"
path_fmt       = "/home/alice/data/hyytiala/ecmwf/%Y/%Y%m%d_hyytiala_ecmwf.nc"
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

By default, `cloudnet-submit` submits data from the past three days.

Use `--dry-run` to list files would be submitted:
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
