# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .shop_trade_record import ShopTradeRecord
from .shop_craft_record import ShopCraftRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class ShopRecord:
    """
    Record of Shop data in an Endless Shop File
    """
    _byte_size: int = 0
    _behavior_id: int = None # type: ignore [assignment]
    _name_length: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _min_level: int = None # type: ignore [assignment]
    _max_level: int = None # type: ignore [assignment]
    _class_requirement: int = None # type: ignore [assignment]
    _trades_count: int = None # type: ignore [assignment]
    _crafts_count: int = None # type: ignore [assignment]
    _trades: list[ShopTradeRecord] = None # type: ignore [assignment]
    _crafts: list[ShopCraftRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, behavior_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._behavior_id = behavior_id

    @property
    def name(self) -> str:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._name = name
        self._name_length = len(self._name)

    @property
    def min_level(self) -> int:
        """
        Minimum level required to use this shop

        Note:
          - Value range is 0-252.
        """
        return self._min_level

    @min_level.setter
    def min_level(self, min_level: int) -> None:
        """
        Minimum level required to use this shop

        Note:
          - Value range is 0-252.
        """
        self._min_level = min_level

    @property
    def max_level(self) -> int:
        """
        Maximum level allowed to use this shop

        Note:
          - Value range is 0-252.
        """
        return self._max_level

    @max_level.setter
    def max_level(self, max_level: int) -> None:
        """
        Maximum level allowed to use this shop

        Note:
          - Value range is 0-252.
        """
        self._max_level = max_level

    @property
    def class_requirement(self) -> int:
        """
        Class required to use this shop

        Note:
          - Value range is 0-252.
        """
        return self._class_requirement

    @class_requirement.setter
    def class_requirement(self, class_requirement: int) -> None:
        """
        Class required to use this shop

        Note:
          - Value range is 0-252.
        """
        self._class_requirement = class_requirement

    @property
    def trades(self) -> list[ShopTradeRecord]:
        """
        Note:
          - Length must be 64008 or less.
        """
        return self._trades

    @trades.setter
    def trades(self, trades: list[ShopTradeRecord]) -> None:
        """
        Note:
          - Length must be 64008 or less.
        """
        self._trades = trades
        self._trades_count = len(self._trades)

    @property
    def crafts(self) -> list[ShopCraftRecord]:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._crafts

    @crafts.setter
    def crafts(self, crafts: list[ShopCraftRecord]) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._crafts = crafts
        self._crafts_count = len(self._crafts)

    @staticmethod
    def serialize(writer: EoWriter, data: "ShopRecord") -> None:
        """
        Serializes an instance of `ShopRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (ShopRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._min_level is None:
                raise SerializationError("min_level must be provided.")
            writer.add_char(data._min_level)
            if data._max_level is None:
                raise SerializationError("max_level must be provided.")
            writer.add_char(data._max_level)
            if data._class_requirement is None:
                raise SerializationError("class_requirement must be provided.")
            writer.add_char(data._class_requirement)
            if data._trades_count is None:
                raise SerializationError("trades_count must be provided.")
            writer.add_short(data._trades_count)
            if data._crafts_count is None:
                raise SerializationError("crafts_count must be provided.")
            writer.add_char(data._crafts_count)
            if data._trades is None:
                raise SerializationError("trades must be provided.")
            if len(data._trades) > 64008:
                raise SerializationError(f"Expected length of trades to be 64008 or less, got {len(data._trades)}.")
            for i in range(data._trades_count):
                ShopTradeRecord.serialize(writer, data._trades[i])
            if data._crafts is None:
                raise SerializationError("crafts must be provided.")
            if len(data._crafts) > 252:
                raise SerializationError(f"Expected length of crafts to be 252 or less, got {len(data._crafts)}.")
            for i in range(data._crafts_count):
                ShopCraftRecord.serialize(writer, data._crafts[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "ShopRecord":
        """
        Deserializes an instance of `ShopRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            ShopRecord: The data to serialize.
        """
        data: ShopRecord = ShopRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._behavior_id = reader.get_short()
            data._name_length = reader.get_char()
            data._name = reader.get_fixed_string(data._name_length, False)
            data._min_level = reader.get_char()
            data._max_level = reader.get_char()
            data._class_requirement = reader.get_char()
            data._trades_count = reader.get_short()
            data._crafts_count = reader.get_char()
            data._trades = []
            for i in range(data._trades_count):
                data._trades.append(ShopTradeRecord.deserialize(reader))
            data._crafts = []
            for i in range(data._crafts_count):
                data._crafts.append(ShopCraftRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"ShopRecord(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, name={repr(self._name)}, min_level={repr(self._min_level)}, max_level={repr(self._max_level)}, class_requirement={repr(self._class_requirement)}, trades={repr(self._trades)}, crafts={repr(self._crafts)})"
