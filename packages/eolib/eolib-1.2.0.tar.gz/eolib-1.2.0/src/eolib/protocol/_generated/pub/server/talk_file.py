# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .talk_record import TalkRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TalkFile:
    """
    Endless Talk File
    """
    _byte_size: int = 0
    _npcs: list[TalkRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def npcs(self) -> list[TalkRecord]:
        return self._npcs

    @npcs.setter
    def npcs(self, npcs: list[TalkRecord]) -> None:
        self._npcs = npcs

    @staticmethod
    def serialize(writer: EoWriter, data: "TalkFile") -> None:
        """
        Serializes an instance of `TalkFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TalkFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.add_fixed_string("ETF", 3, False)
            if data._npcs is None:
                raise SerializationError("npcs must be provided.")
            for i in range(len(data._npcs)):
                TalkRecord.serialize(writer, data._npcs[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TalkFile":
        """
        Deserializes an instance of `TalkFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TalkFile: The data to serialize.
        """
        data: TalkFile = TalkFile()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.get_fixed_string(3, False)
            data._npcs = []
            while reader.remaining > 0:
                data._npcs.append(TalkRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TalkFile(byte_size={repr(self._byte_size)}, npcs={repr(self._npcs)})"
