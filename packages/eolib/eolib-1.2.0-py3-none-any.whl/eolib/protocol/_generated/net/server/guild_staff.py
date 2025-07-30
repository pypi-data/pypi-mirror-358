# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildStaff:
    """
    Information about a guild staff member (recruiter or leader)
    """
    _byte_size: int = 0
    _rank: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def rank(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._rank

    @rank.setter
    def rank(self, rank: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._rank = rank

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildStaff") -> None:
        """
        Serializes an instance of `GuildStaff` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildStaff): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._rank is None:
                raise SerializationError("rank must be provided.")
            writer.add_char(data._rank)
            writer.add_byte(0xFF)
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildStaff":
        """
        Deserializes an instance of `GuildStaff` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildStaff: The data to serialize.
        """
        data: GuildStaff = GuildStaff()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._rank = reader.get_char()
            reader.next_chunk()
            data._name = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildStaff(byte_size={repr(self._byte_size)}, rank={repr(self._rank)}, name={repr(self._name)})"
