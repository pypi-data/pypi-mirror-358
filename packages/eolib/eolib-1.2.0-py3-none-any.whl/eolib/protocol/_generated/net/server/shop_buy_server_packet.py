# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..weight import Weight
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopBuyServerPacket(Packet):
    """
    Response to purchasing an item from a shop
    """
    _byte_size: int = 0
    _gold_amount: int = None # type: ignore [assignment]
    _bought_item: Item = None # type: ignore [assignment]
    _weight: Weight = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def gold_amount(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._gold_amount

    @gold_amount.setter
    def gold_amount(self, gold_amount: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._gold_amount = gold_amount

    @property
    def bought_item(self) -> Item:
        return self._bought_item

    @bought_item.setter
    def bought_item(self, bought_item: Item) -> None:
        self._bought_item = bought_item

    @property
    def weight(self) -> Weight:
        return self._weight

    @weight.setter
    def weight(self, weight: Weight) -> None:
        self._weight = weight

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Shop

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Buy

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ShopBuyServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopBuyServerPacket") -> None:
        """
        Serializes an instance of `ShopBuyServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopBuyServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._gold_amount is None:
                raise SerializationError("gold_amount must be provided.")
            writer.add_int(data._gold_amount)
            if data._bought_item is None:
                raise SerializationError("bought_item must be provided.")
            Item.serialize(writer, data._bought_item)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopBuyServerPacket":
        """
        Deserializes an instance of `ShopBuyServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopBuyServerPacket: The data to serialize.
        """
        data: ShopBuyServerPacket = ShopBuyServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._gold_amount = reader.get_int()
            data._bought_item = Item.deserialize(reader)
            data._weight = Weight.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopBuyServerPacket(byte_size={repr(self._byte_size)}, gold_amount={repr(self._gold_amount)}, bought_item={repr(self._bought_item)}, weight={repr(self._weight)})"
