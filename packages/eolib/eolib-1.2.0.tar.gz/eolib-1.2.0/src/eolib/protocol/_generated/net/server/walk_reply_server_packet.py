# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .item_map_info import ItemMapInfo
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class WalkReplyServerPacket(Packet):
    """
    Players, NPCs, and Items appearing in nearby view
    """
    _byte_size: int = 0
    _player_ids: list[int] = None # type: ignore [assignment]
    _npc_indexes: list[int] = None # type: ignore [assignment]
    _items: list[ItemMapInfo] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def player_ids(self) -> list[int]:
        """
        Note:
          - Element value range is 0-64008.
        """
        return self._player_ids

    @player_ids.setter
    def player_ids(self, player_ids: list[int]) -> None:
        """
        Note:
          - Element value range is 0-64008.
        """
        self._player_ids = player_ids

    @property
    def npc_indexes(self) -> list[int]:
        """
        Note:
          - Element value range is 0-252.
        """
        return self._npc_indexes

    @npc_indexes.setter
    def npc_indexes(self, npc_indexes: list[int]) -> None:
        """
        Note:
          - Element value range is 0-252.
        """
        self._npc_indexes = npc_indexes

    @property
    def items(self) -> list[ItemMapInfo]:
        return self._items

    @items.setter
    def items(self, items: list[ItemMapInfo]) -> None:
        self._items = items

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Walk

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
        WalkReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "WalkReplyServerPacket") -> None:
        """
        Serializes an instance of `WalkReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (WalkReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._player_ids is None:
                raise SerializationError("player_ids must be provided.")
            for i in range(len(data._player_ids)):
                writer.add_short(data._player_ids[i])
            writer.add_byte(0xFF)
            if data._npc_indexes is None:
                raise SerializationError("npc_indexes must be provided.")
            for i in range(len(data._npc_indexes)):
                writer.add_char(data._npc_indexes[i])
            writer.add_byte(0xFF)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                ItemMapInfo.serialize(writer, data._items[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "WalkReplyServerPacket":
        """
        Deserializes an instance of `WalkReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            WalkReplyServerPacket: The data to serialize.
        """
        data: WalkReplyServerPacket = WalkReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            player_ids_length = int(reader.remaining / 2)
            data._player_ids = []
            for i in range(player_ids_length):
                data._player_ids.append(reader.get_short())
            reader.next_chunk()
            npc_indexes_length = int(reader.remaining / 1)
            data._npc_indexes = []
            for i in range(npc_indexes_length):
                data._npc_indexes.append(reader.get_char())
            reader.next_chunk()
            items_length = int(reader.remaining / 9)
            data._items = []
            for i in range(items_length):
                data._items.append(ItemMapInfo.deserialize(reader))
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"WalkReplyServerPacket(byte_size={repr(self._byte_size)}, player_ids={repr(self._player_ids)}, npc_indexes={repr(self._npc_indexes)}, items={repr(self._items)})"
