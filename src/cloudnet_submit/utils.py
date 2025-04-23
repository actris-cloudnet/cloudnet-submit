import datetime
import glob
import itertools
from pathlib import Path
from typing import List

from braceexpand import braceexpand

from .cfg import Config
from .submission import InstrumentMetadata, ModelMetadata, Submission


def get_files(date: datetime.date, path_fmt: str) -> List[Path]:
    files: List[Path] = []
    for pattern in braceexpand(date.strftime(path_fmt)):
        for path_str in glob.glob(pattern):
            path = Path(path_str)
            if path.is_file():
                files.append(path)
    return files


def get_submissions(config: Config) -> List[Submission]:
    submissions: List[Submission] = []
    auth = (config.user_account.username, config.user_account.password)
    for date, iconf in itertools.product(config.dates, config.instrument):
        if iconf.periodicity != "daily":
            continue
        for f in get_files(date, iconf.path_fmt):
            metadata_instrument = InstrumentMetadata(
                site=iconf.site,
                measurement_date=date,
                filename=f.name,
                checksum=None,
                instrument=iconf.instrument,
                instrument_pid=iconf.instrument_pid,
                tags=iconf.tags,
            )
            submissions.append(
                Submission(
                    path=f,
                    metadata=metadata_instrument,
                    auth=auth,
                    dataportal_config=config.dataportal_config,
                    proxy_config=config.proxy_config,
                )
            )

    months = set(date.replace(day=1) for date in config.dates)
    for date, iconf in itertools.product(months, config.instrument):
        if iconf.periodicity != "monthly":
            continue
        for f in get_files(date, iconf.path_fmt):
            metadata_instrument = InstrumentMetadata(
                site=iconf.site,
                measurement_date=date,
                filename=f.name,
                checksum=None,
                instrument=iconf.instrument,
                instrument_pid=iconf.instrument_pid,
                tags=iconf.tags,
            )
            submissions.append(
                Submission(
                    path=f,
                    metadata=metadata_instrument,
                    auth=auth,
                    dataportal_config=config.dataportal_config,
                    proxy_config=config.proxy_config,
                )
            )

    for date, mconf in itertools.product(config.dates, config.model):
        for f in get_files(date, mconf.path_fmt):
            metadata_model = ModelMetadata(
                site=mconf.site,
                measurement_date=date,
                filename=f.name,
                checksum=None,
                model=mconf.model,
            )
            submissions.append(
                Submission(
                    path=f,
                    metadata=metadata_model,
                    auth=auth,
                    dataportal_config=config.dataportal_config,
                    proxy_config=config.proxy_config,
                )
            )

    return submissions


def print_summary(submissions: List[Submission], dry_run: bool):
    n_files = 0
    n_fail = 0
    dates = set()
    for sub in submissions:
        if dry_run or (sub.status.metadata_ok and sub.status.data_ok):
            n_files += 1
            dates.add(sub.metadata.measurement_date)
        else:
            n_fail += 1
    n_dates = len(dates)
    file_noun = "file" if n_files == 1 else "files"
    date_noun = "date" if n_dates == 1 else "dates"
    print("")
    if dry_run:
        print(f"Would submit {n_files} {file_noun} to {n_dates} {date_noun}.")
    elif n_files > 0:
        print(f"Submitted {n_files} {file_noun} successfully to {n_dates} {date_noun}.")
    elif n_fail == 0:
        print("No files to submit.")
    if n_fail > 0:
        fail_noun = "file" if n_fail == 1 else "files"
        print(
            f"Failed to submit {n_fail} {fail_noun}. Please check your configuration!"
        )
