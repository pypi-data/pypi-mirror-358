# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopTradeItem:
    """
    An item that a shop can buy or sell
    """
    _byte_size: int = 0
    _item_id: int = None # type: ignore [assignment]
    _buy_price: int = None # type: ignore [assignment]
    _sell_price: int = None # type: ignore [assignment]
    _max_buy_amount: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

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
    def buy_price(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._buy_price

    @buy_price.setter
    def buy_price(self, buy_price: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._buy_price = buy_price

    @property
    def sell_price(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._sell_price

    @sell_price.setter
    def sell_price(self, sell_price: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._sell_price = sell_price

    @property
    def max_buy_amount(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._max_buy_amount

    @max_buy_amount.setter
    def max_buy_amount(self, max_buy_amount: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._max_buy_amount = max_buy_amount

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopTradeItem") -> None:
        """
        Serializes an instance of `ShopTradeItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopTradeItem): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._buy_price is None:
                raise SerializationError("buy_price must be provided.")
            writer.add_three(data._buy_price)
            if data._sell_price is None:
                raise SerializationError("sell_price must be provided.")
            writer.add_three(data._sell_price)
            if data._max_buy_amount is None:
                raise SerializationError("max_buy_amount must be provided.")
            writer.add_char(data._max_buy_amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopTradeItem":
        """
        Deserializes an instance of `ShopTradeItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopTradeItem: The data to serialize.
        """
        data: ShopTradeItem = ShopTradeItem()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._item_id = reader.get_short()
            data._buy_price = reader.get_three()
            data._sell_price = reader.get_three()
            data._max_buy_amount = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopTradeItem(byte_size={repr(self._byte_size)}, item_id={repr(self._item_id)}, buy_price={repr(self._buy_price)}, sell_price={repr(self._sell_price)}, max_buy_amount={repr(self._max_buy_amount)})"
