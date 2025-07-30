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

class GuildAgreeServerPacket(Packet):
    """
    Joined guild info
    """
    _byte_size: int = 0
    _recruiter_id: int = None # type: ignore [assignment]
    _guild_tag: str = None # type: ignore [assignment]
    _guild_name: str = None # type: ignore [assignment]
    _rank_name: str = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def recruiter_id(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._recruiter_id

    @recruiter_id.setter
    def recruiter_id(self, recruiter_id: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._recruiter_id = recruiter_id

    @property
    def guild_tag(self) -> str:
        return self._guild_tag

    @guild_tag.setter
    def guild_tag(self, guild_tag: str) -> None:
        self._guild_tag = guild_tag

    @property
    def guild_name(self) -> str:
        return self._guild_name

    @guild_name.setter
    def guild_name(self, guild_name: str) -> None:
        self._guild_name = guild_name

    @property
    def rank_name(self) -> str:
        return self._rank_name

    @rank_name.setter
    def rank_name(self, rank_name: str) -> None:
        self._rank_name = rank_name

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
        return PacketAction.Agree

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        GuildAgreeServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "GuildAgreeServerPacket") -> None:
        """
        Serializes an instance of `GuildAgreeServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (GuildAgreeServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            writer.string_sanitization_mode = True
            if data._recruiter_id is None:
                raise SerializationError("recruiter_id must be provided.")
            writer.add_short(data._recruiter_id)
            writer.add_byte(0xFF)
            if data._guild_tag is None:
                raise SerializationError("guild_tag must be provided.")
            writer.add_string(data._guild_tag)
            writer.add_byte(0xFF)
            if data._guild_name is None:
                raise SerializationError("guild_name must be provided.")
            writer.add_string(data._guild_name)
            writer.add_byte(0xFF)
            if data._rank_name is None:
                raise SerializationError("rank_name must be provided.")
            writer.add_string(data._rank_name)
            writer.add_byte(0xFF)
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "GuildAgreeServerPacket":
        """
        Deserializes an instance of `GuildAgreeServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            GuildAgreeServerPacket: The data to serialize.
        """
        data: GuildAgreeServerPacket = GuildAgreeServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._recruiter_id = reader.get_short()
            reader.next_chunk()
            data._guild_tag = reader.get_string()
            reader.next_chunk()
            data._guild_name = reader.get_string()
            reader.next_chunk()
            data._rank_name = reader.get_string()
            reader.next_chunk()
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"GuildAgreeServerPacket(byte_size={repr(self._byte_size)}, recruiter_id={repr(self._recruiter_id)}, guild_tag={repr(self._guild_tag)}, guild_name={repr(self._guild_name)}, rank_name={repr(self._rank_name)})"
