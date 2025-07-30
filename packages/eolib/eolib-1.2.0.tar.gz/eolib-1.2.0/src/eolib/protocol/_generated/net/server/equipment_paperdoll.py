# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class EquipmentPaperdoll:
    """
    Player equipment data.
    Sent with information about a player's paperdoll.
    Note that these values are item IDs.
    """
    _byte_size: int = 0
    _boots: int = None # type: ignore [assignment]
    _accessory: int = None # type: ignore [assignment]
    _gloves: int = None # type: ignore [assignment]
    _belt: int = None # type: ignore [assignment]
    _armor: int = None # type: ignore [assignment]
    _necklace: int = None # type: ignore [assignment]
    _hat: int = None # type: ignore [assignment]
    _shield: int = None # type: ignore [assignment]
    _weapon: int = None # type: ignore [assignment]
    _ring: list[int] = None # type: ignore [assignment]
    _armlet: list[int] = None # type: ignore [assignment]
    _bracer: list[int] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def boots(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._boots

    @boots.setter
    def boots(self, boots: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._boots = boots

    @property
    def accessory(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._accessory

    @accessory.setter
    def accessory(self, accessory: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._accessory = accessory

    @property
    def gloves(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._gloves

    @gloves.setter
    def gloves(self, gloves: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._gloves = gloves

    @property
    def belt(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._belt

    @belt.setter
    def belt(self, belt: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._belt = belt

    @property
    def armor(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._armor

    @armor.setter
    def armor(self, armor: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._armor = armor

    @property
    def necklace(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._necklace

    @necklace.setter
    def necklace(self, necklace: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._necklace = necklace

    @property
    def hat(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._hat

    @hat.setter
    def hat(self, hat: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._hat = hat

    @property
    def shield(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._shield

    @shield.setter
    def shield(self, shield: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._shield = shield

    @property
    def weapon(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._weapon

    @weapon.setter
    def weapon(self, weapon: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._weapon = weapon

    @property
    def ring(self) -> list[int]:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        return self._ring

    @ring.setter
    def ring(self, ring: list[int]) -> None:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        self._ring = ring

    @property
    def armlet(self) -> list[int]:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        return self._armlet

    @armlet.setter
    def armlet(self, armlet: list[int]) -> None:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        self._armlet = armlet

    @property
    def bracer(self) -> list[int]:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        return self._bracer

    @bracer.setter
    def bracer(self, bracer: list[int]) -> None:
        """
        Note:
          - Length must be `2`.
          - Element value range is 0-64008.
        """
        self._bracer = bracer

    @staticmethod
    def serialize(writer: EoWriter, data: "EquipmentPaperdoll") -> None:
        """
        Serializes an instance of `EquipmentPaperdoll` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EquipmentPaperdoll): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._boots is None:
                raise SerializationError("boots must be provided.")
            writer.add_short(data._boots)
            if data._accessory is None:
                raise SerializationError("accessory must be provided.")
            writer.add_short(data._accessory)
            if data._gloves is None:
                raise SerializationError("gloves must be provided.")
            writer.add_short(data._gloves)
            if data._belt is None:
                raise SerializationError("belt must be provided.")
            writer.add_short(data._belt)
            if data._armor is None:
                raise SerializationError("armor must be provided.")
            writer.add_short(data._armor)
            if data._necklace is None:
                raise SerializationError("necklace must be provided.")
            writer.add_short(data._necklace)
            if data._hat is None:
                raise SerializationError("hat must be provided.")
            writer.add_short(data._hat)
            if data._shield is None:
                raise SerializationError("shield must be provided.")
            writer.add_short(data._shield)
            if data._weapon is None:
                raise SerializationError("weapon must be provided.")
            writer.add_short(data._weapon)
            if data._ring is None:
                raise SerializationError("ring must be provided.")
            if len(data._ring) != 2:
                raise SerializationError(f"Expected length of ring to be exactly 2, got {len(data._ring)}.")
            for i in range(2):
                writer.add_short(data._ring[i])
            if data._armlet is None:
                raise SerializationError("armlet must be provided.")
            if len(data._armlet) != 2:
                raise SerializationError(f"Expected length of armlet to be exactly 2, got {len(data._armlet)}.")
            for i in range(2):
                writer.add_short(data._armlet[i])
            if data._bracer is None:
                raise SerializationError("bracer must be provided.")
            if len(data._bracer) != 2:
                raise SerializationError(f"Expected length of bracer to be exactly 2, got {len(data._bracer)}.")
            for i in range(2):
                writer.add_short(data._bracer[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "EquipmentPaperdoll":
        """
        Deserializes an instance of `EquipmentPaperdoll` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EquipmentPaperdoll: The data to serialize.
        """
        data: EquipmentPaperdoll = EquipmentPaperdoll()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._boots = reader.get_short()
            data._accessory = reader.get_short()
            data._gloves = reader.get_short()
            data._belt = reader.get_short()
            data._armor = reader.get_short()
            data._necklace = reader.get_short()
            data._hat = reader.get_short()
            data._shield = reader.get_short()
            data._weapon = reader.get_short()
            data._ring = []
            for i in range(2):
                data._ring.append(reader.get_short())
            data._armlet = []
            for i in range(2):
                data._armlet.append(reader.get_short())
            data._bracer = []
            for i in range(2):
                data._bracer.append(reader.get_short())
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"EquipmentPaperdoll(byte_size={repr(self._byte_size)}, boots={repr(self._boots)}, accessory={repr(self._accessory)}, gloves={repr(self._gloves)}, belt={repr(self._belt)}, armor={repr(self._armor)}, necklace={repr(self._necklace)}, hat={repr(self._hat)}, shield={repr(self._shield)}, weapon={repr(self._weapon)}, ring={repr(self._ring)}, armlet={repr(self._armlet)}, bracer={repr(self._bracer)})"
