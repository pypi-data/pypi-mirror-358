# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapItem:
    """
    Item spawn EMF entity
    """
    _byte_size: int = 0
    _coords: Coords = None # type: ignore [assignment]
    _key: int = None # type: ignore [assignment]
    _chest_slot: int = None # type: ignore [assignment]
    _item_id: int = None # type: ignore [assignment]
    _spawn_time: int = None # type: ignore [assignment]
    _amount: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def coords(self) -> Coords:
        return self._coords

    @coords.setter
    def coords(self, coords: Coords) -> None:
        self._coords = coords

    @property
    def key(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._key

    @key.setter
    def key(self, key: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._key = key

    @property
    def chest_slot(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._chest_slot

    @chest_slot.setter
    def chest_slot(self, chest_slot: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._chest_slot = chest_slot

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
    def spawn_time(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._spawn_time

    @spawn_time.setter
    def spawn_time(self, spawn_time: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._spawn_time = spawn_time

    @property
    def amount(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._amount

    @amount.setter
    def amount(self, amount: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._amount = amount

    @staticmethod
    def serialize(writer: EoWriter, data: "MapItem") -> None:
        """
        Serializes an instance of `MapItem` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapItem): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._key is None:
                raise SerializationError("key must be provided.")
            writer.add_short(data._key)
            if data._chest_slot is None:
                raise SerializationError("chest_slot must be provided.")
            writer.add_char(data._chest_slot)
            if data._item_id is None:
                raise SerializationError("item_id must be provided.")
            writer.add_short(data._item_id)
            if data._spawn_time is None:
                raise SerializationError("spawn_time must be provided.")
            writer.add_short(data._spawn_time)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_three(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapItem":
        """
        Deserializes an instance of `MapItem` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapItem: The data to serialize.
        """
        data: MapItem = MapItem()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._coords = Coords.deserialize(reader)
            data._key = reader.get_short()
            data._chest_slot = reader.get_char()
            data._item_id = reader.get_short()
            data._spawn_time = reader.get_short()
            data._amount = reader.get_three()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapItem(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, key={repr(self._key)}, chest_slot={repr(self._chest_slot)}, item_id={repr(self._item_id)}, spawn_time={repr(self._spawn_time)}, amount={repr(self._amount)})"
