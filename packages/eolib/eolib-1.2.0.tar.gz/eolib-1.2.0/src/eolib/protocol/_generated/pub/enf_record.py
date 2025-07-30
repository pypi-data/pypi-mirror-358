# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .npc_type import NpcType
from .element import Element
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EnfRecord:
    """
    Record of NPC data in an Endless NPC File
    """
    _byte_size: int = 0
    _name_length: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _graphic_id: int = None # type: ignore [assignment]
    _race: int = None # type: ignore [assignment]
    _boss: bool = None # type: ignore [assignment]
    _child: bool = None # type: ignore [assignment]
    _type: NpcType = None # type: ignore [assignment]
    _behavior_id: int = None # type: ignore [assignment]
    _hp: int = None # type: ignore [assignment]
    _tp: int = None # type: ignore [assignment]
    _min_damage: int = None # type: ignore [assignment]
    _max_damage: int = None # type: ignore [assignment]
    _accuracy: int = None # type: ignore [assignment]
    _evade: int = None # type: ignore [assignment]
    _armor: int = None # type: ignore [assignment]
    _return_damage: int = None # type: ignore [assignment]
    _element: Element = None # type: ignore [assignment]
    _element_damage: int = None # type: ignore [assignment]
    _element_weakness: Element = None # type: ignore [assignment]
    _element_weakness_damage: int = None # type: ignore [assignment]
    _level: int = None # type: ignore [assignment]
    _experience: int = None # type: ignore [assignment]

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
    def race(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._race

    @race.setter
    def race(self, race: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._race = race

    @property
    def boss(self) -> bool:
        return self._boss

    @boss.setter
    def boss(self, boss: bool) -> None:
        self._boss = boss

    @property
    def child(self) -> bool:
        return self._child

    @child.setter
    def child(self, child: bool) -> None:
        self._child = child

    @property
    def type(self) -> NpcType:
        return self._type

    @type.setter
    def type(self, type: NpcType) -> None:
        self._type = type

    @property
    def behavior_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, behavior_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._behavior_id = behavior_id

    @property
    def hp(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
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
    def element(self) -> Element:
        return self._element

    @element.setter
    def element(self, element: Element) -> None:
        self._element = element

    @property
    def element_damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._element_damage

    @element_damage.setter
    def element_damage(self, element_damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._element_damage = element_damage

    @property
    def element_weakness(self) -> Element:
        return self._element_weakness

    @element_weakness.setter
    def element_weakness(self, element_weakness: Element) -> None:
        self._element_weakness = element_weakness

    @property
    def element_weakness_damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._element_weakness_damage

    @element_weakness_damage.setter
    def element_weakness_damage(self, element_weakness_damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._element_weakness_damage = element_weakness_damage

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
    def experience(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._experience

    @experience.setter
    def experience(self, experience: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._experience = experience

    @staticmethod
    def serialize(writer: EoWriter, data: "EnfRecord") -> None:
        """
        Serializes an instance of `EnfRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EnfRecord): The data to serialize.
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
            if data._race is None:
                raise SerializationError("race must be provided.")
            writer.add_char(data._race)
            if data._boss is None:
                raise SerializationError("boss must be provided.")
            writer.add_short(1 if data._boss else 0)
            if data._child is None:
                raise SerializationError("child must be provided.")
            writer.add_short(1 if data._child else 0)
            if data._type is None:
                raise SerializationError("type must be provided.")
            writer.add_short(int(data._type))
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_three(data._hp)
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
            if data._element is None:
                raise SerializationError("element must be provided.")
            writer.add_short(int(data._element))
            if data._element_damage is None:
                raise SerializationError("element_damage must be provided.")
            writer.add_short(data._element_damage)
            if data._element_weakness is None:
                raise SerializationError("element_weakness must be provided.")
            writer.add_short(int(data._element_weakness))
            if data._element_weakness_damage is None:
                raise SerializationError("element_weakness_damage must be provided.")
            writer.add_short(data._element_weakness_damage)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._experience is None:
                raise SerializationError("experience must be provided.")
            writer.add_three(data._experience)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EnfRecord":
        """
        Deserializes an instance of `EnfRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EnfRecord: The data to serialize.
        """
        data: EnfRecord = EnfRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._name_length = reader.get_char()
            data._name = reader.get_fixed_string(data._name_length, False)
            data._graphic_id = reader.get_short()
            data._race = reader.get_char()
            data._boss = reader.get_short() != 0
            data._child = reader.get_short() != 0
            data._type = NpcType(reader.get_short())
            data._behavior_id = reader.get_short()
            data._hp = reader.get_three()
            data._tp = reader.get_short()
            data._min_damage = reader.get_short()
            data._max_damage = reader.get_short()
            data._accuracy = reader.get_short()
            data._evade = reader.get_short()
            data._armor = reader.get_short()
            data._return_damage = reader.get_char()
            data._element = Element(reader.get_short())
            data._element_damage = reader.get_short()
            data._element_weakness = Element(reader.get_short())
            data._element_weakness_damage = reader.get_short()
            data._level = reader.get_char()
            data._experience = reader.get_three()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EnfRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, graphic_id={repr(self._graphic_id)}, race={repr(self._race)}, boss={repr(self._boss)}, child={repr(self._child)}, type={repr(self._type)}, behavior_id={repr(self._behavior_id)}, hp={repr(self._hp)}, tp={repr(self._tp)}, min_damage={repr(self._min_damage)}, max_damage={repr(self._max_damage)}, accuracy={repr(self._accuracy)}, evade={repr(self._evade)}, armor={repr(self._armor)}, return_damage={repr(self._return_damage)}, element={repr(self._element)}, element_damage={repr(self._element_damage)}, element_weakness={repr(self._element_weakness)}, element_weakness_damage={repr(self._element_weakness_damage)}, level={repr(self._level)}, experience={repr(self._experience)})"
