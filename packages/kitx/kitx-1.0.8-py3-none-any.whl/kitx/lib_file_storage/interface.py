import io
from abc import ABC, abstractmethod
from typing import Optional, Dict


class ObjectInterface(ABC):

    @abstractmethod
    def upload(self,
               file_path_name: str,
               bytes_io: io.BytesIO,
               length: Optional[int] = None,
               metadata: Optional[dict] = None,
               **kwargs) -> str:
        pass

    @abstractmethod
    def download(self, file_path_name: str):
        pass
