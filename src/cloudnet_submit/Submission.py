from __future__ import annotations

import datetime
import hashlib
from dataclasses import dataclass
from pathlib import Path
from sys import stdout
from typing import Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .cfg import Dataportal as DataportalConfig
from .cfg import ProxyConfig

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
    metadata_msg: Union[str, None] = None
    data_msg: Union[str, None] = None
    proxies: ProxyConfig = ProxyConfig()


class Submission:
    def __init__(
        self,
        path: Path,
        metadata: Union[InstrumentMetadata, ModelMetadata],
        auth: tuple[str, str],
        proxies: ProxyConfig,
    ):
        self.path = path
        self.metadata = metadata
        self.auth = auth
        self.status = Status()
        self.session = make_session(proxies)

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
        path_dir = str(self.path.parent)
        return (
            f"{site:<10} {model_or_instrument:<15} "
            + f"{date:<12} file: {fname:<30}"
            + f"dir: {path_dir}"
        )

    def __str_dry__(self):
        return str(self)

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
                body["instrumentPid"] = self.metadata.instrument_pid
            url = DATAPORTAL.instrument.metadata_url
        else:
            body["model"] = self.metadata.model
            url = DATAPORTAL.model.metadata_url

        res = self.session.post(
            url, json=body, auth=self.auth, headers=DATAPORTAL.headers
        )
        self.status.metadata = res.status_code
        self.status.metadata_msg = res.text
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
                res = self.session.put(
                    url, data=data, auth=self.auth, headers=DATAPORTAL.headers
                )
            else:
                raise ValueError(f"{self}, missing checksum")
        self.status.data = res.status_code
        self.status.data_msg = res.text
        if res.ok:
            self.status.data_ok = True

    def print_status(self, end):
        meta = (
            str(self.status.metadata_msg)
            if self.status.metadata_msg is not None
            else "-"
        )
        data = (
            str(self.status.data_msg)
            if self.status.data_msg is not None
            else "-"
        )
        stdout.write(f"[meta: {meta} | data: {data}] {self}{end}")

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


def make_session(proxies: ProxyConfig) -> requests.Session:
    retries = Retry(total=10, backoff_factor=0.2)
    adapter = HTTPAdapter(max_retries=retries)
    session = requests.Session()
    session.proxies.update(proxies.asdict())
    session.mount("https://", adapter)
    return session


def compute_checksum(path: Path):
    BLOCK_SIZE = 512
    md5hash = hashlib.md5()
    with path.open("rb") as f:
        chunk = f.read(BLOCK_SIZE)
        while chunk:
            md5hash.update(chunk)
            chunk = f.read(BLOCK_SIZE)
    return md5hash.hexdigest()
