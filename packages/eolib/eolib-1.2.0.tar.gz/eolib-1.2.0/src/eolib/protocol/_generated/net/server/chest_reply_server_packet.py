# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..weight import Weight
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ChestReplyServerPacket(Packet):
    """
    Reply to placing an item in to a chest
    """
    _byte_size: int = 0
    _added_item_id: int = None # type: ignore [assignment]
    _remaining_amount: int = None # type: ignore [assignment]
    _weight: Weight = None # type: ignore [assignment]
    _items: list[ThreeItem] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def added_item_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._added_item_id

    @added_item_id.setter
    def added_item_id(self, added_item_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._added_item_id = added_item_id

    @property
    def remaining_amount(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._remaining_amount

    @remaining_amount.setter
    def remaining_amount(self, remaining_amount: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._remaining_amount = remaining_amount

    @property
    def weight(self) -> Weight:
        return self._weight

    @weight.setter
    def weight(self, weight: Weight) -> None:
        self._weight = weight

    @property
    def items(self) -> list[ThreeItem]:
        return self._items

    @items.setter
    def items(self, items: list[ThreeItem]) -> None:
        self._items = items

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Chest

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
        ChestReplyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ChestReplyServerPacket") -> None:
        """
        Serializes an instance of `ChestReplyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ChestReplyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._added_item_id is None:
                raise SerializationError("added_item_id must be provided.")
            writer.add_short(data._added_item_id)
            if data._remaining_amount is None:
                raise SerializationError("remaining_amount must be provided.")
            writer.add_int(data._remaining_amount)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
            if data._items is None:
                raise SerializationError("items must be provided.")
            for i in range(len(data._items)):
                ThreeItem.serialize(writer, data._items[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ChestReplyServerPacket":
        """
        Deserializes an instance of `ChestReplyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ChestReplyServerPacket: The data to serialize.
        """
        data: ChestReplyServerPacket = ChestReplyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._added_item_id = reader.get_short()
            data._remaining_amount = reader.get_int()
            data._weight = Weight.deserialize(reader)
            items_length = int(reader.remaining / 5)
            data._items = []
            for i in range(items_length):
                data._items.append(ThreeItem.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ChestReplyServerPacket(byte_size={repr(self._byte_size)}, added_item_id={repr(self._added_item_id)}, remaining_amount={repr(self._remaining_amount)}, weight={repr(self._weight)}, items={repr(self._items)})"
