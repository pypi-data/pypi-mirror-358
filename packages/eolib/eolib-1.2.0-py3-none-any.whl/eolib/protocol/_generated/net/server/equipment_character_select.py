# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EquipmentCharacterSelect:
    """
    Player equipment data.
    Sent with a character in the character selection list.
    Note that these values are graphic IDs.
    """
    _byte_size: int = 0
    _boots: int = None # type: ignore [assignment]
    _armor: int = None # type: ignore [assignment]
    _hat: int = None # type: ignore [assignment]
    _shield: int = None # type: ignore [assignment]
    _weapon: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def boots(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._boots

    @boots.setter
    def boots(self, boots: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._boots = boots

    @property
    def armor(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._armor

    @armor.setter
    def armor(self, armor: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._armor = armor

    @property
    def hat(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hat

    @hat.setter
    def hat(self, hat: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hat = hat

    @property
    def shield(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._shield

    @shield.setter
    def shield(self, shield: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._shield = shield

    @property
    def weapon(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._weapon

    @weapon.setter
    def weapon(self, weapon: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._weapon = weapon

    @staticmethod
    def serialize(writer: EoWriter, data: "EquipmentCharacterSelect") -> None:
        """
        Serializes an instance of `EquipmentCharacterSelect` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EquipmentCharacterSelect): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._boots is None:
                raise SerializationError("boots must be provided.")
            writer.add_short(data._boots)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
            if data._hat is None:
                raise SerializationError("hat must be provided.")
            writer.add_short(data._hat)
            if data._shield is None:
                raise SerializationError("shield must be provided.")
            writer.add_short(data._shield)
            if data._weapon is None:
                raise SerializationError("weapon must be provided.")
            writer.add_short(data._weapon)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EquipmentCharacterSelect":
        """
        Deserializes an instance of `EquipmentCharacterSelect` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EquipmentCharacterSelect: The data to serialize.
        """
        data: EquipmentCharacterSelect = EquipmentCharacterSelect()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._boots = reader.get_short()
            data._armor = reader.get_short()
            data._hat = reader.get_short()
            data._shield = reader.get_short()
            data._weapon = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EquipmentCharacterSelect(byte_size={repr(self._byte_size)}, boots={repr(self._boots)}, armor={repr(self._armor)}, hat={repr(self._hat)}, shield={repr(self._shield)}, weapon={repr(self._weapon)})"
