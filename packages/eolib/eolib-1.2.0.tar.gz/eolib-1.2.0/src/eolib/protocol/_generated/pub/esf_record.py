# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .skill_type import SkillType
from .skill_target_type import SkillTargetType
from .skill_target_restrict import SkillTargetRestrict
from .skill_nature import SkillNature
from .element import Element
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EsfRecord:
    """
    Record of Skill data in an Endless Skill File
    """
    _byte_size: int = 0
    _name_length: int = None # type: ignore [assignment]
    _chant_length: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _chant: str = None # type: ignore [assignment]
    _icon_id: int = None # type: ignore [assignment]
    _graphic_id: int = None # type: ignore [assignment]
    _tp_cost: int = None # type: ignore [assignment]
    _sp_cost: int = None # type: ignore [assignment]
    _cast_time: int = None # type: ignore [assignment]
    _nature: SkillNature = None # type: ignore [assignment]
    _type: SkillType = None # type: ignore [assignment]
    _element: Element = None # type: ignore [assignment]
    _element_power: int = None # type: ignore [assignment]
    _target_restrict: SkillTargetRestrict = None # type: ignore [assignment]
    _target_type: SkillTargetType = None # type: ignore [assignment]
    _target_time: int = None # type: ignore [assignment]
    _max_skill_level: int = None # type: ignore [assignment]
    _min_damage: int = None # type: ignore [assignment]
    _max_damage: int = None # type: ignore [assignment]
    _accuracy: int = None # type: ignore [assignment]
    _evade: int = None # type: ignore [assignment]
    _armor: int = None # type: ignore [assignment]
    _return_damage: int = None # type: ignore [assignment]
    _hp_heal: int = None # type: ignore [assignment]
    _tp_heal: int = None # type: ignore [assignment]
    _sp_heal: int = None # type: ignore [assignment]
    _str: int = None # type: ignore [assignment]
    _intl: int = None # type: ignore [assignment]
    _wis: int = None # type: ignore [assignment]
    _agi: int = None # type: ignore [assignment]
    _con: int = None # type: ignore [assignment]
    _cha: int = None # type: ignore [assignment]

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
        """
        Note:
          - Length must be 252 or less.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._name = name
        self._name_length = len(self._name)

    @property
    def chant(self) -> str:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._chant

    @chant.setter
    def chant(self, chant: str) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._chant = chant
        self._chant_length = len(self._chant)

    @property
    def icon_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._icon_id

    @icon_id.setter
    def icon_id(self, icon_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._icon_id = icon_id

    @property
    def graphic_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._graphic_id

    @graphic_id.setter
    def graphic_id(self, graphic_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._graphic_id = graphic_id

    @property
    def tp_cost(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._tp_cost

    @tp_cost.setter
    def tp_cost(self, tp_cost: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._tp_cost = tp_cost

    @property
    def sp_cost(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._sp_cost

    @sp_cost.setter
    def sp_cost(self, sp_cost: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._sp_cost = sp_cost

    @property
    def cast_time(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._cast_time

    @cast_time.setter
    def cast_time(self, cast_time: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._cast_time = cast_time

    @property
    def nature(self) -> SkillNature:
        return self._nature

    @nature.setter
    def nature(self, nature: SkillNature) -> None:
        self._nature = nature

    @property
    def type(self) -> SkillType:
        return self._type

    @type.setter
    def type(self, type: SkillType) -> None:
        self._type = type

    @property
    def element(self) -> Element:
        return self._element

    @element.setter
    def element(self, element: Element) -> None:
        self._element = element

    @property
    def element_power(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._element_power

    @element_power.setter
    def element_power(self, element_power: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._element_power = element_power

    @property
    def target_restrict(self) -> SkillTargetRestrict:
        return self._target_restrict

    @target_restrict.setter
    def target_restrict(self, target_restrict: SkillTargetRestrict) -> None:
        self._target_restrict = target_restrict

    @property
    def target_type(self) -> SkillTargetType:
        return self._target_type

    @target_type.setter
    def target_type(self, target_type: SkillTargetType) -> None:
        self._target_type = target_type

    @property
    def target_time(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._target_time

    @target_time.setter
    def target_time(self, target_time: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._target_time = target_time

    @property
    def max_skill_level(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_skill_level

    @max_skill_level.setter
    def max_skill_level(self, max_skill_level: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_skill_level = max_skill_level

    @property
    def min_damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._min_damage

    @min_damage.setter
    def min_damage(self, min_damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._min_damage = min_damage

    @property
    def max_damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_damage

    @max_damage.setter
    def max_damage(self, max_damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_damage = max_damage

    @property
    def accuracy(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._accuracy

    @accuracy.setter
    def accuracy(self, accuracy: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._accuracy = accuracy

    @property
    def evade(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._evade

    @evade.setter
    def evade(self, evade: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._evade = evade

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
    def return_damage(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._return_damage

    @return_damage.setter
    def return_damage(self, return_damage: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._return_damage = return_damage

    @property
    def hp_heal(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hp_heal

    @hp_heal.setter
    def hp_heal(self, hp_heal: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hp_heal = hp_heal

    @property
    def tp_heal(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._tp_heal

    @tp_heal.setter
    def tp_heal(self, tp_heal: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._tp_heal = tp_heal

    @property
    def sp_heal(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._sp_heal

    @sp_heal.setter
    def sp_heal(self, sp_heal: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._sp_heal = sp_heal

    @property
    def str(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._str

    @str.setter
    def str(self, str: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._str = str

    @property
    def intl(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._intl

    @intl.setter
    def intl(self, intl: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._intl = intl

    @property
    def wis(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._wis

    @wis.setter
    def wis(self, wis: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._wis = wis

    @property
    def agi(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._agi

    @agi.setter
    def agi(self, agi: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._agi = agi

    @property
    def con(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._con

    @con.setter
    def con(self, con: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._con = con

    @property
    def cha(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._cha

    @cha.setter
    def cha(self, cha: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._cha = cha

    @staticmethod
    def serialize(writer: EoWriter, data: "EsfRecord") -> None:
        """
        Serializes an instance of `EsfRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EsfRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._chant_length is None:
                raise SerializationError("chant_length must be provided.")
            writer.add_char(data._chant_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._chant is None:
                raise SerializationError("chant must be provided.")
            if len(data._chant) > 252:
                raise SerializationError(f"Expected length of chant to be 252 or less, got {len(data._chant)}.")
            writer.add_fixed_string(data._chant, data._chant_length, False)
            if data._icon_id is None:
                raise SerializationError("icon_id must be provided.")
            writer.add_short(data._icon_id)
            if data._graphic_id is None:
                raise SerializationError("graphic_id must be provided.")
            writer.add_short(data._graphic_id)
            if data._tp_cost is None:
                raise SerializationError("tp_cost must be provided.")
            writer.add_short(data._tp_cost)
            if data._sp_cost is None:
                raise SerializationError("sp_cost must be provided.")
            writer.add_short(data._sp_cost)
            if data._cast_time is None:
                raise SerializationError("cast_time must be provided.")
            writer.add_char(data._cast_time)
            if data._nature is None:
                raise SerializationError("nature must be provided.")
            writer.add_char(int(data._nature))
            writer.add_char(1)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_three(int(data._type))
            if data._element is None:
                raise SerializationError("element must be provided.")
            writer.add_char(int(data._element))
            if data._element_power is None:
                raise SerializationError("element_power must be provided.")
            writer.add_short(data._element_power)
            if data._target_restrict is None:
                raise SerializationError("target_restrict must be provided.")
            writer.add_char(int(data._target_restrict))
            if data._target_type is None:
                raise SerializationError("target_type must be provided.")
            writer.add_char(int(data._target_type))
            if data._target_time is None:
                raise SerializationError("target_time must be provided.")
            writer.add_char(data._target_time)
            writer.add_char(0)
            if data._max_skill_level is None:
                raise SerializationError("max_skill_level must be provided.")
            writer.add_short(data._max_skill_level)
            if data._min_damage is None:
                raise SerializationError("min_damage must be provided.")
            writer.add_short(data._min_damage)
            if data._max_damage is None:
                raise SerializationError("max_damage must be provided.")
            writer.add_short(data._max_damage)
            if data._accuracy is None:
                raise SerializationError("accuracy must be provided.")
            writer.add_short(data._accuracy)
            if data._evade is None:
                raise SerializationError("evade must be provided.")
            writer.add_short(data._evade)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
            if data._return_damage is None:
                raise SerializationError("return_damage must be provided.")
            writer.add_char(data._return_damage)
            if data._hp_heal is None:
                raise SerializationError("hp_heal must be provided.")
            writer.add_short(data._hp_heal)
            if data._tp_heal is None:
                raise SerializationError("tp_heal must be provided.")
            writer.add_short(data._tp_heal)
            if data._sp_heal is None:
                raise SerializationError("sp_heal must be provided.")
            writer.add_char(data._sp_heal)
            if data._str is None:
                raise SerializationError("str must be provided.")
            writer.add_short(data._str)
            if data._intl is None:
                raise SerializationError("intl must be provided.")
            writer.add_short(data._intl)
            if data._wis is None:
                raise SerializationError("wis must be provided.")
            writer.add_short(data._wis)
            if data._agi is None:
                raise SerializationError("agi must be provided.")
            writer.add_short(data._agi)
            if data._con is None:
                raise SerializationError("con must be provided.")
            writer.add_short(data._con)
            if data._cha is None:
                raise SerializationError("cha must be provided.")
            writer.add_short(data._cha)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EsfRecord":
        """
        Deserializes an instance of `EsfRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EsfRecord: The data to serialize.
        """
        data: EsfRecord = EsfRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._name_length = reader.get_char()
            data._chant_length = reader.get_char()
            data._name = reader.get_fixed_string(data._name_length, False)
            data._chant = reader.get_fixed_string(data._chant_length, False)
            data._icon_id = reader.get_short()
            data._graphic_id = reader.get_short()
            data._tp_cost = reader.get_short()
            data._sp_cost = reader.get_short()
            data._cast_time = reader.get_char()
            data._nature = SkillNature(reader.get_char())
            reader.get_char()
            data._type = SkillType(reader.get_three())
            data._element = Element(reader.get_char())
            data._element_power = reader.get_short()
            data._target_restrict = SkillTargetRestrict(reader.get_char())
            data._target_type = SkillTargetType(reader.get_char())
            data._target_time = reader.get_char()
            reader.get_char()
            data._max_skill_level = reader.get_short()
            data._min_damage = reader.get_short()
            data._max_damage = reader.get_short()
            data._accuracy = reader.get_short()
            data._evade = reader.get_short()
            data._armor = reader.get_short()
            data._return_damage = reader.get_char()
            data._hp_heal = reader.get_short()
            data._tp_heal = reader.get_short()
            data._sp_heal = reader.get_char()
            data._str = reader.get_short()
            data._intl = reader.get_short()
            data._wis = reader.get_short()
            data._agi = reader.get_short()
            data._con = reader.get_short()
            data._cha = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EsfRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, chant={repr(self._chant)}, icon_id={repr(self._icon_id)}, graphic_id={repr(self._graphic_id)}, tp_cost={repr(self._tp_cost)}, sp_cost={repr(self._sp_cost)}, cast_time={repr(self._cast_time)}, nature={repr(self._nature)}, type={repr(self._type)}, element={repr(self._element)}, element_power={repr(self._element_power)}, target_restrict={repr(self._target_restrict)}, target_type={repr(self._target_type)}, target_time={repr(self._target_time)}, max_skill_level={repr(self._max_skill_level)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)}, return_damage={repr(self._return_damage)}, hp_heal={repr(self._hp_heal)}, tp_heal={repr(self._tp_heal)}, sp_heal={repr(self._sp_heal)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)})"
