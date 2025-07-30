# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class SkillMasterSkillRecord:
    """
    Record of a skill that a Skill Master NPC can teach
    """
    _byte_size: int = 0
    _skill_id: int = None # type: ignore [assignment]
    _level_requirement: int = None # type: ignore [assignment]
    _class_requirement: int = None # type: ignore [assignment]
    _price: int = None # type: ignore [assignment]
    _skill_requirements: list[int] = None # type: ignore [assignment]
    _str_requirement: int = None # type: ignore [assignment]
    _int_requirement: int = None # type: ignore [assignment]
    _wis_requirement: int = None # type: ignore [assignment]
    _agi_requirement: int = None # type: ignore [assignment]
    _con_requirement: int = None # type: ignore [assignment]
    _cha_requirement: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def skill_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._skill_id

    @skill_id.setter
    def skill_id(self, skill_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._skill_id = skill_id

    @property
    def level_requirement(self) -> int:
        """
        Level required to learn this skill

        Note:
          - Value range is 0-252.
        """
        return self._level_requirement

    @level_requirement.setter
    def level_requirement(self, level_requirement: int) -> None:
        """
        Level required to learn this skill

        Note:
          - Value range is 0-252.
        """
        self._level_requirement = level_requirement

    @property
    def class_requirement(self) -> int:
        """
        Class required to learn this skill

        Note:
          - Value range is 0-252.
        """
        return self._class_requirement

    @class_requirement.setter
    def class_requirement(self, class_requirement: int) -> None:
        """
        Class required to learn this skill

        Note:
          - Value range is 0-252.
        """
        self._class_requirement = class_requirement

    @property
    def price(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._price

    @price.setter
    def price(self, price: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._price = price

    @property
    def skill_requirements(self) -> list[int]:
        """
        IDs of skills that must be learned before a player can learn this skill

        Note:
          - Length must be `4`.
          - Element value range is 0-64008.
        """
        return self._skill_requirements

    @skill_requirements.setter
    def skill_requirements(self, skill_requirements: list[int]) -> None:
        """
        IDs of skills that must be learned before a player can learn this skill

        Note:
          - Length must be `4`.
          - Element value range is 0-64008.
        """
        self._skill_requirements = skill_requirements

    @property
    def str_requirement(self) -> int:
        """
        Strength required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        return self._str_requirement

    @str_requirement.setter
    def str_requirement(self, str_requirement: int) -> None:
        """
        Strength required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        self._str_requirement = str_requirement

    @property
    def int_requirement(self) -> int:
        """
        Intelligence required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        return self._int_requirement

    @int_requirement.setter
    def int_requirement(self, int_requirement: int) -> None:
        """
        Intelligence required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        self._int_requirement = int_requirement

    @property
    def wis_requirement(self) -> int:
        """
        Wisdom required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        return self._wis_requirement

    @wis_requirement.setter
    def wis_requirement(self, wis_requirement: int) -> None:
        """
        Wisdom required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        self._wis_requirement = wis_requirement

    @property
    def agi_requirement(self) -> int:
        """
        Agility required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        return self._agi_requirement

    @agi_requirement.setter
    def agi_requirement(self, agi_requirement: int) -> None:
        """
        Agility required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        self._agi_requirement = agi_requirement

    @property
    def con_requirement(self) -> int:
        """
        Constitution required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        return self._con_requirement

    @con_requirement.setter
    def con_requirement(self, con_requirement: int) -> None:
        """
        Constitution required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        self._con_requirement = con_requirement

    @property
    def cha_requirement(self) -> int:
        """
        Charisma required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        return self._cha_requirement

    @cha_requirement.setter
    def cha_requirement(self, cha_requirement: int) -> None:
        """
        Charisma required to learn this skill

        Note:
          - Value range is 0-64008.
        """
        self._cha_requirement = cha_requirement

    @staticmethod
    def serialize(writer: EoWriter, data: "SkillMasterSkillRecord") -> None:
        """
        Serializes an instance of `SkillMasterSkillRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (SkillMasterSkillRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._skill_id is None:
                raise SerializationError("skill_id must be provided.")
            writer.add_short(data._skill_id)
            if data._level_requirement is None:
                raise SerializationError("level_requirement must be provided.")
            writer.add_char(data._level_requirement)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_char(data._class_requirement)
            if data._price is None:
                raise SerializationError("price must be provided.")
            writer.add_int(data._price)
            if data._skill_requirements is None:
                raise SerializationError("skill_requirements must be provided.")
            if len(data._skill_requirements) != 4:
                raise SerializationError(f"Expected length of skill_requirements to be exactly 4, got {len(data._skill_requirements)}.")
            for i in range(4):
                writer.add_short(data._skill_requirements[i])
            if data._str_requirement is None:
                raise SerializationError("str_requirement must be provided.")
            writer.add_short(data._str_requirement)
            if data._int_requirement is None:
                raise SerializationError("int_requirement must be provided.")
            writer.add_short(data._int_requirement)
            if data._wis_requirement is None:
                raise SerializationError("wis_requirement must be provided.")
            writer.add_short(data._wis_requirement)
            if data._agi_requirement is None:
                raise SerializationError("agi_requirement must be provided.")
            writer.add_short(data._agi_requirement)
            if data._con_requirement is None:
                raise SerializationError("con_requirement must be provided.")
            writer.add_short(data._con_requirement)
            if data._cha_requirement is None:
                raise SerializationError("cha_requirement must be provided.")
            writer.add_short(data._cha_requirement)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "SkillMasterSkillRecord":
        """
        Deserializes an instance of `SkillMasterSkillRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            SkillMasterSkillRecord: The data to serialize.
        """
        data: SkillMasterSkillRecord = SkillMasterSkillRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._skill_id = reader.get_short()
            data._level_requirement = reader.get_char()
            data._class_requirement = reader.get_char()
            data._price = reader.get_int()
            data._skill_requirements = []
            for i in range(4):
                data._skill_requirements.append(reader.get_short())
            data._str_requirement = reader.get_short()
            data._int_requirement = reader.get_short()
            data._wis_requirement = reader.get_short()
            data._agi_requirement = reader.get_short()
            data._con_requirement = reader.get_short()
            data._cha_requirement = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"SkillMasterSkillRecord(byte_size={repr(self._byte_size)}, skill_id={repr(self._skill_id)}, level_requirement={repr(self._level_requirement)}, class_requirement={repr(self._class_requirement)}, price={repr(self._price)}, skill_requirements={repr(self._skill_requirements)}, str_requirement={repr(self._str_requirement)}, int_requirement={repr(self._int_requirement)}, wis_requirement={repr(self._wis_requirement)}, agi_requirement={repr(self._agi_requirement)}, con_requirement={repr(self._con_requirement)}, cha_requirement={repr(self._cha_requirement)})"
