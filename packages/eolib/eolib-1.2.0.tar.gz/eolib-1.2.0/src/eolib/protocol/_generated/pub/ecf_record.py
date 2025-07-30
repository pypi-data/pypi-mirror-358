# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from ...serialization_error import SerializationError
from ....data.eo_writer import EoWriter
from ....data.eo_reader import EoReader

class EcfRecord:
    """
    Record of Class data in an Endless Class File
    """
    _byte_size: int = 0
    _name_length: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _parent_type: int = None # type: ignore [assignment]
    _stat_group: int = None # type: ignore [assignment]
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
    def name(self) -> str:
        """
        Note:
          - Length must be 252 or less.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Note:
          - Length must be 252 or less.
        """
        self._name = name
        self._name_length = len(self._name)

    @property
    def parent_type(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._parent_type

    @parent_type.setter
    def parent_type(self, parent_type: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._parent_type = parent_type

    @property
    def stat_group(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._stat_group

    @stat_group.setter
    def stat_group(self, stat_group: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._stat_group = stat_group

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
    def serialize(writer: EoWriter, data: "EcfRecord") -> None:
        """
        Serializes an instance of `EcfRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (EcfRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._parent_type is None:
                raise SerializationError("parent_type must be provided.")
            writer.add_char(data._parent_type)
            if data._stat_group is None:
                raise SerializationError("stat_group must be provided.")
            writer.add_char(data._stat_group)
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
    def deserialize(reader: EoReader) -> "EcfRecord":
        """
        Deserializes an instance of `EcfRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            EcfRecord: The data to serialize.
        """
        data: EcfRecord = EcfRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._name_length = reader.get_char()
            data._name = reader.get_fixed_string(data._name_length, False)
            data._parent_type = reader.get_char()
            data._stat_group = reader.get_char()
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
        return f"EcfRecord(byte_size={repr(self._byte_size)}, name={repr(self._name)}, parent_type={repr(self._parent_type)}, stat_group={repr(self._stat_group)}, str={repr(self._str)}, intl={repr(self._intl)}, wis={repr(self._wis)}, agi={repr(self._agi)}, con={repr(self._con)}, cha={repr(self._cha)})"
