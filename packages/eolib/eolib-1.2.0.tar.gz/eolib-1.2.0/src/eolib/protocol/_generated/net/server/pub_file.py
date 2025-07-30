# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PubFile:
    """
    A pub file (EIF, ENF, ECF, ESF)
    """
    _byte_size: int = 0
    _file_id: int = None # type: ignore [assignment]
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
    def file_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._file_id

    @file_id.setter
    def file_id(self, file_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._file_id = file_id

    @property
    def content(self) -> bytes:
        return self._content

    @content.setter
    def content(self, content: bytes) -> None:
        self._content = content

    @staticmethod
    def serialize(writer: EoWriter, data: "PubFile") -> None:
        """
        Serializes an instance of `PubFile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PubFile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._file_id is None:
                raise SerializationError("file_id must be provided.")
            writer.add_char(data._file_id)
            if data._content is None:
                raise SerializationError("content must be provided.")
            writer.add_bytes(data._content)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PubFile":
        """
        Deserializes an instance of `PubFile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PubFile: The data to serialize.
        """
        data: PubFile = PubFile()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._file_id = reader.get_char()
            data._content = reader.get_bytes(reader.remaining)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PubFile(byte_size={repr(self._byte_size)}, file_id={repr(self._file_id)}, content={repr(self._content)})"
