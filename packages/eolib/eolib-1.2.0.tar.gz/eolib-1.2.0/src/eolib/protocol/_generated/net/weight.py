# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Weight:
    """
    Current carry weight and maximum carry capacity of a player
    """
    _byte_size: int = 0
    _current: int = None # type: ignore [assignment]
    _max: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def current(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._current

    @current.setter
    def current(self, current: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._current = current

    @property
    def max(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._max

    @max.setter
    def max(self, max: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._max = max

    @staticmethod
    def serialize(writer: EoWriter, data: "Weight") -> None:
        """
        Serializes an instance of `Weight` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Weight): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._current is None:
                raise SerializationError("current must be provided.")
            writer.add_char(data._current)
            if data._max is None:
                raise SerializationError("max must be provided.")
            writer.add_char(data._max)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Weight":
        """
        Deserializes an instance of `Weight` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Weight: The data to serialize.
        """
        data: Weight = Weight()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._current = reader.get_char()
            data._max = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Weight(byte_size={repr(self._byte_size)}, current={repr(self._current)}, max={repr(self._max)})"
