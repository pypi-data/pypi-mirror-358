# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..coords import Coords
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapLegacyDoorKey:
    """
    Legacy EMF entity used to specify a key on a door
    """
    _byte_size: int = 0
    _coords: Coords = None # type: ignore [assignment]
    _key: int = None # type: ignore [assignment]

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

    @staticmethod
    def serialize(writer: EoWriter, data: "MapLegacyDoorKey") -> None:
        """
        Serializes an instance of `MapLegacyDoorKey` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapLegacyDoorKey): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._key is None:
                raise SerializationError("key must be provided.")
            writer.add_short(data._key)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapLegacyDoorKey":
        """
        Deserializes an instance of `MapLegacyDoorKey` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapLegacyDoorKey: The data to serialize.
        """
        data: MapLegacyDoorKey = MapLegacyDoorKey()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._coords = Coords.deserialize(reader)
            data._key = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapLegacyDoorKey(byte_size={repr(self._byte_size)}, coords={repr(self._coords)}, key={repr(self._key)})"
