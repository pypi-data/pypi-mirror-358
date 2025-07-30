# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_stats_equipment_change import CharacterStatsEquipmentChange
from .avatar_change import AvatarChange
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class PaperdollRemoveServerPacket(Packet):
    """
    Reply to unequipping an item
    """
    _byte_size: int = 0
    _change: AvatarChange = None # type: ignore [assignment]
    _item_id: int = None # type: ignore [assignment]
    _sub_loc: int = None # type: ignore [assignment]
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
    def change(self) -> AvatarChange:
        return self._change

    @change.setter
    def change(self, change: AvatarChange) -> None:
        self._change = change

    @property
    def item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._item_id

    @item_id.setter
    def item_id(self, item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._item_id = item_id

    @property
    def sub_loc(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._sub_loc

    @sub_loc.setter
    def sub_loc(self, sub_loc: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._sub_loc = sub_loc

    @property
    def stats(self) -> CharacterStatsEquipmentChange:
        return self._stats

    @stats.setter
    def stats(self, stats: CharacterStatsEquipmentChange) -> None:
        self._stats = stats

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Paperdoll

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Remove

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        PaperdollRemoveServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "PaperdollRemoveServerPacket") -> None:
        """
        Serializes an instance of `PaperdollRemoveServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (PaperdollRemoveServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._change is None:
                raise SerializationError("change must be provided.")
            AvatarChange.serialize(writer, data._change)
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._sub_loc is None:
                raise SerializationError("sub_loc must be provided.")
            writer.add_char(data._sub_loc)
            if data._stats is None:
                raise SerializationError("stats must be provided.")
            CharacterStatsEquipmentChange.serialize(writer, data._stats)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "PaperdollRemoveServerPacket":
        """
        Deserializes an instance of `PaperdollRemoveServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            PaperdollRemoveServerPacket: The data to serialize.
        """
        data: PaperdollRemoveServerPacket = PaperdollRemoveServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._change = AvatarChange.deserialize(reader)
            data._item_id = reader.get_short()
            data._sub_loc = reader.get_char()
            data._stats = CharacterStatsEquipmentChange.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"PaperdollRemoveServerPacket(byte_size={repr(self._byte_size)}, change={repr(self._change)}, item_id={repr(self._item_id)}, sub_loc={repr(self._sub_loc)}, stats={repr(self._stats)})"
