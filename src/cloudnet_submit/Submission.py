from __future__ import annotations

import datetime
import glob
import itertools
from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from typing import Union

import requests

from .configuration import Config
from .utils import compute_checksum


@dataclass
class Clu:
    metadata_url: str = "https://cloudnet.fmi.fi/upload/metadata/"
    data_url_base: str = "https://cloudnet.fmi.fi/upload/data/"

    def data_url(self, checksum: str) -> str:
        return f"{self.data_url_base}{checksum}"


CLU = Clu()


@dataclass
class Metadata:
    site: str
    measurement_date: datetime.date
    filename: str
    checksum: Union[str, None]


@dataclass
class InstrumentMetadata(Metadata):
    instrument: str


@dataclass
class ModelMetadata(Metadata):
    model: str


@dataclass
class Status:
    metadata_uploaded: bool = False
    metadata_submission_status: Union[int, None] = None
    data_uploaded: bool = False
    data_submission_status: Union[int, None] = None


class Submission:
    def __init__(
        self,
        path: Path,
        metadata: Union[InstrumentMetadata, ModelMetadata],
        auth: tuple[str, str],
    ):
        self.path = path
        self.metadata = metadata
        self.auth = auth
        self.status = Status()

    def __gt__(self, other):
        return (self.metadata.measurement_date, self.metadata.site) > (
            other.metadata.measurement_date,
            other.metadata.site,
        )

    def __str__(self):
        if isinstance(self.metadata, InstrumentMetadata):
            model_or_instrument = self.metadata.instrument
        else:
            model_or_instrument = self.metadata.model
        site = self.metadata.site
        date = str(self.metadata.measurement_date)
        fname = self.metadata.filename
        checksum_str = (
            self.metadata.checksum
            if self.metadata.checksum
            else "checksum-not-computed"
        )
        return (
            f"{site:<10} {model_or_instrument:<10} "
            + f"{date: <15} {fname:<30} {checksum_str}"
        )

    def compute_checksum(self):
        if self.metadata.checksum is None:
            self.metadata.checksum = compute_checksum(self.path)
        if self.metadata.checksum is None:
            raise ValueError(f"Checksum for {self.path} is None")

    def submit_metadata(self):
        self.compute_checksum()
        body = {
            "site": self.metadata.site,
            "filename": self.metadata.filename,
            "measurementDate": self.metadata.measurement_date.isoformat(),
            "checksum": self.metadata.checksum,
        }
        if isinstance(self.metadata, InstrumentMetadata):
            body["instrument"] = self.metadata.instrument
        else:
            body["model"] = self.metadata.model

        res = requests.post(CLU.metadata_url, json=body, auth=self.auth)
        self.status.metadata_submission_status = res.status_code
        if res.ok:
            self.status.metadata_uploaded = True

    def submit_data(self):
        with self.path.open("rb") as data:
            if isinstance(self.metadata.checksum, str):
                url = CLU.data_url(self.metadata.checksum)
                res = requests.put(f"{url}", data=data, auth=self.auth)
            else:
                raise ValueError(f"{self}, missing checksum")
        self.status.data_submission_status = res.status_code
        if res.ok:
            self.status.data_uploaded = True

    def submit(self):
        import time

        stdout.write(f"Submitting metadata: {self}\r")
        time.sleep(1)
        self.submit_metadata()
        if self.status.metadata_uploaded:
            self.submit_data()
        else:
            stdout.write(f"Failed to submit metadata: {self}\n")

    def dry_run(self):
        stdout.write(f"DRY-RUN: {self}\n")


def get_submissions(config: Config) -> list[Submission]:
    submissions: list[Submission] = []
    auth = (config.user_account.username, config.user_account.password)
    for date, iconf in itertools.product(config.dates, config.instrument):
        for f in get_files(date, iconf.path_fmt):
            metadata_instrument = InstrumentMetadata(
                site=iconf.site,
                measurement_date=date,
                filename=f.name,
                checksum=None,
                instrument=iconf.instrument,
            )
            submissions.append(
                Submission(path=f, metadata=metadata_instrument, auth=auth)
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
                Submission(path=f, metadata=metadata_model, auth=auth)
            )

    return submissions


def get_files(date: datetime.date, path_fmt: str) -> list[Path]:
    files: list[Path] = []
    for p in glob.glob(date.strftime(path_fmt)):
        path = Path(p)
        if path.is_file():
            files.append(path)
    return files
