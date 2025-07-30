# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .ecf_record import EcfRecord
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Ecf:
    """
    Endless Class File
    """
    _byte_size: int = 0
    _rid: list[int] = None # type: ignore [assignment]
    _total_classes_count: int = None # type: ignore [assignment]
    _version: int = None # type: ignore [assignment]
    _classes: list[EcfRecord] = None # type: ignore [assignment]

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
    def total_classes_count(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._total_classes_count

    @total_classes_count.setter
    def total_classes_count(self, total_classes_count: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._total_classes_count = total_classes_count

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
    def classes(self) -> list[EcfRecord]:
        return self._classes

    @classes.setter
    def classes(self, classes: list[EcfRecord]) -> None:
        self._classes = classes

    @staticmethod
    def serialize(writer: EoWriter, data: "Ecf") -> None:
        """
        Serializes an instance of `Ecf` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Ecf): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("ECF", 3, False)
            if data._rid is None:
                raise SerializationError("rid must be provided.")
            if len(data._rid) != 2:
                raise SerializationError(f"Expected length of rid to be exactly 2, got {len(data._rid)}.")
            for i in range(2):
                writer.add_short(data._rid[i])
            if data._total_classes_count is None:
                raise SerializationError("total_classes_count must be provided.")
            writer.add_short(data._total_classes_count)
            if data._version is None:
                raise SerializationError("version must be provided.")
            writer.add_char(data._version)
            if data._classes is None:
                raise SerializationError("classes must be provided.")
            for i in range(len(data._classes)):
                EcfRecord.serialize(writer, data._classes[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Ecf":
        """
        Deserializes an instance of `Ecf` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Ecf: The data to serialize.
        """
        data: Ecf = Ecf()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            data._rid = []
            for i in range(2):
                data._rid.append(reader.get_short())
            data._total_classes_count = reader.get_short()
            data._version = reader.get_char()
            data._classes = []
            while reader.remaining > 0:
                data._classes.append(EcfRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Ecf(byte_size={repr(self._byte_size)}, rid={repr(self._rid)}, total_classes_count={repr(self._total_classes_count)}, version={repr(self._version)}, classes={repr(self._classes)})"
