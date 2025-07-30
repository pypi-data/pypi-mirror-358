# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .map_drain_damage_other import MapDrainDamageOther
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EffectTargetOtherServerPacket(Packet):
    """
    Map drain damage
    """
    _byte_size: int = 0
    _damage: int = None # type: ignore [assignment]
    _hp: int = None # type: ignore [assignment]
    _max_hp: int = None # type: ignore [assignment]
    _others: list[MapDrainDamageOther] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def damage(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._damage

    @damage.setter
    def damage(self, damage: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._damage = damage

    @property
    def hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hp

    @hp.setter
    def hp(self, hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hp = hp

    @property
    def max_hp(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._max_hp

    @max_hp.setter
    def max_hp(self, max_hp: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._max_hp = max_hp

    @property
    def others(self) -> list[MapDrainDamageOther]:
        return self._others

    @others.setter
    def others(self, others: list[MapDrainDamageOther]) -> None:
        self._others = others

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
        return PacketAction.TargetOther

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        EffectTargetOtherServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "EffectTargetOtherServerPacket") -> None:
        """
        Serializes an instance of `EffectTargetOtherServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EffectTargetOtherServerPacket): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._damage is None:
                raise SerializationError("damage must be provided.")
            writer.add_short(data._damage)
            if data._hp is None:
                raise SerializationError("hp must be provided.")
            writer.add_short(data._hp)
            if data._max_hp is None:
                raise SerializationError("max_hp must be provided.")
            writer.add_short(data._max_hp)
            if data._others is None:
                raise SerializationError("others must be provided.")
            for i in range(len(data._others)):
                MapDrainDamageOther.serialize(writer, data._others[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EffectTargetOtherServerPacket":
        """
        Deserializes an instance of `EffectTargetOtherServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EffectTargetOtherServerPacket: The data to serialize.
        """
        data: EffectTargetOtherServerPacket = EffectTargetOtherServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._damage = reader.get_short()
            data._hp = reader.get_short()
            data._max_hp = reader.get_short()
            others_length = int(reader.remaining / 5)
            data._others = []
            for i in range(others_length):
                data._others.append(MapDrainDamageOther.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EffectTargetOtherServerPacket(byte_size={repr(self._byte_size)}, damage={repr(self._damage)}, hp={repr(self._hp)}, max_hp={repr(self._max_hp)}, others={repr(self._others)})"
