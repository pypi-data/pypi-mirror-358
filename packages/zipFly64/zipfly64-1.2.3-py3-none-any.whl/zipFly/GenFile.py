import time
from typing import Generator, AsyncGenerator, Union

from . import consts
from .BaseFile import BaseFile


class GenFile(BaseFile):
    """DO NOT REUSE GenFile instances!"""
    def __init__(self, name: str, generator: Union[Generator[bytes, None, None], AsyncGenerator[bytes, None]], compression_method: int = consts.NO_COMPRESSION, modification_time: float = None, size: int = None, crc: int = None):
        super().__init__(compression_method)
        self._name = name
        self._generator = generator
        self._size = size
        self._overriden_crc = crc  # used in byte offset mode
        self._modification_time = modification_time if modification_time else time.time()

    def _get_generator(self):
        return self._generator

    def _generate_file_data(self) -> Generator[bytes, None, None]:
        generator = self._get_generator()
        if isinstance(generator, Generator):
            yield from generator
        else:
            raise ValueError(f"generator must be of type Generator, not '{type(generator)}'")

    async def _async_generate_file_data(self) -> AsyncGenerator[bytes, None]:
        generator = self._get_generator()
        if isinstance(generator, AsyncGenerator):
            async for chunk in generator:
                yield chunk
        else:
            raise ValueError(f"generator must be of type AsyncGenerator, not '{type(generator)}'")

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        if self._size is not None:
            return self._size
        raise RuntimeError("Archive size not known before streaming. Probably GenFile() is missing size attribute.")

    @property
    def modification_time(self) -> float:
        return self._modification_time

    def set_file_name(self, new_name: str) -> None:
        self._name = new_name

    def calculate_crc(self) -> int:
        if self._overriden_crc:
            return self._overriden_crc
        raise ValueError("Crc must be explicitly set to allow for byte offset streaming!")
