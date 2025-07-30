# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class DialogQuestEntry:
    """
    An entry in the quest switcher
    """
    _byte_size: int = 0
    _quest_id: int = None # type: ignore [assignment]
    _quest_name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def quest_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._quest_id

    @quest_id.setter
    def quest_id(self, quest_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._quest_id = quest_id

    @property
    def quest_name(self) -> str:
        return self._quest_name

    @quest_name.setter
    def quest_name(self, quest_name: str) -> None:
        self._quest_name = quest_name

    @staticmethod
    def serialize(writer: EoWriter, data: "DialogQuestEntry") -> None:
        """
        Serializes an instance of `DialogQuestEntry` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (DialogQuestEntry): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._quest_id is None:
                raise SerializationError("quest_id must be provided.")
            writer.add_short(data._quest_id)
            if data._quest_name is None:
                raise SerializationError("quest_name must be provided.")
            writer.add_string(data._quest_name)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "DialogQuestEntry":
        """
        Deserializes an instance of `DialogQuestEntry` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            DialogQuestEntry: The data to serialize.
        """
        data: DialogQuestEntry = DialogQuestEntry()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._quest_id = reader.get_short()
            data._quest_name = reader.get_string()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"DialogQuestEntry(byte_size={repr(self._byte_size)}, quest_id={repr(self._quest_id)}, quest_name={repr(self._quest_name)})"
