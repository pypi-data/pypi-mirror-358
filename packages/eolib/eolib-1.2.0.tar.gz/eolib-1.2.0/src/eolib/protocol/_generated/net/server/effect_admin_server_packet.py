# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectAdminServerPacket(Packet):
    """
    Nearby character taking spike damage
    """
    _byte_size: int = 0
    _player_id: int = None # type: ignore [assignment]
    _hp_percentage: int = None # type: ignore [assignment]
    _died: bool = None # type: ignore [assignment]
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
    def player_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._player_id

    @player_id.setter
    def player_id(self, player_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._player_id = player_id

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
    def died(self) -> bool:
        return self._died

    @died.setter
    def died(self, died: bool) -> None:
        self._died = died

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
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Effect

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
        EffectAdminServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectAdminServerPacket") -> None:
        """
        Serializes an instance of `EffectAdminServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectAdminServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._player_id is None:
                raise SerializationError("player_id must be provided.")
            writer.add_short(data._player_id)
            if data._hp_percentage is None:
                raise SerializationError("hp_percentage must be provided.")
            writer.add_char(data._hp_percentage)
            if data._died is None:
                raise SerializationError("died must be provided.")
            writer.add_char(1 if data._died else 0)
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_three(data._damage)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectAdminServerPacket":
        """
        Deserializes an instance of `EffectAdminServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectAdminServerPacket: The data to serialize.
        """
        data: EffectAdminServerPacket = EffectAdminServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._player_id = reader.get_short()
            data._hp_percentage = reader.get_char()
            data._died = reader.get_char() != 0
            data._damage = reader.get_three()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectAdminServerPacket(byte_size={repr(self._byte_size)}, player_id={repr(self._player_id)}, hp_percentage={repr(self._hp_percentage)}, died={repr(self._died)}, damage={repr(self._damage)})"
