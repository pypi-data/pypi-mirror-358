# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .character_stats_info_lookup import CharacterStatsInfoLookup
from .big_coords import BigCoords
from ..weight import Weight
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AdminInteractTellServerPacket(Packet):
    """
    Admin character info lookup
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _usage: int = None # type: ignore [assignment]
    _exp: int = None # type: ignore [assignment]
    _level: int = None # type: ignore [assignment]
    _map_id: int = None # type: ignore [assignment]
    _map_coords: BigCoords = None # type: ignore [assignment]
    _stats: CharacterStatsInfoLookup = None # type: ignore [assignment]
    _weight: Weight = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def usage(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._usage

    @usage.setter
    def usage(self, usage: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._usage = usage

    @property
    def exp(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._exp

    @exp.setter
    def exp(self, exp: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._exp = exp

    @property
    def level(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._level

    @level.setter
    def level(self, level: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._level = level

    @property
    def map_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._map_id

    @map_id.setter
    def map_id(self, map_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._map_id = map_id

    @property
    def map_coords(self) -> BigCoords:
        return self._map_coords

    @map_coords.setter
    def map_coords(self, map_coords: BigCoords) -> None:
        self._map_coords = map_coords

    @property
    def stats(self) -> CharacterStatsInfoLookup:
        return self._stats

    @stats.setter
    def stats(self, stats: CharacterStatsInfoLookup) -> None:
        self._stats = stats

    @property
    def weight(self) -> Weight:
        return self._weight

    @weight.setter
    def weight(self, weight: Weight) -> None:
        self._weight = weight

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.AdminInteract

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Tell

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AdminInteractTellServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AdminInteractTellServerPacket") -> None:
        """
        Serializes an instance of `AdminInteractTellServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AdminInteractTellServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._name is None:
                raise SerializationError("name must be provided.")
            writer.add_string(data._name)
            writer.add_byte(0xFF)
            if data._usage is None:
                raise SerializationError("usage must be provided.")
            writer.add_int(data._usage)
            writer.add_byte(0xFF)
            writer.add_byte(0xFF)
            if data._exp is None:
                raise SerializationError("exp must be provided.")
            writer.add_int(data._exp)
            if data._level is None:
                raise SerializationError("level must be provided.")
            writer.add_char(data._level)
            if data._map_id is None:
                raise SerializationError("map_id must be provided.")
            writer.add_short(data._map_id)
            if data._map_coords is None:
                raise SerializationError("map_coords must be provided.")
            BigCoords.serialize(writer, data._map_coords)
            if data._stats is None:
                raise SerializationError("stats must be provided.")
            CharacterStatsInfoLookup.serialize(writer, data._stats)
            if data._weight is None:
                raise SerializationError("weight must be provided.")
            Weight.serialize(writer, data._weight)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AdminInteractTellServerPacket":
        """
        Deserializes an instance of `AdminInteractTellServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AdminInteractTellServerPacket: The data to serialize.
        """
        data: AdminInteractTellServerPacket = AdminInteractTellServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._usage = reader.get_int()
            reader.next_chunk()
            reader.next_chunk()
            data._exp = reader.get_int()
            data._level = reader.get_char()
            data._map_id = reader.get_short()
            data._map_coords = BigCoords.deserialize(reader)
            data._stats = CharacterStatsInfoLookup.deserialize(reader)
            data._weight = Weight.deserialize(reader)
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AdminInteractTellServerPacket(byte_size={repr(self._byte_size)}, name={repr(self._name)}, usage={repr(self._usage)}, exp={repr(self._exp)}, level={repr(self._level)}, map_id={repr(self._map_id)}, map_coords={repr(self._map_coords)}, stats={repr(self._stats)}, weight={repr(self._weight)})"
