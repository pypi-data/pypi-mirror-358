# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopSoldItem:
    """
    A sold item when selling an item to a shop
    """
    _byte_size: int = 0
    _amount: int = None # type: ignore [assignment]
    _id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def amount(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._amount

    @amount.setter
    def amount(self, amount: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._amount = amount

    @property
    def id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._id = id

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopSoldItem") -> None:
        """
        Serializes an instance of `ShopSoldItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopSoldItem): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_int(data._amount)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopSoldItem":
        """
        Deserializes an instance of `ShopSoldItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopSoldItem: The data to serialize.
        """
        data: ShopSoldItem = ShopSoldItem()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._amount = reader.get_int()
            data._id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopSoldItem(byte_size={repr(self._byte_size)}, amount={repr(self._amount)}, id={repr(self._id)})"
