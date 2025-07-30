# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class BoardPostListing:
    """
    An entry in the list of town board posts
    """
    _byte_size: int = 0
    _post_id: int = None # type: ignore [assignment]
    _author: str = None # type: ignore [assignment]
    _subject: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def post_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._post_id

    @post_id.setter
    def post_id(self, post_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._post_id = post_id

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, author: str) -> None:
        self._author = author

    @property
    def subject(self) -> str:
        return self._subject

    @subject.setter
    def subject(self, subject: str) -> None:
        self._subject = subject

    @staticmethod
    def serialize(writer: EoWriter, data: "BoardPostListing") -> None:
        """
        Serializes an instance of `BoardPostListing` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (BoardPostListing): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._post_id is None:
                raise SerializationError("post_id must be provided.")
            writer.add_short(data._post_id)
            writer.add_byte(0xFF)
            if data._author is None:
                raise SerializationError("author must be provided.")
            writer.add_string(data._author)
            writer.add_byte(0xFF)
            if data._subject is None:
                raise SerializationError("subject must be provided.")
            writer.add_string(data._subject)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "BoardPostListing":
        """
        Deserializes an instance of `BoardPostListing` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            BoardPostListing: The data to serialize.
        """
        data: BoardPostListing = BoardPostListing()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._post_id = reader.get_short()
            reader.next_chunk()
            data._author = reader.get_string()
            reader.next_chunk()
            data._subject = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"BoardPostListing(byte_size={repr(self._byte_size)}, post_id={repr(self._post_id)}, author={repr(self._author)}, subject={repr(self._subject)})"
