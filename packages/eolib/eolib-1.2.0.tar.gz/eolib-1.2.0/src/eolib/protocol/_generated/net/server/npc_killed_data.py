# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...direction import Direction
from ...coords import Coords
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class NpcKilledData:
    """
    Information about an NPC that has been killed
    """
    _byte_size: int = 0
    _killer_id: int = None # type: ignore [assignment]
    _killer_direction: Direction = None # type: ignore [assignment]
    _npc_index: int = None # type: ignore [assignment]
    _drop_index: int = None # type: ignore [assignment]
    _drop_id: int = None # type: ignore [assignment]
    _drop_coords: Coords = None # type: ignore [assignment]
    _drop_amount: int = None # type: ignore [assignment]
    _damage: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def killer_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._killer_id

    @killer_id.setter
    def killer_id(self, killer_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._killer_id = killer_id

    @property
    def killer_direction(self) -> Direction:
        return self._killer_direction

    @killer_direction.setter
    def killer_direction(self, killer_direction: Direction) -> None:
        self._killer_direction = killer_direction

    @property
    def npc_index(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._npc_index

    @npc_index.setter
    def npc_index(self, npc_index: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._npc_index = npc_index

    @property
    def drop_index(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._drop_index

    @drop_index.setter
    def drop_index(self, drop_index: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._drop_index = drop_index

    @property
    def drop_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._drop_id

    @drop_id.setter
    def drop_id(self, drop_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._drop_id = drop_id

    @property
    def drop_coords(self) -> Coords:
        return self._drop_coords

    @drop_coords.setter
    def drop_coords(self, drop_coords: Coords) -> None:
        self._drop_coords = drop_coords

    @property
    def drop_amount(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._drop_amount

    @drop_amount.setter
    def drop_amount(self, drop_amount: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._drop_amount = drop_amount

    @property
    def damage(self) -> int:
        """
        Note:
          - Value range is 0-16194276.
        """
        return self._damage

    @damage.setter
    def damage(self, damage: int) -> None:
        """
        Note:
          - Value range is 0-16194276.
        """
        self._damage = damage

    @staticmethod
    def serialize(writer: EoWriter, data: "NpcKilledData") -> None:
        """
        Serializes an instance of `NpcKilledData` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (NpcKilledData): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._killer_id is None:
                raise SerializationError("killer_id must be provided.")
            writer.add_short(data._killer_id)
            if data._killer_direction is None:
                raise SerializationError("killer_direction must be provided.")
            writer.add_char(int(data._killer_direction))
            if data._npc_index is None:
                raise SerializationError("npc_index must be provided.")
            writer.add_short(data._npc_index)
            if data._drop_index is None:
                raise SerializationError("drop_index must be provided.")
            writer.add_short(data._drop_index)
            if data._drop_id is None:
                raise SerializationError("drop_id must be provided.")
            writer.add_short(data._drop_id)
            if data._drop_coords is None:
                raise SerializationError("drop_coords must be provided.")
            Coords.serialize(writer, data._drop_coords)
            if data._drop_amount is None:
                raise SerializationError("drop_amount must be provided.")
            writer.add_int(data._drop_amount)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "NpcKilledData":
        """
        Deserializes an instance of `NpcKilledData` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            NpcKilledData: The data to serialize.
        """
        data: NpcKilledData = NpcKilledData()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._killer_id = reader.get_short()
            data._killer_direction = Direction(reader.get_char())
            data._npc_index = reader.get_short()
            data._drop_index = reader.get_short()
            data._drop_id = reader.get_short()
            data._drop_coords = Coords.deserialize(reader)
            data._drop_amount = reader.get_int()
            data._damage = reader.get_three()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"NpcKilledData(byte_size={repr(self._byte_size)}, killer_id={repr(self._killer_id)}, killer_direction={repr(self._killer_direction)}, npc_index={repr(self._npc_index)}, drop_index={repr(self._drop_index)}, drop_id={repr(self._drop_id)}, drop_coords={repr(self._drop_coords)}, drop_amount={repr(self._drop_amount)}, damage={repr(self._damage)})"
