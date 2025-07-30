# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ...direction import Direction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AvatarAdminServerPacket(Packet):
    """
    Nearby player hit by a damage spell from a player
    """
    _byte_size: int = 0
    _caster_id: int = None # type: ignore [assignment]
    _victim_id: int = None # type: ignore [assignment]
    _damage: int = None # type: ignore [assignment]
    _caster_direction: Direction = None # type: ignore [assignment]
    _hp_percentage: int = None # type: ignore [assignment]
    _victim_died: bool = None # type: ignore [assignment]
    _spell_id: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def caster_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._caster_id

    @caster_id.setter
    def caster_id(self, caster_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._caster_id = caster_id

    @property
    def victim_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._victim_id

    @victim_id.setter
    def victim_id(self, victim_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._victim_id = victim_id

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

    @property
    def caster_direction(self) -> Direction:
        return self._caster_direction

    @caster_direction.setter
    def caster_direction(self, caster_direction: Direction) -> None:
        self._caster_direction = caster_direction

    @property
    def hp_percentage(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._hp_percentage

    @hp_percentage.setter
    def hp_percentage(self, hp_percentage: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._hp_percentage = hp_percentage

    @property
    def victim_died(self) -> bool:
        return self._victim_died

    @victim_died.setter
    def victim_died(self, victim_died: bool) -> None:
        self._victim_died = victim_died

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

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Avatar

    @staticmethod
    def action() -> PacketAction:
        """
        Returns the packet action associated with this packet.

        Returns:
            PacketAction: The packet action associated with this packet.
        """
        return PacketAction.Admin

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AvatarAdminServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AvatarAdminServerPacket") -> None:
        """
        Serializes an instance of `AvatarAdminServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AvatarAdminServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._caster_id is None:
                raise SerializationError("caster_id must be provided.")
            writer.add_short(data._caster_id)
            if data._victim_id is None:
                raise SerializationError("victim_id must be provided.")
            writer.add_short(data._victim_id)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
            if data._caster_direction is None:
                raise SerializationError("caster_direction must be provided.")
            writer.add_char(int(data._caster_direction))
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._victim_died is None:
                raise SerializationError("victim_died must be provided.")
            writer.add_char(1 if data._victim_died else 0)
            if data._spell_id is None:
                raise SerializationError("spell_id must be provided.")
            writer.add_short(data._spell_id)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AvatarAdminServerPacket":
        """
        Deserializes an instance of `AvatarAdminServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AvatarAdminServerPacket: The data to serialize.
        """
        data: AvatarAdminServerPacket = AvatarAdminServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._caster_id = reader.get_short()
            data._victim_id = reader.get_short()
            data._damage = reader.get_three()
            data._caster_direction = Direction(reader.get_char())
            data._hp_percentage = reader.get_char()
            data._victim_died = reader.get_char() != 0
            data._spell_id = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AvatarAdminServerPacket(byte_size={repr(self._byte_size)}, caster_id={repr(self._caster_id)}, victim_id={repr(self._victim_id)}, damage={repr(self._damage)}, caster_direction={repr(self._caster_direction)}, hp_percentage={repr(self._hp_percentage)}, victim_died={repr(self._victim_died)}, spell_id={repr(self._spell_id)})"
