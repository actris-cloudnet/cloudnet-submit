from __future__ import annotations

import argparse
import datetime
from dataclasses import dataclass
from pathlib import Path
from sys import stderr

import toml

from .utils import date_parser


@dataclass
class UserAccountConfig:
    username: str
    password: str


@dataclass
class InstrumentConfig:
    site: str
    instrument: str
    path_fmt: str


@dataclass
class ModelConfig:
    site: str
    model: str
    path_fmt: str


@dataclass
class Config:
    user_account: UserAccountConfig
    instrument: list[InstrumentConfig]
    model: list[ModelConfig]
    dry_run: bool
    dates: list[datetime.date]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", type=str, default="cloudnet-config.toml"
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
    return Config(
        user_account=user_conf,
        instrument=instrument_conf,
        model=model_conf,
        dry_run=args.dry_run,
        dates=get_dates(args),
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
    if all(
        [
            a is None
            for a in [args.date, args.from_date, args.to_date, args.last_ndays]
        ]
    ):
        return [today]
    dates = set()
    # Dates from --date argument
    for date in args.date if args.date else []:
        dates.add(date)
    # Date range from --from-date --to-date arguments
    to_date = args.to_date if args.to_date else today
    from_date = args.from_date if args.from_date else min(to_date, today)
    one_day = datetime.timedelta(days=1)
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
