# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .equipment_character_select import EquipmentCharacterSelect
from ...gender import Gender
from ...admin_level import AdminLevel
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterSelectionListEntry:
    """
    Character selection screen character
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _id: int = None # type: ignore [assignment]
    _level: int = None # type: ignore [assignment]
    _gender: Gender = None # type: ignore [assignment]
    _hair_style: int = None # type: ignore [assignment]
    _hair_color: int = None # type: ignore [assignment]
    _skin: int = None # type: ignore [assignment]
    _admin: AdminLevel = None # type: ignore [assignment]
    _equipment: EquipmentCharacterSelect = None # type: ignore [assignment]

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
    def id(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._id = id

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
    def gender(self) -> Gender:
        return self._gender

    @gender.setter
    def gender(self, gender: Gender) -> None:
        self._gender = gender

    @property
    def hair_style(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hair_style

    @hair_style.setter
    def hair_style(self, hair_style: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hair_style = hair_style

    @property
    def hair_color(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hair_color

    @hair_color.setter
    def hair_color(self, hair_color: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hair_color = hair_color

    @property
    def skin(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._skin

    @skin.setter
    def skin(self, skin: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._skin = skin

    @property
    def admin(self) -> AdminLevel:
        return self._admin

    @admin.setter
    def admin(self, admin: AdminLevel) -> None:
        self._admin = admin

    @property
    def equipment(self) -> EquipmentCharacterSelect:
        return self._equipment

    @equipment.setter
    def equipment(self, equipment: EquipmentCharacterSelect) -> None:
        self._equipment = equipment

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterSelectionListEntry") -> None:
        """
        Serializes an instance of `CharacterSelectionListEntry` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterSelectionListEntry): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_int(data._id)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._gender is None:
                raise SerializationError("gender must be provided.")
            writer.add_char(int(data._gender))
            if data._hair_style is None:
                raise SerializationError("hair_style must be provided.")
            writer.add_char(data._hair_style)
            if data._hair_color is None:
                raise SerializationError("hair_color must be provided.")
            writer.add_char(data._hair_color)
            if data._skin is None:
                raise SerializationError("skin must be provided.")
            writer.add_char(data._skin)
            if data._admin is None:
                raise SerializationError("admin must be provided.")
            writer.add_char(int(data._admin))
            if data._equipment is None:
                raise SerializationError("equipment must be provided.")
            EquipmentCharacterSelect.serialize(writer, data._equipment)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterSelectionListEntry":
        """
        Deserializes an instance of `CharacterSelectionListEntry` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterSelectionListEntry: The data to serialize.
        """
        data: CharacterSelectionListEntry = CharacterSelectionListEntry()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._id = reader.get_int()
            data._level = reader.get_char()
            data._gender = Gender(reader.get_char())
            data._hair_style = reader.get_char()
            data._hair_color = reader.get_char()
            data._skin = reader.get_char()
            data._admin = AdminLevel(reader.get_char())
            data._equipment = EquipmentCharacterSelect.deserialize(reader)
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterSelectionListEntry(byte_size={repr(self._byte_size)}, name={repr(self._name)}, id={repr(self._id)}, level={repr(self._level)}, gender={repr(self._gender)}, hair_style={repr(self._hair_style)}, hair_color={repr(self._hair_color)}, skin={repr(self._skin)}, admin={repr(self._admin)}, equipment={repr(self._equipment)})"
