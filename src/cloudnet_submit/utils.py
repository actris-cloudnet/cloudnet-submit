import datetime
import glob
import itertools
from pathlib import Path
from typing import List

from .cfg import Config
from .submission import InstrumentMetadata, ModelMetadata, Submission


def get_files(date: datetime.date, path_fmt: str) -> List[Path]:
    files: List[Path] = []
    for path_ in glob.glob(date.strftime(path_fmt)):
        path = Path(path_)
        if path.is_file():
            files.append(path)
    return files


def get_submissions(config: Config) -> List[Submission]:
    submissions: List[Submission] = []
    auth = (config.user_account.username, config.user_account.password)
    for date, iconf in itertools.product(config.dates, config.instrument):
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
