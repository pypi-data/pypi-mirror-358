import os
import zlib
from pathlib import Path
from typing import Generator, AsyncGenerator, Union

import aiofiles

from . import consts
from .BaseFile import BaseFile


class LocalFile(BaseFile):
    def __init__(self, file_path: Union[str, Path], name: str = None, compression_method: int = consts.NO_COMPRESSION, chunk_size=None):
        file_path = Path(file_path)
        if not file_path.is_file():
            raise ValueError(f"{file_path} is not a correct file path.")

        self._file_path = str(file_path)
        self.chunk_size = chunk_size
        self._name = name if name else self._file_path
        super().__init__(compression_method)

    async def _async_generate_file_data(self) -> AsyncGenerator[bytes, None]:
        if not self.chunk_size:
            self.chunk_size = 1048 * 1048 * 4
        async with aiofiles.open(self._file_path, "rb") as fh:
            while True:
                part = await fh.read(self.chunk_size)
                if not part:
                    break
                yield part

    def _generate_file_data(self) -> Generator[bytes, None, None]:
        if not self.chunk_size:
            self.chunk_size = 1048 * 16

        with open(self._file_path, 'rb') as file:
            while True:
                chunk = file.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return os.path.getsize(self._file_path)

    @property
    def modification_time(self) -> float:
        """Returns the modification time as a Unix timestamp"""
        return os.path.getmtime(self._file_path)

    def set_file_name(self, new_name: str) -> None:
        self._name = new_name

    def calculate_crc(self) -> int:
        crc = 0
        with open(self._file_path, "rb") as f:
            while chunk := f.read(self.chunk_size):
                crc = zlib.crc32(chunk, crc)
        return crc & 0xFFFFFFFF
