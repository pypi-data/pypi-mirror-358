# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ItemObtainServerPacket(Packet):
    """
    Receive item (from quest)
    """
    _byte_size: int = 0
    _item: ThreeItem = None # type: ignore [assignment]
    _current_weight: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def item(self) -> ThreeItem:
        return self._item

    @item.setter
    def item(self, item: ThreeItem) -> None:
        self._item = item

    @property
    def current_weight(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._current_weight

    @current_weight.setter
    def current_weight(self, current_weight: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._current_weight = current_weight

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
        return PacketAction.Obtain

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ItemObtainServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ItemObtainServerPacket") -> None:
        """
        Serializes an instance of `ItemObtainServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ItemObtainServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item is None:
                raise SerializationError("item must be provided.")
            ThreeItem.serialize(writer, data._item)
            if data._current_weight is None:
                raise SerializationError("current_weight must be provided.")
            writer.add_char(data._current_weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ItemObtainServerPacket":
        """
        Deserializes an instance of `ItemObtainServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ItemObtainServerPacket: The data to serialize.
        """
        data: ItemObtainServerPacket = ItemObtainServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._item = ThreeItem.deserialize(reader)
            data._current_weight = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ItemObtainServerPacket(byte_size={repr(self._byte_size)}, item={repr(self._item)}, current_weight={repr(self._current_weight)})"
