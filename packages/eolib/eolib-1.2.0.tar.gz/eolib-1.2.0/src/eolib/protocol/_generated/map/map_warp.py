# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapWarp:
    """
    Warp EMF entity
    """
    _byte_size: int = 0
    _destination_map: int = None # type: ignore [assignment]
    _destination_coords: Coords = None # type: ignore [assignment]
    _level_required: int = None # type: ignore [assignment]
    _door: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def destination_map(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._destination_map

    @destination_map.setter
    def destination_map(self, destination_map: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._destination_map = destination_map

    @property
    def destination_coords(self) -> Coords:
        return self._destination_coords

    @destination_coords.setter
    def destination_coords(self, destination_coords: Coords) -> None:
        self._destination_coords = destination_coords

    @property
    def level_required(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._level_required

    @level_required.setter
    def level_required(self, level_required: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._level_required = level_required

    @property
    def door(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._door

    @door.setter
    def door(self, door: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._door = door

    @staticmethod
    def serialize(writer: EoWriter, data: "MapWarp") -> None:
        """
        Serializes an instance of `MapWarp` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapWarp): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._destination_map is None:
                raise SerializationError("destination_map must be provided.")
            writer.add_short(data._destination_map)
            if data._destination_coords is None:
                raise SerializationError("destination_coords must be provided.")
            Coords.serialize(writer, data._destination_coords)
            if data._level_required is None:
                raise SerializationError("level_required must be provided.")
            writer.add_char(data._level_required)
            if data._door is None:
                raise SerializationError("door must be provided.")
            writer.add_short(data._door)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapWarp":
        """
        Deserializes an instance of `MapWarp` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapWarp: The data to serialize.
        """
        data: MapWarp = MapWarp()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._destination_map = reader.get_short()
            data._destination_coords = Coords.deserialize(reader)
            data._level_required = reader.get_char()
            data._door = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapWarp(byte_size={repr(self._byte_size)}, destination_map={repr(self._destination_map)}, destination_coords={repr(self._destination_coords)}, level_required={repr(self._level_required)}, door={repr(self._door)})"
