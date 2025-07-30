# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .shop_trade_item import ShopTradeItem
from .shop_craft_item import ShopCraftItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopOpenServerPacket(Packet):
    """
    Response from talking to a shop NPC
    """
    _byte_size: int = 0
    _session_id: int = None # type: ignore [assignment]
    _shop_name: str = None # type: ignore [assignment]
    _trade_items: list[ShopTradeItem] = None # type: ignore [assignment]
    _craft_items: list[ShopCraftItem] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def session_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._session_id

    @session_id.setter
    def session_id(self, session_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._session_id = session_id

    @property
    def shop_name(self) -> str:
        return self._shop_name

    @shop_name.setter
    def shop_name(self, shop_name: str) -> None:
        self._shop_name = shop_name

    @property
    def trade_items(self) -> list[ShopTradeItem]:
        return self._trade_items

    @trade_items.setter
    def trade_items(self, trade_items: list[ShopTradeItem]) -> None:
        self._trade_items = trade_items

    @property
    def craft_items(self) -> list[ShopCraftItem]:
        return self._craft_items

    @craft_items.setter
    def craft_items(self, craft_items: list[ShopCraftItem]) -> None:
        self._craft_items = craft_items

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
        return PacketAction.Open

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        ShopOpenServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopOpenServerPacket") -> None:
        """
        Serializes an instance of `ShopOpenServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopOpenServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._session_id is None:
                raise SerializationError("session_id must be provided.")
            writer.add_short(data._session_id)
            if data._shop_name is None:
                raise SerializationError("shop_name must be provided.")
            writer.add_string(data._shop_name)
            writer.add_byte(0xFF)
            if data._trade_items is None:
                raise SerializationError("trade_items must be provided.")
            for i in range(len(data._trade_items)):
                ShopTradeItem.serialize(writer, data._trade_items[i])
            writer.add_byte(0xFF)
            if data._craft_items is None:
                raise SerializationError("craft_items must be provided.")
            for i in range(len(data._craft_items)):
                ShopCraftItem.serialize(writer, data._craft_items[i])
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopOpenServerPacket":
        """
        Deserializes an instance of `ShopOpenServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopOpenServerPacket: The data to serialize.
        """
        data: ShopOpenServerPacket = ShopOpenServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._session_id = reader.get_short()
            data._shop_name = reader.get_string()
            reader.next_chunk()
            trade_items_length = int(reader.remaining / 9)
            data._trade_items = []
            for i in range(trade_items_length):
                data._trade_items.append(ShopTradeItem.deserialize(reader))
            reader.next_chunk()
            craft_items_length = int(reader.remaining / 14)
            data._craft_items = []
            for i in range(craft_items_length):
                data._craft_items.append(ShopCraftItem.deserialize(reader))
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopOpenServerPacket(byte_size={repr(self._byte_size)}, session_id={repr(self._session_id)}, shop_name={repr(self._shop_name)}, trade_items={repr(self._trade_items)}, craft_items={repr(self._craft_items)})"
