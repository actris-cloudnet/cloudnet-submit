from __future__ import annotations

import datetime
import hashlib
from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from typing import Union

import requests

from .cfg import Dataportal as DataportalConfig

DATAPORTAL = DataportalConfig()


@dataclass
class Metadata:
    site: str
    measurement_date: datetime.date
    filename: str
    checksum: Union[str, None]


@dataclass
class InstrumentMetadata(Metadata):
    instrument: str
    instrument_pid: Union[str, None]


@dataclass
class ModelMetadata(Metadata):
    model: str


@dataclass
class Status:
    metadata_ok: bool = False
    data_ok: bool = False
    metadata: Union[int, None] = None
    data: Union[int, None] = None


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
        model_or_instrument = self.get_model_or_instrument()
        site = self.metadata.site
        date = str(self.metadata.measurement_date)
        fname = self.metadata.filename
        return (
            f"{site:<10} {model_or_instrument:<15} "
            + f"{date:<15} {fname:<30}"
        )

    def __str_dry__(self):
        model_or_instrument = self.get_model_or_instrument()
        site = self.metadata.site
        date = str(self.metadata.measurement_date)
        return f"{site:<10} {model_or_instrument:<15} {date:<15} {self.path}"

    def get_model_or_instrument(self) -> str:
        if isinstance(self.metadata, InstrumentMetadata):
            return self.metadata.instrument
        else:
            return self.metadata.model

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
            if isinstance(self.metadata.instrument_pid, str):
                body["instrument_pid"] = self.metadata.instrument_pid
            url = DATAPORTAL.instrument.metadata_url
        else:
            body["model"] = self.metadata.model
            url = DATAPORTAL.model.metadata_url

        res = requests.post(
            url, json=body, auth=self.auth, headers=DATAPORTAL.headers
        )
        self.status.metadata = res.status_code
        if res.ok:
            self.status.metadata_ok = True

    def submit_data(self):
        with self.path.open("rb") as data:
            if isinstance(self.metadata.checksum, str):
                checksum = self.metadata.checksum
                url = (
                    DATAPORTAL.instrument.data_url(checksum)
                    if isinstance(self.metadata, InstrumentMetadata)
                    else DATAPORTAL.model.data_url(checksum)
                )
                res = requests.put(
                    url, data=data, auth=self.auth, headers=DATAPORTAL.headers
                )
            else:
                raise ValueError(f"{self}, missing checksum")
        self.status.data = res.status_code
        if res.ok:
            self.status.data_ok = True

    def print_status(self, ret):
        meta = (
            str(self.status.metadata)
            if self.status.metadata is not None
            else "-"
        )
        data = str(self.status.data) if self.status.data is not None else "-"
        stdout.write(f"[metadata: {meta:<3} data: {data:<3}] {self}{ret}")

    def submit(self):
        self.print_status("\r")
        self.submit_metadata()
        self.print_status("\r")
        if self.status.metadata_ok:
            self.submit_data()
        self.print_status("\n")

    def dry_run(self):
        info_str = self.__str_dry__()
        stdout.write(f"{info_str}\n")


def compute_checksum(path: Path):
    BLOCK_SIZE = 512
    md5hash = hashlib.md5()
    with path.open("rb") as f:
        chunk = f.read(BLOCK_SIZE)
        while chunk:
            md5hash.update(chunk)
            chunk = f.read(BLOCK_SIZE)
    return md5hash.hexdigest()
