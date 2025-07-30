# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .shop_record import ShopRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopFile:
    """
    Endless Shop File
    """
    _byte_size: int = 0
    _shops: list[ShopRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def shops(self) -> list[ShopRecord]:
        return self._shops

    @shops.setter
    def shops(self, shops: list[ShopRecord]) -> None:
        self._shops = shops

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopFile") -> None:
        """
        Serializes an instance of `ShopFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("ESF", 3, False)
            if data._shops is None:
                raise SerializationError("shops must be provided.")
            for i in range(len(data._shops)):
                ShopRecord.serialize(writer, data._shops[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopFile":
        """
        Deserializes an instance of `ShopFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopFile: The data to serialize.
        """
        data: ShopFile = ShopFile()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            data._shops = []
            while reader.remaining > 0:
                data._shops.append(ShopRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopFile(byte_size={repr(self._byte_size)}, shops={repr(self._shops)})"
