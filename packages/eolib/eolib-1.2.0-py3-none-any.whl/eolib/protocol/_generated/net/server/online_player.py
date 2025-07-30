# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_icon import CharacterIcon
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class OnlinePlayer:
    """
    A player in the online list
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _title: str = None # type: ignore [assignment]
    _level: int = None # type: ignore [assignment]
    _icon: CharacterIcon = None # type: ignore [assignment]
    _class_id: int = None # type: ignore [assignment]
    _guild_tag: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str) -> None:
        self._title = title

    @property
    def level(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._level = level

    @property
    def icon(self) -> CharacterIcon:
        return self._icon

    @icon.setter
    def icon(self, icon: CharacterIcon) -> None:
        self._icon = icon

    @property
    def class_id(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._class_id

    @class_id.setter
    def class_id(self, class_id: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._class_id = class_id

    @property
    def guild_tag(self) -> str:
        return self._guild_tag

    @guild_tag.setter
    def guild_tag(self, guild_tag: str) -> None:
        self._guild_tag = guild_tag

    @staticmethod
    def serialize(writer: EoWriter, data: "OnlinePlayer") -> None:
        """
        Serializes an instance of `OnlinePlayer` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (OnlinePlayer): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._title is None:
                raise SerializationError("title must be provided.")
            writer.add_string(data._title)
            writer.add_byte(0xFF)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._icon is None:
                raise SerializationError("icon must be provided.")
            writer.add_char(int(data._icon))
            if data._class_id is None:
                raise SerializationError("class_id must be provided.")
            writer.add_char(data._class_id)
            if data._guild_tag is None:
                raise SerializationError("guild_tag must be provided.")
            writer.add_string(data._guild_tag)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "OnlinePlayer":
        """
        Deserializes an instance of `OnlinePlayer` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            OnlinePlayer: The data to serialize.
        """
        data: OnlinePlayer = OnlinePlayer()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._title = reader.get_string()
            reader.next_chunk()
            data._level = reader.get_char()
            data._icon = CharacterIcon(reader.get_char())
            data._class_id = reader.get_char()
            data._guild_tag = reader.get_string()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"OnlinePlayer(byte_size={repr(self._byte_size)}, name={repr(self._name)}, title={repr(self._title)}, level={repr(self._level)}, icon={repr(self._icon)}, class_id={repr(self._class_id)}, guild_tag={repr(self._guild_tag)})"
