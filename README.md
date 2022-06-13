# ACTRIS Cloudnet data submission tool
![Tests](https://github.com/actris-cloudnet/cloudnet-submit/actions/workflows/tests.yml/badge.svg)

## Installation

```sh
pip install cloudnet-submit
```

## Getting started

Generate a `config.toml` file
```sh
cloudnet-submit generate-config
```

Update your credentials and data configuration in the `config.toml` file:

```toml
[user_account]
username = "alice"
password = "alisSecretPassword"

[[instrument]]
site_id = "mace-head"
instrument="chm15k"
path_fmt = "/data/chm15k/%Y/data-%Y%m%d-*.{nc,NC}"
```

Submit today's data:
```sh
cloudnet-submit upload
```
