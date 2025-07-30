# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .inn_record import InnRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class InnFile:
    """
    Endless Inn File
    """
    _byte_size: int = 0
    _inns: list[InnRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def inns(self) -> list[InnRecord]:
        return self._inns

    @inns.setter
    def inns(self, inns: list[InnRecord]) -> None:
        self._inns = inns

    @staticmethod
    def serialize(writer: EoWriter, data: "InnFile") -> None:
        """
        Serializes an instance of `InnFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (InnFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("EID", 3, False)
            if data._inns is None:
                raise SerializationError("inns must be provided.")
            for i in range(len(data._inns)):
                InnRecord.serialize(writer, data._inns[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "InnFile":
        """
        Deserializes an instance of `InnFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            InnFile: The data to serialize.
        """
        data: InnFile = InnFile()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            data._inns = []
            while reader.remaining > 0:
                data._inns.append(InnRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"InnFile(byte_size={repr(self._byte_size)}, inns={repr(self._inns)})"
