# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..weight import Weight
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class LockerReplyServerPacket(Packet):
    """
    Response to adding an item to a bank locker
    """
    _byte_size: int = 0
    _deposited_item: Item = None # type: ignore [assignment]
    _weight: Weight = None # type: ignore [assignment]
    _locker_items: list[ThreeItem] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def deposited_item(self) -> Item:
        return self._deposited_item

    @deposited_item.setter
    def deposited_item(self, deposited_item: Item) -> None:
        self._deposited_item = deposited_item

    @property
    def weight(self) -> Weight:
        return self._weight

    @weight.setter
    def weight(self, weight: Weight) -> None:
        self._weight = weight

    @property
    def locker_items(self) -> list[ThreeItem]:
        return self._locker_items

    @locker_items.setter
    def locker_items(self, locker_items: list[ThreeItem]) -> None:
        self._locker_items = locker_items

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Locker

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
        LockerReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "LockerReplyServerPacket") -> None:
        """
        Serializes an instance of `LockerReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (LockerReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._deposited_item is None:
                raise SerializationError("deposited_item must be provided.")
            Item.serialize(writer, data._deposited_item)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
            if data._locker_items is None:
                raise SerializationError("locker_items must be provided.")
            for i in range(len(data._locker_items)):
                ThreeItem.serialize(writer, data._locker_items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "LockerReplyServerPacket":
        """
        Deserializes an instance of `LockerReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            LockerReplyServerPacket: The data to serialize.
        """
        data: LockerReplyServerPacket = LockerReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._deposited_item = Item.deserialize(reader)
            data._weight = Weight.deserialize(reader)
            locker_items_length = int(reader.remaining / 5)
            data._locker_items = []
            for i in range(locker_items_length):
                data._locker_items.append(ThreeItem.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"LockerReplyServerPacket(byte_size={repr(self._byte_size)}, deposited_item={repr(self._deposited_item)}, weight={repr(self._weight)}, locker_items={repr(self._locker_items)})"
