from __future__ import annotations

import argparse
import datetime
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from platform import platform
from typing import Literal

import toml

from . import __version__
from .generate_config import generate_config

EXAMPLE_CONFIG_FNAME = "cloudnet-config-example.toml"
DEFAULT_CONFIG_FNAME = "cloudnet-config.toml"


class DataportalConfig:
    def __init__(self, base_url):
        self.base_url: str = base_url
        self.instrument = self.Instrument(self.base_url)
        self.model = self.Model(self.base_url)
        self.headers: dict[str, str] = {
            "User-Agent": f"cloudnet-submit/{__version__} ({platform()})"
        }

    def __str__(self) -> str:
        return f"DataportalConfig: base_url={self.base_url}"

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
    http: str | None = None
    https: str | None = None

    def asdict(self) -> dict:
        return asdict(self)


@dataclass
class InstrumentConfig:
    site: str
    instrument: str
    instrument_pid: str
    path_fmt: str
    tags: list[str] | None
    periodicity: Literal["daily", "monthly"]

    def __post_init__(self):
        _validate_path_fmt(self.periodicity, self.path_fmt)


@dataclass
class ModelConfig:
    site: str
    model: str
    path_fmt: str

    def __post_init__(self):
        _validate_path_fmt("daily", self.path_fmt)


@dataclass
class Config:
    user_account: UserAccountConfig
    dataportal_config: DataportalConfig
    proxy_config: ProxyConfig
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
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG_FNAME)
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-d", "--date", type=datetime.date.fromisoformat, nargs="*")
    parser.add_argument("-l", "--last-ndays", type=last_ndays_arg)
    parser.add_argument("--from-date", type=datetime.date.fromisoformat)
    parser.add_argument("--to-date", type=datetime.date.fromisoformat)
    parser.add_argument("--host", type=str, default="https://cloudnet.fmi.fi")
    parser.add_argument("--port", type=str)
    return parser.parse_args()


def last_ndays_arg(val):
    ndays = int(val)
    if ndays <= 0:
        raise argparse.ArgumentTypeError(f"# of days must be positive: {ndays}")
    return ndays


def get_config():
    args = get_args()
    if args.generate_config:
        generate_config(EXAMPLE_CONFIG_FNAME, args.config)
        sys.exit(0)

    path = Path(args.config)
    if not path.is_file():
        sys.stderr.write(f'"{path}" does not exist. Cannot read the configuration.\n')
        sys.exit(1)
    config_toml = toml.load(path)
    base_url = args.host + (f":{args.port}" if args.port else "")
    return Config(
        user_account=get_user_account_config(config_toml),
        dataportal_config=DataportalConfig(base_url=base_url),
        proxy_config=get_proxy_config(config_toml),
        instrument=get_instrument_config(config_toml),
        model=get_model_config(config_toml),
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
    if "instrument" not in config:
        return []
    instrument_configs = []
    for iconf in config["instrument"]:
        instrument_configs.append(
            InstrumentConfig(
                site=iconf["site"],
                instrument=iconf["instrument"],
                instrument_pid=iconf["instrument_pid"],
                path_fmt=iconf["path_fmt"],
                tags=iconf.get("tags", None),
                periodicity=iconf.get("periodicity", "daily"),
            )
        )
    return instrument_configs


def get_model_config(config) -> list[ModelConfig]:
    if "model" not in config:
        return []
    model_configs = []
    for mconf in config["model"]:
        model_configs.append(
            ModelConfig(
                site=mconf["site"],
                model=mconf["model"],
                path_fmt=mconf["path_fmt"],
            )
        )
    return model_configs


def get_dates(args) -> list[datetime.date]:
    today = datetime.datetime.now(tz=datetime.timezone.utc).date()
    one_day = datetime.timedelta(days=1)
    if all(
        a is None for a in [args.date, args.from_date, args.to_date, args.last_ndays]
    ):
        last_three_days = [today - i * one_day for i in range(3)]
        return last_three_days
    dates = set()
    # Dates from --date argument
    for date in args.date if args.date else []:
        dates.add(date)
    # Date range from --from-date --to-date arguments
    if not (args.from_date is None and args.to_date is None):
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


def _validate_path_fmt(periodicity: Literal["daily", "monthly"], path_fmt: str) -> None:
    used = set(re.findall("%[a-z]", path_fmt, re.I))
    year = {"%Y", "%y"}
    month = {"%m"}
    day = {"%d"}
    required: tuple
    if periodicity == "daily":
        required = (year, month, day)
    elif periodicity == "monthly":
        required = (year, month)
    else:
        raise ValueError(f"Invalid periodicity: {periodicity}")
    invalid = used
    for req in required:
        if not used & req:
            lst = " or ".join(req)
            raise ValueError(f"path_fmt '{path_fmt}' must contain {lst}")
        invalid -= req
    if invalid:
        plural = "s" if len(invalid) != 1 else ""
        lst = ", ".join(invalid)
        raise ValueError(f"Unsupported directive{plural} in path_fmt: {lst}")
