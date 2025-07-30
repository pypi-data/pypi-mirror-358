# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .item_type import ItemType
from .item_subtype import ItemSubtype
from .item_special import ItemSpecial
from .item_size import ItemSize
from .element import Element
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EifRecord:
    """
    Record of Item data in an Endless Item File
    """
    _byte_size: int = 0
    _name_length: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _graphic_id: int = None # type: ignore [assignment]
    _type: ItemType = None # type: ignore [assignment]
    _subtype: ItemSubtype = None # type: ignore [assignment]
    _special: ItemSpecial = None # type: ignore [assignment]
    _hp: int = None # type: ignore [assignment]
    _tp: int = None # type: ignore [assignment]
    _min_damage: int = None # type: ignore [assignment]
    _max_damage: int = None # type: ignore [assignment]
    _accuracy: int = None # type: ignore [assignment]
    _evade: int = None # type: ignore [assignment]
    _armor: int = None # type: ignore [assignment]
    _return_damage: int = None # type: ignore [assignment]
    _str: int = None # type: ignore [assignment]
    _intl: int = None # type: ignore [assignment]
    _wis: int = None # type: ignore [assignment]
    _agi: int = None # type: ignore [assignment]
    _con: int = None # type: ignore [assignment]
    _cha: int = None # type: ignore [assignment]
    _light_resistance: int = None # type: ignore [assignment]
    _dark_resistance: int = None # type: ignore [assignment]
    _earth_resistance: int = None # type: ignore [assignment]
    _air_resistance: int = None # type: ignore [assignment]
    _water_resistance: int = None # type: ignore [assignment]
    _fire_resistance: int = None # type: ignore [assignment]
    _spec1: int = None # type: ignore [assignment]
    _spec2: int = None # type: ignore [assignment]
    _spec3: int = None # type: ignore [assignment]
    _level_requirement: int = None # type: ignore [assignment]
    _class_requirement: int = None # type: ignore [assignment]
    _str_requirement: int = None # type: ignore [assignment]
    _int_requirement: int = None # type: ignore [assignment]
    _wis_requirement: int = None # type: ignore [assignment]
    _agi_requirement: int = None # type: ignore [assignment]
    _con_requirement: int = None # type: ignore [assignment]
    _cha_requirement: int = None # type: ignore [assignment]
    _element: Element = None # type: ignore [assignment]
    _element_damage: int = None # type: ignore [assignment]
    _weight: int = None # type: ignore [assignment]
    _size: ItemSize = None # type: ignore [assignment]

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
    def type(self) -> ItemType:
        return self._type

    @type.setter
    def type(self, type: ItemType) -> None:
        self._type = type

    @property
    def subtype(self) -> ItemSubtype:
        return self._subtype

    @subtype.setter
    def subtype(self, subtype: ItemSubtype) -> None:
        self._subtype = subtype

    @property
    def special(self) -> ItemSpecial:
        return self._special

    @special.setter
    def special(self, special: ItemSpecial) -> None:
        self._special = special

    @property
    def hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hp = hp

    @property
    def tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._tp

    @tp.setter
    def tp(self, tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._tp = tp

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
    def str(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._str

    @str.setter
    def str(self, str: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._str = str

    @property
    def intl(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._intl

    @intl.setter
    def intl(self, intl: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._intl = intl

    @property
    def wis(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._wis

    @wis.setter
    def wis(self, wis: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._wis = wis

    @property
    def agi(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._agi

    @agi.setter
    def agi(self, agi: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._agi = agi

    @property
    def con(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._con

    @con.setter
    def con(self, con: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._con = con

    @property
    def cha(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._cha

    @cha.setter
    def cha(self, cha: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._cha = cha

    @property
    def light_resistance(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._light_resistance

    @light_resistance.setter
    def light_resistance(self, light_resistance: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._light_resistance = light_resistance

    @property
    def dark_resistance(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._dark_resistance

    @dark_resistance.setter
    def dark_resistance(self, dark_resistance: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._dark_resistance = dark_resistance

    @property
    def earth_resistance(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._earth_resistance

    @earth_resistance.setter
    def earth_resistance(self, earth_resistance: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._earth_resistance = earth_resistance

    @property
    def air_resistance(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._air_resistance

    @air_resistance.setter
    def air_resistance(self, air_resistance: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._air_resistance = air_resistance

    @property
    def water_resistance(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._water_resistance

    @water_resistance.setter
    def water_resistance(self, water_resistance: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._water_resistance = water_resistance

    @property
    def fire_resistance(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._fire_resistance

    @fire_resistance.setter
    def fire_resistance(self, fire_resistance: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._fire_resistance = fire_resistance

    @property
    def spec1(self) -> int:
        """
        Holds one the following values, depending on item type:
        scroll_map, doll_graphic, exp_reward, hair_color, effect, key, alcohol_potency

        Note:
          - Value range is 0-16194276.
        """
        return self._spec1

    @spec1.setter
    def spec1(self, spec1: int) -> None:
        """
        Holds one the following values, depending on item type:
        scroll_map, doll_graphic, exp_reward, hair_color, effect, key, alcohol_potency

        Note:
          - Value range is 0-16194276.
        """
        self._spec1 = spec1

    @property
    def spec2(self) -> int:
        """
        Holds one the following values, depending on item type:
        scroll_x, gender

        Note:
          - Value range is 0-252.
        """
        return self._spec2

    @spec2.setter
    def spec2(self, spec2: int) -> None:
        """
        Holds one the following values, depending on item type:
        scroll_x, gender

        Note:
          - Value range is 0-252.
        """
        self._spec2 = spec2

    @property
    def spec3(self) -> int:
        """
        Holds one the following values, depending on item type:
        scroll_y

        Note:
          - Value range is 0-252.
        """
        return self._spec3

    @spec3.setter
    def spec3(self, spec3: int) -> None:
        """
        Holds one the following values, depending on item type:
        scroll_y

        Note:
          - Value range is 0-252.
        """
        self._spec3 = spec3

    @property
    def level_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._level_requirement

    @level_requirement.setter
    def level_requirement(self, level_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._level_requirement = level_requirement

    @property
    def class_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._class_requirement

    @class_requirement.setter
    def class_requirement(self, class_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._class_requirement = class_requirement

    @property
    def str_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._str_requirement

    @str_requirement.setter
    def str_requirement(self, str_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._str_requirement = str_requirement

    @property
    def int_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._int_requirement

    @int_requirement.setter
    def int_requirement(self, int_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._int_requirement = int_requirement

    @property
    def wis_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._wis_requirement

    @wis_requirement.setter
    def wis_requirement(self, wis_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._wis_requirement = wis_requirement

    @property
    def agi_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._agi_requirement

    @agi_requirement.setter
    def agi_requirement(self, agi_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._agi_requirement = agi_requirement

    @property
    def con_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._con_requirement

    @con_requirement.setter
    def con_requirement(self, con_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._con_requirement = con_requirement

    @property
    def cha_requirement(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._cha_requirement

    @cha_requirement.setter
    def cha_requirement(self, cha_requirement: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._cha_requirement = cha_requirement

    @property
    def element(self) -> Element:
        return self._element

    @element.setter
    def element(self, element: Element) -> None:
        self._element = element

    @property
    def element_damage(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._element_damage

    @element_damage.setter
    def element_damage(self, element_damage: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._element_damage = element_damage

    @property
    def weight(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._weight

    @weight.setter
    def weight(self, weight: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._weight = weight

    @property
    def size(self) -> ItemSize:
        return self._size

    @size.setter
    def size(self, size: ItemSize) -> None:
        self._size = size

    @staticmethod
    def serialize(writer: EoWriter, data: "EifRecord") -> None:
        """
        Serializes an instance of `EifRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EifRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._graphic_id is None:
                raise SerializationError("graphic_id must be provided.")
            writer.add_short(data._graphic_id)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_char(int(data._type))
            if data._subtype is None:
                raise SerializationError("subtype must be provided.")
            writer.add_char(int(data._subtype))
            if data._special is None:
                raise SerializationError("special must be provided.")
            writer.add_char(int(data._special))
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._tp is None:
                raise SerializationError("tp must be provided.")
            writer.add_short(data._tp)
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
            if data._str is None:
                raise SerializationError("str must be provided.")
            writer.add_char(data._str)
            if data._intl is None:
                raise SerializationError("intl must be provided.")
            writer.add_char(data._intl)
            if data._wis is None:
                raise SerializationError("wis must be provided.")
            writer.add_char(data._wis)
            if data._agi is None:
                raise SerializationError("agi must be provided.")
            writer.add_char(data._agi)
            if data._con is None:
                raise SerializationError("con must be provided.")
            writer.add_char(data._con)
            if data._cha is None:
                raise SerializationError("cha must be provided.")
            writer.add_char(data._cha)
            if data._light_resistance is None:
                raise SerializationError("light_resistance must be provided.")
            writer.add_char(data._light_resistance)
            if data._dark_resistance is None:
                raise SerializationError("dark_resistance must be provided.")
            writer.add_char(data._dark_resistance)
            if data._earth_resistance is None:
                raise SerializationError("earth_resistance must be provided.")
            writer.add_char(data._earth_resistance)
            if data._air_resistance is None:
                raise SerializationError("air_resistance must be provided.")
            writer.add_char(data._air_resistance)
            if data._water_resistance is None:
                raise SerializationError("water_resistance must be provided.")
            writer.add_char(data._water_resistance)
            if data._fire_resistance is None:
                raise SerializationError("fire_resistance must be provided.")
            writer.add_char(data._fire_resistance)
            if data._spec1 is None:
                raise SerializationError("spec1 must be provided.")
            writer.add_three(data._spec1)
            if data._spec2 is None:
                raise SerializationError("spec2 must be provided.")
            writer.add_char(data._spec2)
            if data._spec3 is None:
                raise SerializationError("spec3 must be provided.")
            writer.add_char(data._spec3)
            if data._level_requirement is None:
                raise SerializationError("level_requirement must be provided.")
            writer.add_short(data._level_requirement)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_short(data._class_requirement)
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
            if data._element is None:
                raise SerializationError("element must be provided.")
            writer.add_char(int(data._element))
            if data._element_damage is None:
                raise SerializationError("element_damage must be provided.")
            writer.add_char(data._element_damage)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            writer.add_char(data._weight)
            writer.add_char(0)
            if data._size is None:
                raise SerializationError("size must be provided.")
            writer.add_char(int(data._size))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EifRecord":
        """
        Deserializes an instance of `EifRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EifRecord: The data to serialize.
        """
        data: EifRecord = EifRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._name_length = reader.get_char()
            data._name = reader.get_fixed_string(data._name_length, False)
            data._graphic_id = reader.get_short()
            data._type = ItemType(reader.get_char())
            data._subtype = ItemSubtype(reader.get_char())
            data._special = ItemSpecial(reader.get_char())
            data._hp = reader.get_short()
            data._tp = reader.get_short()
            data._min_damage = reader.get_short()
            data._max_damage = reader.get_short()
            data._accuracy = reader.get_short()
            data._evade = reader.get_short()
            data._armor = reader.get_short()
            data._return_damage = reader.get_char()
            data._str = reader.get_char()
            data._intl = reader.get_char()
            data._wis = reader.get_char()
            data._agi = reader.get_char()
            data._con = reader.get_char()
            data._cha = reader.get_char()
            data._light_resistance = reader.get_char()
            data._dark_resistance = reader.get_char()
            data._earth_resistance = reader.get_char()
            data._air_resistance = reader.get_char()
            data._water_resistance = reader.get_char()
            data._fire_resistance = reader.get_char()
            data._spec1 = reader.get_three()
            data._spec2 = reader.get_char()
            data._spec3 = reader.get_char()
            data._level_requirement = reader.get_short()
            data._class_requirement = reader.get_short()
            data._str_requirement = reader.get_short()
            data._int_requirement = reader.get_short()
            data._wis_requirement = reader.get_short()
            data._agi_requirement = reader.get_short()
            data._con_requirement = reader.get_short()
            data._cha_requirement = reader.get_short()
            data._element = Element(reader.get_char())
            data._element_damage = reader.get_char()
            data._weight = reader.get_char()
            reader.get_char()
            data._size = ItemSize(reader.get_char())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EifRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, graphic_id={repr(self._graphic_id)}, type={repr(self._type)}, subtype={repr(self._subtype)}, special={repr(self._special)}, hp={repr(self._hp)}, tp={repr(self._tp)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)}, return_damage={repr(self._return_damage)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)}, light_resistance={repr(self._light_resistance)}, dark_resistance={repr(self._dark_resistance)}, earth_resistance={repr(self._earth_resistance)}, air_resistance={repr(self._air_resistance)}, water_resistance={repr(self._water_resistance)}, fire_resistance={repr(self._fire_resistance)}, spec1={repr(self._spec1)}, spec2={repr(self._spec2)}, spec3={repr(self._spec3)}, level_requirement={repr(self._level_requirement)}, class_requirement={repr(self._class_requirement)}, str_requirement={repr(self._str_requirement)}, int_requirement={repr(self._int_requirement)}, wis_requirement={repr(self._wis_requirement)}, agi_requirement={repr(self._agi_requirement)}, con_requirement={repr(self._con_requirement)}, cha_requirement={repr(self._cha_requirement)}, element={repr(self._element)}, element_damage={repr(self._element_damage)}, weight={repr(self._weight)}, size={repr(self._size)})"
