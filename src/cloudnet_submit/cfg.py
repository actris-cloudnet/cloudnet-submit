from __future__ import annotations

import argparse
import datetime
from dataclasses import asdict, dataclass
from pathlib import Path
from platform import platform
from sys import stderr
from typing import Dict, Union

import toml

from . import __version__
from .dateutils import date_parser
from .generate_config import generate_config

example_config_fname = "cloudnet-config-example.toml"
default_config_fname = "cloudnet-config.toml"


class Dataportal:
    def __init__(self, base_url: str = "https://cloudnet.fmi.fi"):
        self.base_url: str = base_url
        self.instrument = self.Instrument(self.base_url)
        self.model = self.Model(self.base_url)
        self.headers: Dict[str, str] = {
            "User-Agent": f"cloudnet-submit/{__version__} ({platform()})"
        }

    class Instrument:
        def __init__(self, base_url: str):
            self.base_url: str = base_url
            self.metadata_url: str = f"{self.base_url}/upload/metadata"

        def data_url(self, checksum: str) -> str:
            return f"{self.base_url}/upload/data/{checksum}"

    class Model:
        def __init__(self, base_url: str):
            self.base_url: str = base_url
            self.metadata_url: str = f"{self.base_url}/model-upload/metadata"

        def data_url(self, checksum: str) -> str:
            return f"{self.base_url}/model-upload/data/{checksum}"


@dataclass
class UserAccountConfig:
    username: str
    password: str


@dataclass
class ProxyConfig:
    http: Union[str, None] = None
    https: Union[str, None] = None

    def asdict(self) -> dict:
        return asdict(self)


@dataclass
class InstrumentConfig:
    site: str
    instrument: str
    instrument_pid: Union[str, None]
    path_fmt: str


@dataclass
class ModelConfig:
    site: str
    model: str
    path_fmt: str


@dataclass
class Config:
    user_account: UserAccountConfig
    proxies: ProxyConfig
    instrument: list[InstrumentConfig]
    model: list[ModelConfig]
    dry_run: bool
    dates: list[datetime.date]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--generate-config", action="store_true")
    parser.add_argument(
        "-c", "--config", type=str, default=default_config_fname
    )
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-d", "--date", type=date_parser, nargs="*")
    parser.add_argument("-l", "--last-ndays", type=last_ndays_arg)
    parser.add_argument("--from-date", type=date_parser)
    parser.add_argument("--to-date", type=date_parser)
    return parser.parse_args()


def last_ndays_arg(val):
    ndays = int(val)
    if ndays <= 0:
        raise argparse.ArgumentTypeError(
            f"# of days must be positive: {ndays}"
        )
    return ndays


def get_config():
    args = get_args()
    if args.generate_config:
        generate_config(example_config_fname, args.config)
        exit(0)

    path = Path(args.config)
    if not path.is_file():
        stderr.write(
            f'"{path}" does not exist. Cannot read the configuration.\n'
        )
        exit(1)
    config = toml.load(path)
    user_conf = get_user_account_config(config)
    instrument_conf = get_instrument_config(config)
    model_conf = get_model_config(config)
    proxy_conf = get_proxy_config(config)
    print(proxy_conf)
    return Config(
        user_account=user_conf,
        proxies=proxy_conf,
        instrument=instrument_conf,
        model=model_conf,
        dry_run=args.dry_run,
        dates=get_dates(args),
    )


def get_proxy_config(config) -> ProxyConfig:
    proxies = config.get("network", {}).get("proxies", {})
    return ProxyConfig(
        http=proxies.get("http", None),
        https=proxies.get("https", None),
    )


def get_user_account_config(config) -> UserAccountConfig:
    return UserAccountConfig(
        username=config["user_account"]["username"],
        password=config["user_account"]["password"],
    )


def get_instrument_config(config) -> list[InstrumentConfig]:
    instrument_configs = []
    for iconf in config["instrument"] if "instrument" in config else []:
        instrument_configs.append(
            InstrumentConfig(
                site=iconf["site"],
                instrument=iconf["instrument"],
                instrument_pid=(
                    iconf["instrument_pid"]
                    if "instrument_pid" in iconf
                    else None
                ),
                path_fmt=iconf["path_fmt"],
            )
        )
    return instrument_configs


def get_model_config(config) -> list[ModelConfig]:
    model_configs = []
    for mconf in config["model"] if "model" in config else []:
        model_configs.append(
            ModelConfig(
                site=mconf["site"],
                model=mconf["model"],
                path_fmt=mconf["path_fmt"],
            )
        )
    return model_configs


def get_dates(args) -> list[datetime.date]:
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)
    if all(
        [
            a is None
            for a in [args.date, args.from_date, args.to_date, args.last_ndays]
        ]
    ):
        last_three_days = [today - i * one_day for i in range(3)]
        return last_three_days
    dates = set()
    # Dates from --date argument
    for date in args.date if args.date else []:
        dates.add(date)
    # Date range from --from-date --to-date arguments
    to_date = args.to_date if args.to_date else today
    from_date = args.from_date if args.from_date else min(to_date, today)
    idate = from_date
    while idate <= to_date:
        dates.add(idate)
        idate += one_day
    # Dates from --last-ndays argument
    if args.last_ndays:
        idate = today - datetime.timedelta(days=args.last_ndays - 1)
        while idate <= today:
            dates.add(idate)
            idate += one_day
    non_future_dates = [date for date in dates if date <= today]
    return sorted(non_future_dates)
