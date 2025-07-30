# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class Version:
    """
    Client version
    """
    _byte_size: int = 0
    _major: int = None # type: ignore [assignment]
    _minor: int = None # type: ignore [assignment]
    _patch: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def major(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._major

    @major.setter
    def major(self, major: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._major = major

    @property
    def minor(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._minor

    @minor.setter
    def minor(self, minor: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._minor = minor

    @property
    def patch(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._patch

    @patch.setter
    def patch(self, patch: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._patch = patch

    @staticmethod
    def serialize(writer: EoWriter, data: "Version") -> None:
        """
        Serializes an instance of `Version` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (Version): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._major is None:
                raise SerializationError("major must be provided.")
            writer.add_char(data._major)
            if data._minor is None:
                raise SerializationError("minor must be provided.")
            writer.add_char(data._minor)
            if data._patch is None:
                raise SerializationError("patch must be provided.")
            writer.add_char(data._patch)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "Version":
        """
        Deserializes an instance of `Version` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            Version: The data to serialize.
        """
        data: Version = Version()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._major = reader.get_char()
            data._minor = reader.get_char()
            data._patch = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"Version(byte_size={repr(self._byte_size)}, major={repr(self._major)}, minor={repr(self._minor)}, patch={repr(self._patch)})"
