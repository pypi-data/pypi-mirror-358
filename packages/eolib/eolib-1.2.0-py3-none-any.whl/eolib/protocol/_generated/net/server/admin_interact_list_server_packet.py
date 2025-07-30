# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ..three_item import ThreeItem
from ..packet_family import PacketFamily
from ..packet_action import PacketAction
from ..item import Item
from ....serialization_error import SerializationError
from ....net.packet import Packet
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class AdminInteractListServerPacket(Packet):
    """
    Admin character inventory popup
    """
    _byte_size: int = 0
    _name: str = None # type: ignore [assignment]
    _usage: int = None # type: ignore [assignment]
    _gold_bank: int = None # type: ignore [assignment]
    _inventory: list[Item] = None # type: ignore [assignment]
    _bank: list[ThreeItem] = None # type: ignore [assignment]

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
    def gold_bank(self) -> int:
        """
        Note:
          - Value range is 0-4097152080.
        """
        return self._gold_bank

    @gold_bank.setter
    def gold_bank(self, gold_bank: int) -> None:
        """
        Note:
          - Value range is 0-4097152080.
        """
        self._gold_bank = gold_bank

    @property
    def inventory(self) -> list[Item]:
        return self._inventory

    @inventory.setter
    def inventory(self, inventory: list[Item]) -> None:
        self._inventory = inventory

    @property
    def bank(self) -> list[ThreeItem]:
        return self._bank

    @bank.setter
    def bank(self, bank: list[ThreeItem]) -> None:
        self._bank = bank

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
        return PacketAction.List

    def write(self, writer):
        """
        Serializes and writes this packet to the provided EoWriter.

        Args:
            writer (EoWriter): the writer that this packet will be written to.
        """
        AdminInteractListServerPacket.serialize(writer, self)

    @staticmethod
    def serialize(writer: EoWriter, data: "AdminInteractListServerPacket") -> None:
        """
        Serializes an instance of `AdminInteractListServerPacket` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (AdminInteractListServerPacket): The data to serialize.
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
            if data._gold_bank is None:
                raise SerializationError("gold_bank must be provided.")
            writer.add_int(data._gold_bank)
            writer.add_byte(0xFF)
            if data._inventory is None:
                raise SerializationError("inventory must be provided.")
            for i in range(len(data._inventory)):
                Item.serialize(writer, data._inventory[i])
            writer.add_byte(0xFF)
            if data._bank is None:
                raise SerializationError("bank must be provided.")
            for i in range(len(data._bank)):
                ThreeItem.serialize(writer, data._bank[i])
            writer.string_sanitization_mode = False
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "AdminInteractListServerPacket":
        """
        Deserializes an instance of `AdminInteractListServerPacket` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            AdminInteractListServerPacket: The data to serialize.
        """
        data: AdminInteractListServerPacket = AdminInteractListServerPacket()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            reader.chunked_reading_mode = True
            data._name = reader.get_string()
            reader.next_chunk()
            data._usage = reader.get_int()
            reader.next_chunk()
            data._gold_bank = reader.get_int()
            reader.next_chunk()
            inventory_length = int(reader.remaining / 6)
            data._inventory = []
            for i in range(inventory_length):
                data._inventory.append(Item.deserialize(reader))
            reader.next_chunk()
            bank_length = int(reader.remaining / 5)
            data._bank = []
            for i in range(bank_length):
                data._bank.append(ThreeItem.deserialize(reader))
            reader.chunked_reading_mode = False
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"AdminInteractListServerPacket(byte_size={repr(self._byte_size)}, name={repr(self._name)}, usage={repr(self._usage)}, gold_bank={repr(self._gold_bank)}, inventory={repr(self._inventory)}, bank={repr(self._bank)})"
