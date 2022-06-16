from platform import platform
from typing import Dict

from . import __version__


class Clu:
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
