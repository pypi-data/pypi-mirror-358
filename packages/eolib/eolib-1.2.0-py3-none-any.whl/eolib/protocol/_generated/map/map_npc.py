# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapNpc:
    """
    NPC spawn EMF entity
    """
    _byte_size: int = 0
    _coords: Coords = None # type: ignore [assignment]
    _id: int = None # type: ignore [assignment]
    _spawn_type: int = None # type: ignore [assignment]
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
    def id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._id = id

    @property
    def spawn_type(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._spawn_type

    @spawn_type.setter
    def spawn_type(self, spawn_type: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._spawn_type = spawn_type

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
          - Value range is 0-252.
        """
        return self._amount

    @amount.setter
    def amount(self, amount: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._amount = amount

    @staticmethod
    def serialize(writer: EoWriter, data: "MapNpc") -> None:
        """
        Serializes an instance of `MapNpc` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapNpc): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._spawn_type is None:
                raise SerializationError("spawn_type must be provided.")
            writer.add_char(data._spawn_type)
            if data._spawn_time is None:
                raise SerializationError("spawn_time must be provided.")
            writer.add_short(data._spawn_time)
            if data._amount is None:
                raise SerializationError("amount must be provided.")
            writer.add_char(data._amount)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapNpc":
        """
        Deserializes an instance of `MapNpc` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapNpc: The data to serialize.
        """
        data: MapNpc = MapNpc()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._coords = Coords.deserialize(reader)
            data._id = reader.get_short()
            data._spawn_type = reader.get_char()
            data._spawn_time = reader.get_short()
            data._amount = reader.get_char()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapNpc(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, id={repr(self._id)}, spawn_type={repr(self._spawn_type)}, spawn_time={repr(self._spawn_time)}, amount={repr(self._amount)})"
