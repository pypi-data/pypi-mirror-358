# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class MapFile:
    """
    A map file (EMF)
    """
    _byte_size: int = 0
    _content: bytes = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def content(self) -> bytes:
        return self._content

    @content.setter
    def content(self, content: bytes) -> None:
        self._content = content

    @staticmethod
    def serialize(writer: EoWriter, data: "MapFile") -> None:
        """
        Serializes an instance of `MapFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._content is None:
                raise SerializationError("content must be provided.")
            writer.add_bytes(data._content)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapFile":
        """
        Deserializes an instance of `MapFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapFile: The data to serialize.
        """
        data: MapFile = MapFile()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._content = reader.get_bytes(reader.remaining)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapFile(byte_size={repr(self._byte_size)}, content={repr(self._content)})"
