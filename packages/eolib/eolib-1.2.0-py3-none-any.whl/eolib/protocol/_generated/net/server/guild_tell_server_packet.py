# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .guild_member import GuildMember
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class GuildTellServerPacket(Packet):
    """
    Get guild member list reply
    """
    _byte_size: int = 0
    _members_count: int = None # type: ignore [assignment]
    _members: list[GuildMember] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def members(self) -> list[GuildMember]:
        """
        Note:
          - Length must be 64008 or less.
        """
        return self._members

    @members.setter
    def members(self, members: list[GuildMember]) -> None:
        """
        Note:
          - Length must be 64008 or less.
        """
        self._members = members
        self._members_count = len(self._members)

    @staticmethod
    def family() -> PacketFamily:
        """
        Returns the packet family associated with this packet.

        Returns:
            PacketFamily: The packet family associated with this packet.
        """
        return PacketFamily.Guild

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
        GuildTellServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildTellServerPacket") -> None:
        """
        Serializes an instance of `GuildTellServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildTellServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._members_count is None:
                raise SerializationError("members_count must be provided.")
            writer.add_short(data._members_count)
            writer.add_byte(0xFF)
            if data._members is None:
                raise SerializationError("members must be provided.")
            if len(data._members) > 64008:
                raise SerializationError(f"Expected length of members to be 64008 or less, got {len(data._members)}.")
            for i in range(data._members_count):
                GuildMember.serialize(writer, data._members[i])
                writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildTellServerPacket":
        """
        Deserializes an instance of `GuildTellServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildTellServerPacket: The data to serialize.
        """
        data: GuildTellServerPacket = GuildTellServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._members_count = reader.get_short()
            reader.next_chunk()
            data._members = []
            for i in range(data._members_count):
                data._members.append(GuildMember.deserialize(reader))
                reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildTellServerPacket(byte_size={repr(self._byte_size)}, members={repr(self._members)})"
