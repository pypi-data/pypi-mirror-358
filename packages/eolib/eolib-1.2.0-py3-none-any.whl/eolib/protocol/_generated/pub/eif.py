# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .eif_record import EifRecord
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Eif:
    """
    Endless Item File
    """
    _byte_size: int = 0
    _rid: list[int] = None # type: ignore [assignment]
    _total_items_count: int = None # type: ignore [assignment]
    _version: int = None # type: ignore [assignment]
    _items: list[EifRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rid(self) -> list[int]:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        return self._rid

    @rid.setter
    def rid(self, rid: list[int]) -> None:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        self._rid = rid

    @property
    def total_items_count(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._total_items_count

    @total_items_count.setter
    def total_items_count(self, total_items_count: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._total_items_count = total_items_count

    @property
    def version(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._version

    @version.setter
    def version(self, version: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._version = version

    @property
    def items(self) -> list[EifRecord]:
        return self._items

    @items.setter
    def items(self, items: list[EifRecord]) -> None:
        self._items = items

    @staticmethod
    def serialize(writer: EoWriter, data: "Eif") -> None:
        """
        Serializes an instance of `Eif` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Eif): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("EIF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._total_items_count is None:
                raise SerializationError("total_items_count must be provided.")
            writer.add_short(data._total_items_count)
            if data._version is None:
                raise SerializationError("version must be provided.")
            writer.add_char(data._version)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                EifRecord.serialize(writer, data._items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Eif":
        """
        Deserializes an instance of `Eif` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Eif: The data to serialize.
        """
        data: Eif = Eif()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            data._rid = []
            for i in range(2):
                data._rid.append(reader.get_short())
            data._total_items_count = reader.get_short()
            data._version = reader.get_char()
            data._items = []
            while reader.remaining > 0:
                data._items.append(EifRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Eif(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, total_items_count={repr(self._total_items_count)}, version={repr(self._version)}, items={repr(self._items)})"
