# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from .npc_killed_data import NpcKilledData
from .level_up_stats import LevelUpStats
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CastAcceptServerPacket(Packet):
    """
    Nearby NPC killed by player spell and you leveled up
    """
    _byte_size: int = 0
    _spell_id: int = None # type: ignore [assignment]
    _npc_killed_data: NpcKilledData = None # type: ignore [assignment]
    _caster_tp: int = None # type: ignore [assignment]
    _experience: int = None # type: ignore [assignment]
    _level_up: LevelUpStats = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def spell_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._spell_id

    @spell_id.setter
    def spell_id(self, spell_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._spell_id = spell_id

    @property
    def npc_killed_data(self) -> NpcKilledData:
        return self._npc_killed_data

    @npc_killed_data.setter
    def npc_killed_data(self, npc_killed_data: NpcKilledData) -> None:
        self._npc_killed_data = npc_killed_data

    @property
    def caster_tp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._caster_tp

    @caster_tp.setter
    def caster_tp(self, caster_tp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._caster_tp = caster_tp

    @property
    def experience(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._experience

    @experience.setter
    def experience(self, experience: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._experience = experience

    @property
    def level_up(self) -> LevelUpStats:
        return self._level_up

    @level_up.setter
    def level_up(self, level_up: LevelUpStats) -> None:
        self._level_up = level_up

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Cast

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Accept

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        CastAcceptServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "CastAcceptServerPacket") -> None:
        """
        Serializes an instance of `CastAcceptServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CastAcceptServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
            if data._npc_killed_data is None:
                raise SerializationError("npc_killed_data must be provided.")
            NpcKilledData.serialize(writer, data._npc_killed_data)
            if data._caster_tp is None:
                raise SerializationError("caster_tp must be provided.")
            writer.add_short(data._caster_tp)
            if data._experience is None:
                raise SerializationError("experience must be provided.")
            writer.add_int(data._experience)
            if data._level_up is None:
                raise SerializationError("level_up must be provided.")
            LevelUpStats.serialize(writer, data._level_up)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CastAcceptServerPacket":
        """
        Deserializes an instance of `CastAcceptServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CastAcceptServerPacket: The data to serialize.
        """
        data: CastAcceptServerPacket = CastAcceptServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._spell_id = reader.get_short()
            data._npc_killed_data = NpcKilledData.deserialize(reader)
            data._caster_tp = reader.get_short()
            data._experience = reader.get_int()
            data._level_up = LevelUpStats.deserialize(reader)
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CastAcceptServerPacket(byte_size={repr(self._byte_size)}, spell_id={repr(self._spell_id)}, npc_killed_data={repr(self._npc_killed_data)}, caster_tp={repr(self._caster_tp)}, experience={repr(self._experience)}, level_up={repr(self._level_up)})"
