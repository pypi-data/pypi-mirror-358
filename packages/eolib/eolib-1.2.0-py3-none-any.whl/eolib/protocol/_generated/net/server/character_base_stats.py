# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class CharacterBaseStats:
    """
    The 6 base character stats
    """
    _byte_size: int = 0
    _str: int = None # type: ignore [assignment]
    _intl: int = None # type: ignore [assignment]
    _wis: int = None # type: ignore [assignment]
    _agi: int = None # type: ignore [assignment]
    _con: int = None # type: ignore [assignment]
    _cha: int = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def str(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._str

    @str.setter
    def str(self, str: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._str = str

    @property
    def intl(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._intl

    @intl.setter
    def intl(self, intl: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._intl = intl

    @property
    def wis(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._wis

    @wis.setter
    def wis(self, wis: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._wis = wis

    @property
    def agi(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._agi

    @agi.setter
    def agi(self, agi: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._agi = agi

    @property
    def con(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._con

    @con.setter
    def con(self, con: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._con = con

    @property
    def cha(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._cha

    @cha.setter
    def cha(self, cha: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._cha = cha

    @staticmethod
    def serialize(writer: EoWriter, data: "CharacterBaseStats") -> None:
        """
        Serializes an instance of `CharacterBaseStats` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (CharacterBaseStats): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._str is None:
                raise SerializationError("str must be provided.")
            writer.add_short(data._str)
            if data._intl is None:
                raise SerializationError("intl must be provided.")
            writer.add_short(data._intl)
            if data._wis is None:
                raise SerializationError("wis must be provided.")
            writer.add_short(data._wis)
            if data._agi is None:
                raise SerializationError("agi must be provided.")
            writer.add_short(data._agi)
            if data._con is None:
                raise SerializationError("con must be provided.")
            writer.add_short(data._con)
            if data._cha is None:
                raise SerializationError("cha must be provided.")
            writer.add_short(data._cha)
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "CharacterBaseStats":
        """
        Deserializes an instance of `CharacterBaseStats` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            CharacterBaseStats: The data to serialize.
        """
        data: CharacterBaseStats = CharacterBaseStats()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._str = reader.get_short()
            data._intl = reader.get_short()
            data._wis = reader.get_short()
            data._agi = reader.get_short()
            data._con = reader.get_short()
            data._cha = reader.get_short()
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"CharacterBaseStats(byte_size={repr(self._byte_size)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)})"
