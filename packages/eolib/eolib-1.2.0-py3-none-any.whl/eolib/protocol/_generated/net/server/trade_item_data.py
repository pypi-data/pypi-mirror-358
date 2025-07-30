# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..item import Item
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class TradeItemData:
    """
    Trade window item data
    """
    _byte_size: int = 0
    _partner_player_id: int = None # type: ignore [assignment]
    _partner_items: list[Item] = None # type: ignore [assignment]
    _your_player_id: int = None # type: ignore [assignment]
    _your_items: list[Item] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def partner_player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._partner_player_id

    @partner_player_id.setter
    def partner_player_id(self, partner_player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._partner_player_id = partner_player_id

    @property
    def partner_items(self) -> list[Item]:
        return self._partner_items

    @partner_items.setter
    def partner_items(self, partner_items: list[Item]) -> None:
        self._partner_items = partner_items

    @property
    def your_player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._your_player_id

    @your_player_id.setter
    def your_player_id(self, your_player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._your_player_id = your_player_id

    @property
    def your_items(self) -> list[Item]:
        return self._your_items

    @your_items.setter
    def your_items(self, your_items: list[Item]) -> None:
        self._your_items = your_items

    @staticmethod
    def serialize(writer: EoWriter, data: "TradeItemData") -> None:
        """
        Serializes an instance of `TradeItemData` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (TradeItemData): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._partner_player_id is None:
                raise SerializationError("partner_player_id must be provided.")
            writer.add_short(data._partner_player_id)
            if data._partner_items is None:
                raise SerializationError("partner_items must be provided.")
            for i in range(len(data._partner_items)):
                Item.serialize(writer, data._partner_items[i])
            writer.add_byte(0xFF)
            if data._your_player_id is None:
                raise SerializationError("your_player_id must be provided.")
            writer.add_short(data._your_player_id)
            if data._your_items is None:
                raise SerializationError("your_items must be provided.")
            for i in range(len(data._your_items)):
                Item.serialize(writer, data._your_items[i])
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "TradeItemData":
        """
        Deserializes an instance of `TradeItemData` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            TradeItemData: The data to serialize.
        """
        data: TradeItemData = TradeItemData()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._partner_player_id = reader.get_short()
            partner_items_length = int(reader.remaining / 6)
            data._partner_items = []
            for i in range(partner_items_length):
                data._partner_items.append(Item.deserialize(reader))
            reader.next_chunk()
            data._your_player_id = reader.get_short()
            your_items_length = int(reader.remaining / 6)
            data._your_items = []
            for i in range(your_items_length):
                data._your_items.append(Item.deserialize(reader))
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"TradeItemData(byte_size={repr(self._byte_size)}, partner_player_id={repr(self._partner_player_id)}, partner_items={repr(self._partner_items)}, your_player_id={repr(self._your_player_id)}, your_items={repr(self._your_items)})"
