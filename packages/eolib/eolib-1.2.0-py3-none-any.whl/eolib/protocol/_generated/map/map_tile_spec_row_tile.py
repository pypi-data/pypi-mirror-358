# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .map_tile_spec import MapTileSpec
from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class MapTileSpecRowTile:
    """
    A single tile in a row of tilespecs
    """
    _byte_size: int = 0
    _x: int = None # type: ignore [assignment]
    _tile_spec: MapTileSpec = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def x(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._x

    @x.setter
    def x(self, x: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._x = x

    @property
    def tile_spec(self) -> MapTileSpec:
        return self._tile_spec

    @tile_spec.setter
    def tile_spec(self, tile_spec: MapTileSpec) -> None:
        self._tile_spec = tile_spec

    @staticmethod
    def serialize(writer: EoWriter, data: "MapTileSpecRowTile") -> None:
        """
        Serializes an instance of `MapTileSpecRowTile` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (MapTileSpecRowTile): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._x is None:
                raise SerializationError("x must be provided.")
            writer.add_char(data._x)
            if data._tile_spec is None:
                raise SerializationError("tile_spec must be provided.")
            writer.add_char(int(data._tile_spec))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "MapTileSpecRowTile":
        """
        Deserializes an instance of `MapTileSpecRowTile` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            MapTileSpecRowTile: The data to serialize.
        """
        data: MapTileSpecRowTile = MapTileSpecRowTile()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._x = reader.get_char()
            data._tile_spec = MapTileSpec(reader.get_char())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"MapTileSpecRowTile(byte_size={repr(self._byte_size)}, x={repr(self._x)}, tile_spec={repr(self._tile_spec)})"
