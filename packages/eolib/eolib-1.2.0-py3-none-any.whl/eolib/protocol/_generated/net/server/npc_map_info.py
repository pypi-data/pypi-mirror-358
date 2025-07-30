# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcMapInfo:
    """
    Information about a nearby NPC
    """
    _byte_size: int = 0
    _index: int = None # type: ignore [assignment]
    _id: int = None # type: ignore [assignment]
    _coords: Coords = None # type: ignore [assignment]
    _direction: Direction = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def index(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._index

    @index.setter
    def index(self, index: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._index = index

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
    def coords(self) -> Coords:
        return self._coords

    @coords.setter
    def coords(self, coords: Coords) -> None:
        self._coords = coords

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, direction: Direction) -> None:
        self._direction = direction

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcMapInfo") -> None:
        """
        Serializes an instance of `NpcMapInfo` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcMapInfo): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._index is None:
                raise SerializationError("index must be provided.")
            writer.add_char(data._index)
            if data._id is None:
                raise SerializationError("id must be provided.")
            writer.add_short(data._id)
            if data._coords is None:
                raise SerializationError("coords must be provided.")
            Coords.serialize(writer, data._coords)
            if data._direction is None:
                raise SerializationError("direction must be provided.")
            writer.add_char(int(data._direction))
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcMapInfo":
        """
        Deserializes an instance of `NpcMapInfo` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcMapInfo: The data to serialize.
        """
        data: NpcMapInfo = NpcMapInfo()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._index = reader.get_char()
            data._id = reader.get_short()
            data._coords = Coords.deserialize(reader)
            data._direction = Direction(reader.get_char())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcMapInfo(byte_size={repr(self._byte_size)}, index={repr(self._index)}, id={repr(self._id)}, coords={repr(self._coords)}, direction={repr(self._direction)})"
