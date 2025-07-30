# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from typing import Union
from .character_stats_equipment_change import CharacterStatsEquipmentChange
from ..weight import Weight
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ...pub.item_type import ItemType
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemReplyServerPacket(Packet):
    """
    Reply to using an item
    """
    _byte_size: int = 0
    _item_type: ItemType = None # type: ignore [assignment]
    _used_item: Item = None # type: ignore [assignment]
    _weight: Weight = None # type: ignore [assignment]
    _item_type_data: 'ItemReplyServerPacket.ItemTypeData' = None

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item_type(self) -> ItemType:
        return self._item_type

    @item_type.setter
    def item_type(self, item_type: ItemType) -> None:
        self._item_type = item_type

    @property
    def used_item(self) -> Item:
        return self._used_item

    @used_item.setter
    def used_item(self, used_item: Item) -> None:
        self._used_item = used_item

    @property
    def weight(self) -> Weight:
        return self._weight

    @weight.setter
    def weight(self, weight: Weight) -> None:
        self._weight = weight

    @property
    def item_type_data(self) -> 'ItemReplyServerPacket.ItemTypeData':
        """
        ItemReplyServerPacket.ItemTypeData: Gets or sets the data associated with the `item_type` field.
        """
        return self._item_type_data

    @item_type_data.setter
    def item_type_data(self, item_type_data: 'ItemReplyServerPacket.ItemTypeData') -> None:
        self._item_type_data = item_type_data

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Item

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Reply

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemReplyServerPacket") -> None:
        """
        Serializes an instance of `ItemReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_type is None:
                raise SerializationError("item_type must be provided.")
            writer.add_char(int(data._item_type))
            if data._used_item is None:
                raise SerializationError("used_item must be provided.")
            Item.serialize(writer, data._used_item)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
            if data._item_type == ItemType.Heal:
                if not isinstance(data._item_type_data, ItemReplyServerPacket.ItemTypeDataHeal):
                    raise SerializationError("Expected item_type_data to be type ItemReplyServerPacket.ItemTypeDataHeal for item_type " + ItemType(data._item_type).name + ".")
                ItemReplyServerPacket.ItemTypeDataHeal.serialize(writer, data._item_type_data)
            elif data._item_type == ItemType.HairDye:
                if not isinstance(data._item_type_data, ItemReplyServerPacket.ItemTypeDataHairDye):
                    raise SerializationError("Expected item_type_data to be type ItemReplyServerPacket.ItemTypeDataHairDye for item_type " + ItemType(data._item_type).name + ".")
                ItemReplyServerPacket.ItemTypeDataHairDye.serialize(writer, data._item_type_data)
            elif data._item_type == ItemType.EffectPotion:
                if not isinstance(data._item_type_data, ItemReplyServerPacket.ItemTypeDataEffectPotion):
                    raise SerializationError("Expected item_type_data to be type ItemReplyServerPacket.ItemTypeDataEffectPotion for item_type " + ItemType(data._item_type).name + ".")
                ItemReplyServerPacket.ItemTypeDataEffectPotion.serialize(writer, data._item_type_data)
            elif data._item_type == ItemType.CureCurse:
                if not isinstance(data._item_type_data, ItemReplyServerPacket.ItemTypeDataCureCurse):
                    raise SerializationError("Expected item_type_data to be type ItemReplyServerPacket.ItemTypeDataCureCurse for item_type " + ItemType(data._item_type).name + ".")
                ItemReplyServerPacket.ItemTypeDataCureCurse.serialize(writer, data._item_type_data)
            elif data._item_type == ItemType.ExpReward:
                if not isinstance(data._item_type_data, ItemReplyServerPacket.ItemTypeDataExpReward):
                    raise SerializationError("Expected item_type_data to be type ItemReplyServerPacket.ItemTypeDataExpReward for item_type " + ItemType(data._item_type).name + ".")
                ItemReplyServerPacket.ItemTypeDataExpReward.serialize(writer, data._item_type_data)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemReplyServerPacket":
        """
        Deserializes an instance of `ItemReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemReplyServerPacket: The data to serialize.
        """
        data: ItemReplyServerPacket = ItemReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._item_type = ItemType(reader.get_char())
            data._used_item = Item.deserialize(reader)
            data._weight = Weight.deserialize(reader)
            if data._item_type == ItemType.Heal:
                data._item_type_data = ItemReplyServerPacket.ItemTypeDataHeal.deserialize(reader)
            elif data._item_type == ItemType.HairDye:
                data._item_type_data = ItemReplyServerPacket.ItemTypeDataHairDye.deserialize(reader)
            elif data._item_type == ItemType.EffectPotion:
                data._item_type_data = ItemReplyServerPacket.ItemTypeDataEffectPotion.deserialize(reader)
            elif data._item_type == ItemType.CureCurse:
                data._item_type_data = ItemReplyServerPacket.ItemTypeDataCureCurse.deserialize(reader)
            elif data._item_type == ItemType.ExpReward:
                data._item_type_data = ItemReplyServerPacket.ItemTypeDataExpReward.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemReplyServerPacket(byte_size={repr(self._byte_size)}, item_type={repr(self._item_type)}, used_item={repr(self._used_item)}, weight={repr(self._weight)}, item_type_data={repr(self._item_type_data)})"

    ItemTypeData = Union['ItemReplyServerPacket.ItemTypeDataHeal', 'ItemReplyServerPacket.ItemTypeDataHairDye', 'ItemReplyServerPacket.ItemTypeDataEffectPotion', 'ItemReplyServerPacket.ItemTypeDataCureCurse', 'ItemReplyServerPacket.ItemTypeDataExpReward', None]
    """
    Data associated with different values of the `item_type` field.
    """

    class ItemTypeDataHeal:
        """
        Data associated with item_type value ItemType.Heal
        """
        _byte_size: int = 0
        _hp_gain: int = None # type: ignore [assignment]
        _hp: int = None # type: ignore [assignment]
        _tp: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def hp_gain(self) -> int:
            """
            Note:
              - Value range is 0-4097152080.
            """
            return self._hp_gain

        @hp_gain.setter
        def hp_gain(self, hp_gain: int) -> None:
            """
            Note:
              - Value range is 0-4097152080.
            """
            self._hp_gain = hp_gain

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

        @staticmethod
        def serialize(writer: EoWriter, data: "ItemReplyServerPacket.ItemTypeDataHeal") -> None:
            """
            Serializes an instance of `ItemReplyServerPacket.ItemTypeDataHeal` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (ItemReplyServerPacket.ItemTypeDataHeal): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._hp_gain is None:
                    raise SerializationError("hp_gain must be provided.")
                writer.add_int(data._hp_gain)
                if data._hp is None:
                    raise SerializationError("hp must be provided.")
                writer.add_short(data._hp)
                if data._tp is None:
                    raise SerializationError("tp must be provided.")
                writer.add_short(data._tp)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "ItemReplyServerPacket.ItemTypeDataHeal":
            """
            Deserializes an instance of `ItemReplyServerPacket.ItemTypeDataHeal` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                ItemReplyServerPacket.ItemTypeDataHeal: The data to serialize.
            """
            data: ItemReplyServerPacket.ItemTypeDataHeal = ItemReplyServerPacket.ItemTypeDataHeal()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._hp_gain = reader.get_int()
                data._hp = reader.get_short()
                data._tp = reader.get_short()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"ItemReplyServerPacket.ItemTypeDataHeal(byte_size={repr(self._byte_size)}, hp_gain={repr(self._hp_gain)}, hp={repr(self._hp)}, tp={repr(self._tp)})"

    class ItemTypeDataHairDye:
        """
        Data associated with item_type value ItemType.HairDye
        """
        _byte_size: int = 0
        _hair_color: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

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

        @staticmethod
        def serialize(writer: EoWriter, data: "ItemReplyServerPacket.ItemTypeDataHairDye") -> None:
            """
            Serializes an instance of `ItemReplyServerPacket.ItemTypeDataHairDye` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (ItemReplyServerPacket.ItemTypeDataHairDye): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._hair_color is None:
                    raise SerializationError("hair_color must be provided.")
                writer.add_char(data._hair_color)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "ItemReplyServerPacket.ItemTypeDataHairDye":
            """
            Deserializes an instance of `ItemReplyServerPacket.ItemTypeDataHairDye` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                ItemReplyServerPacket.ItemTypeDataHairDye: The data to serialize.
            """
            data: ItemReplyServerPacket.ItemTypeDataHairDye = ItemReplyServerPacket.ItemTypeDataHairDye()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._hair_color = reader.get_char()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"ItemReplyServerPacket.ItemTypeDataHairDye(byte_size={repr(self._byte_size)}, hair_color={repr(self._hair_color)})"

    class ItemTypeDataEffectPotion:
        """
        Data associated with item_type value ItemType.EffectPotion
        """
        _byte_size: int = 0
        _effect_id: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def effect_id(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._effect_id

        @effect_id.setter
        def effect_id(self, effect_id: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._effect_id = effect_id

        @staticmethod
        def serialize(writer: EoWriter, data: "ItemReplyServerPacket.ItemTypeDataEffectPotion") -> None:
            """
            Serializes an instance of `ItemReplyServerPacket.ItemTypeDataEffectPotion` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (ItemReplyServerPacket.ItemTypeDataEffectPotion): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._effect_id is None:
                    raise SerializationError("effect_id must be provided.")
                writer.add_short(data._effect_id)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "ItemReplyServerPacket.ItemTypeDataEffectPotion":
            """
            Deserializes an instance of `ItemReplyServerPacket.ItemTypeDataEffectPotion` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                ItemReplyServerPacket.ItemTypeDataEffectPotion: The data to serialize.
            """
            data: ItemReplyServerPacket.ItemTypeDataEffectPotion = ItemReplyServerPacket.ItemTypeDataEffectPotion()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._effect_id = reader.get_short()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"ItemReplyServerPacket.ItemTypeDataEffectPotion(byte_size={repr(self._byte_size)}, effect_id={repr(self._effect_id)})"

    class ItemTypeDataCureCurse:
        """
        Data associated with item_type value ItemType.CureCurse
        """
        _byte_size: int = 0
        _stats: CharacterStatsEquipmentChange = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def stats(self) -> CharacterStatsEquipmentChange:
            return self._stats

        @stats.setter
        def stats(self, stats: CharacterStatsEquipmentChange) -> None:
            self._stats = stats

        @staticmethod
        def serialize(writer: EoWriter, data: "ItemReplyServerPacket.ItemTypeDataCureCurse") -> None:
            """
            Serializes an instance of `ItemReplyServerPacket.ItemTypeDataCureCurse` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (ItemReplyServerPacket.ItemTypeDataCureCurse): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._stats is None:
                    raise SerializationError("stats must be provided.")
                CharacterStatsEquipmentChange.serialize(writer, data._stats)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "ItemReplyServerPacket.ItemTypeDataCureCurse":
            """
            Deserializes an instance of `ItemReplyServerPacket.ItemTypeDataCureCurse` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                ItemReplyServerPacket.ItemTypeDataCureCurse: The data to serialize.
            """
            data: ItemReplyServerPacket.ItemTypeDataCureCurse = ItemReplyServerPacket.ItemTypeDataCureCurse()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._stats = CharacterStatsEquipmentChange.deserialize(reader)
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"ItemReplyServerPacket.ItemTypeDataCureCurse(byte_size={repr(self._byte_size)}, stats={repr(self._stats)})"

    class ItemTypeDataExpReward:
        """
        Data associated with item_type value ItemType.ExpReward
        """
        _byte_size: int = 0
        _experience: int = None # type: ignore [assignment]
        _level_up: int = None # type: ignore [assignment]
        _stat_points: int = None # type: ignore [assignment]
        _skill_points: int = None # type: ignore [assignment]
        _max_hp: int = None # type: ignore [assignment]
        _max_tp: int = None # type: ignore [assignment]
        _max_sp: int = None # type: ignore [assignment]

        @property
        def byte_size(self) -> int:
            """
            Returns the size of the data that this was deserialized from.

            Returns:
                int: The size of the data that this was deserialized from.
            """
            return self._byte_size

        @property
        def experience(self) -> int:
            """
            Note:
              - Value range is 0-4097152080.
            """
            return self._experience

        @experience.setter
        def experience(self, experience: int) -> None:
            """
            Note:
              - Value range is 0-4097152080.
            """
            self._experience = experience

        @property
        def level_up(self) -> int:
            """
            A value greater than 0 is "new level" and indicates the player leveled up.

            Note:
              - Value range is 0-252.
            """
            return self._level_up

        @level_up.setter
        def level_up(self, level_up: int) -> None:
            """
            A value greater than 0 is "new level" and indicates the player leveled up.

            Note:
              - Value range is 0-252.
            """
            self._level_up = level_up

        @property
        def stat_points(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._stat_points

        @stat_points.setter
        def stat_points(self, stat_points: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._stat_points = stat_points

        @property
        def skill_points(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._skill_points

        @skill_points.setter
        def skill_points(self, skill_points: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._skill_points = skill_points

        @property
        def max_hp(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._max_hp

        @max_hp.setter
        def max_hp(self, max_hp: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._max_hp = max_hp

        @property
        def max_tp(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._max_tp

        @max_tp.setter
        def max_tp(self, max_tp: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._max_tp = max_tp

        @property
        def max_sp(self) -> int:
            """
            Note:
              - Value range is 0-64008.
            """
            return self._max_sp

        @max_sp.setter
        def max_sp(self, max_sp: int) -> None:
            """
            Note:
              - Value range is 0-64008.
            """
            self._max_sp = max_sp

        @staticmethod
        def serialize(writer: EoWriter, data: "ItemReplyServerPacket.ItemTypeDataExpReward") -> None:
            """
            Serializes an instance of `ItemReplyServerPacket.ItemTypeDataExpReward` to the provided `EoWriter`.

            Args:
                writer (EoWriter): The writer that the data will be serialized to.
                data (ItemReplyServerPacket.ItemTypeDataExpReward): The data to serialize.
            """
            old_string_sanitization_mode: bool = writer.string_sanitization_mode
            try:
                if data._experience is None:
                    raise SerializationError("experience must be provided.")
                writer.add_int(data._experience)
                if data._level_up is None:
                    raise SerializationError("level_up must be provided.")
                writer.add_char(data._level_up)
                if data._stat_points is None:
                    raise SerializationError("stat_points must be provided.")
                writer.add_short(data._stat_points)
                if data._skill_points is None:
                    raise SerializationError("skill_points must be provided.")
                writer.add_short(data._skill_points)
                if data._max_hp is None:
                    raise SerializationError("max_hp must be provided.")
                writer.add_short(data._max_hp)
                if data._max_tp is None:
                    raise SerializationError("max_tp must be provided.")
                writer.add_short(data._max_tp)
                if data._max_sp is None:
                    raise SerializationError("max_sp must be provided.")
                writer.add_short(data._max_sp)
            finally:
                writer.string_sanitization_mode = old_string_sanitization_mode

        @staticmethod
        def deserialize(reader: EoReader) -> "ItemReplyServerPacket.ItemTypeDataExpReward":
            """
            Deserializes an instance of `ItemReplyServerPacket.ItemTypeDataExpReward` from the provided `EoReader`.

            Args:
                reader (EoReader): The writer that the data will be serialized to.

            Returns:
                ItemReplyServerPacket.ItemTypeDataExpReward: The data to serialize.
            """
            data: ItemReplyServerPacket.ItemTypeDataExpReward = ItemReplyServerPacket.ItemTypeDataExpReward()
            old_chunked_reading_mode: bool = reader.chunked_reading_mode
            try:
                reader_start_position: int = reader.position
                data._experience = reader.get_int()
                data._level_up = reader.get_char()
                data._stat_points = reader.get_short()
                data._skill_points = reader.get_short()
                data._max_hp = reader.get_short()
                data._max_tp = reader.get_short()
                data._max_sp = reader.get_short()
                data._byte_size = reader.position - reader_start_position
                return data
            finally:
                reader.chunked_reading_mode = old_chunked_reading_mode

        def __repr__(self):
            return f"ItemReplyServerPacket.ItemTypeDataExpReward(byte_size={repr(self._byte_size)}, experience={repr(self._experience)}, level_up={repr(self._level_up)}, stat_points={repr(self._stat_points)}, skill_points={repr(self._skill_points)}, max_hp={repr(self._max_hp)}, max_tp={repr(self._max_tp)}, max_sp={repr(self._max_sp)})"
