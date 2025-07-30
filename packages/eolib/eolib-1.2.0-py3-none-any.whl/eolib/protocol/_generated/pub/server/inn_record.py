# Generated from the eo-protocol XML specification.
#
# This file should not be modified.
# Changes will be lost when code is regenerated.

from __future__ import annotations
from .inn_question_record import InnQuestionRecord
from ....serialization_error import SerializationError
from .....data.eo_writer import EoWriter
from .....data.eo_reader import EoReader

class InnRecord:
    """
    Record of Inn data in an Endless Inn File
    """
    _byte_size: int = 0
    _behavior_id: int = None # type: ignore [assignment]
    _name_length: int = None # type: ignore [assignment]
    _name: str = None # type: ignore [assignment]
    _spawn_map: int = None # type: ignore [assignment]
    _spawn_x: int = None # type: ignore [assignment]
    _spawn_y: int = None # type: ignore [assignment]
    _sleep_map: int = None # type: ignore [assignment]
    _sleep_x: int = None # type: ignore [assignment]
    _sleep_y: int = None # type: ignore [assignment]
    _alternate_spawn_enabled: bool = None # type: ignore [assignment]
    _alternate_spawn_map: int = None # type: ignore [assignment]
    _alternate_spawn_x: int = None # type: ignore [assignment]
    _alternate_spawn_y: int = None # type: ignore [assignment]
    _questions: list[InnQuestionRecord] = None # type: ignore [assignment]

    @property
    def byte_size(self) -> int:
        """
        Returns the size of the data that this was deserialized from.

        Returns:
            int: The size of the data that this was deserialized from.
        """
        return self._byte_size

    @property
    def behavior_id(self) -> int:
        """
        Behavior ID of the NPC that runs the inn. 0 for default inn

        Note:
          - Value range is 0-64008.
        """
        return self._behavior_id

    @behavior_id.setter
    def behavior_id(self, behavior_id: int) -> None:
        """
        Behavior ID of the NPC that runs the inn. 0 for default inn

        Note:
          - Value range is 0-64008.
        """
        self._behavior_id = behavior_id

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
    def spawn_map(self) -> int:
        """
        ID of the map the player is sent to after respawning

        Note:
          - Value range is 0-64008.
        """
        return self._spawn_map

    @spawn_map.setter
    def spawn_map(self, spawn_map: int) -> None:
        """
        ID of the map the player is sent to after respawning

        Note:
          - Value range is 0-64008.
        """
        self._spawn_map = spawn_map

    @property
    def spawn_x(self) -> int:
        """
        X coordinate of the map the player is sent to after respawning

        Note:
          - Value range is 0-252.
        """
        return self._spawn_x

    @spawn_x.setter
    def spawn_x(self, spawn_x: int) -> None:
        """
        X coordinate of the map the player is sent to after respawning

        Note:
          - Value range is 0-252.
        """
        self._spawn_x = spawn_x

    @property
    def spawn_y(self) -> int:
        """
        Y coordinate of the map the player is sent to after respawning

        Note:
          - Value range is 0-252.
        """
        return self._spawn_y

    @spawn_y.setter
    def spawn_y(self, spawn_y: int) -> None:
        """
        Y coordinate of the map the player is sent to after respawning

        Note:
          - Value range is 0-252.
        """
        self._spawn_y = spawn_y

    @property
    def sleep_map(self) -> int:
        """
        ID of the map the player is sent to after sleeping at the inn

        Note:
          - Value range is 0-64008.
        """
        return self._sleep_map

    @sleep_map.setter
    def sleep_map(self, sleep_map: int) -> None:
        """
        ID of the map the player is sent to after sleeping at the inn

        Note:
          - Value range is 0-64008.
        """
        self._sleep_map = sleep_map

    @property
    def sleep_x(self) -> int:
        """
        X coordinate of the map the player is sent to after sleeping at the inn

        Note:
          - Value range is 0-252.
        """
        return self._sleep_x

    @sleep_x.setter
    def sleep_x(self, sleep_x: int) -> None:
        """
        X coordinate of the map the player is sent to after sleeping at the inn

        Note:
          - Value range is 0-252.
        """
        self._sleep_x = sleep_x

    @property
    def sleep_y(self) -> int:
        """
        Y coordinate of the map the player is sent to after sleeping at the inn

        Note:
          - Value range is 0-252.
        """
        return self._sleep_y

    @sleep_y.setter
    def sleep_y(self, sleep_y: int) -> None:
        """
        Y coordinate of the map the player is sent to after sleeping at the inn

        Note:
          - Value range is 0-252.
        """
        self._sleep_y = sleep_y

    @property
    def alternate_spawn_enabled(self) -> bool:
        """
        Flag for an alternate spawn point. If true, the server will use this alternate spawn
        map, x, and, y based on some other condition.

        In the official server, this is used to respawn new characters on the noob island
        until they reach a certain level.
        """
        return self._alternate_spawn_enabled

    @alternate_spawn_enabled.setter
    def alternate_spawn_enabled(self, alternate_spawn_enabled: bool) -> None:
        """
        Flag for an alternate spawn point. If true, the server will use this alternate spawn
        map, x, and, y based on some other condition.

        In the official server, this is used to respawn new characters on the noob island
        until they reach a certain level.
        """
        self._alternate_spawn_enabled = alternate_spawn_enabled

    @property
    def alternate_spawn_map(self) -> int:
        """
        Note:
          - Value range is 0-64008.
        """
        return self._alternate_spawn_map

    @alternate_spawn_map.setter
    def alternate_spawn_map(self, alternate_spawn_map: int) -> None:
        """
        Note:
          - Value range is 0-64008.
        """
        self._alternate_spawn_map = alternate_spawn_map

    @property
    def alternate_spawn_x(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._alternate_spawn_x

    @alternate_spawn_x.setter
    def alternate_spawn_x(self, alternate_spawn_x: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._alternate_spawn_x = alternate_spawn_x

    @property
    def alternate_spawn_y(self) -> int:
        """
        Note:
          - Value range is 0-252.
        """
        return self._alternate_spawn_y

    @alternate_spawn_y.setter
    def alternate_spawn_y(self, alternate_spawn_y: int) -> None:
        """
        Note:
          - Value range is 0-252.
        """
        self._alternate_spawn_y = alternate_spawn_y

    @property
    def questions(self) -> list[InnQuestionRecord]:
        """
        Note:
          - Length must be `3`.
        """
        return self._questions

    @questions.setter
    def questions(self, questions: list[InnQuestionRecord]) -> None:
        """
        Note:
          - Length must be `3`.
        """
        self._questions = questions

    @staticmethod
    def serialize(writer: EoWriter, data: "InnRecord") -> None:
        """
        Serializes an instance of `InnRecord` to the provided `EoWriter`.

        Args:
            writer (EoWriter): The writer that the data will be serialized to.
            data (InnRecord): The data to serialize.
        """
        old_string_sanitization_mode: bool = writer.string_sanitization_mode
        try:
            if data._behavior_id is None:
                raise SerializationError("behavior_id must be provided.")
            writer.add_short(data._behavior_id)
            if data._name_length is None:
                raise SerializationError("name_length must be provided.")
            writer.add_char(data._name_length)
            if data._name is None:
                raise SerializationError("name must be provided.")
            if len(data._name) > 252:
                raise SerializationError(f"Expected length of name to be 252 or less, got {len(data._name)}.")
            writer.add_fixed_string(data._name, data._name_length, False)
            if data._spawn_map is None:
                raise SerializationError("spawn_map must be provided.")
            writer.add_short(data._spawn_map)
            if data._spawn_x is None:
                raise SerializationError("spawn_x must be provided.")
            writer.add_char(data._spawn_x)
            if data._spawn_y is None:
                raise SerializationError("spawn_y must be provided.")
            writer.add_char(data._spawn_y)
            if data._sleep_map is None:
                raise SerializationError("sleep_map must be provided.")
            writer.add_short(data._sleep_map)
            if data._sleep_x is None:
                raise SerializationError("sleep_x must be provided.")
            writer.add_char(data._sleep_x)
            if data._sleep_y is None:
                raise SerializationError("sleep_y must be provided.")
            writer.add_char(data._sleep_y)
            if data._alternate_spawn_enabled is None:
                raise SerializationError("alternate_spawn_enabled must be provided.")
            writer.add_char(1 if data._alternate_spawn_enabled else 0)
            if data._alternate_spawn_map is None:
                raise SerializationError("alternate_spawn_map must be provided.")
            writer.add_short(data._alternate_spawn_map)
            if data._alternate_spawn_x is None:
                raise SerializationError("alternate_spawn_x must be provided.")
            writer.add_char(data._alternate_spawn_x)
            if data._alternate_spawn_y is None:
                raise SerializationError("alternate_spawn_y must be provided.")
            writer.add_char(data._alternate_spawn_y)
            if data._questions is None:
                raise SerializationError("questions must be provided.")
            if len(data._questions) != 3:
                raise SerializationError(f"Expected length of questions to be exactly 3, got {len(data._questions)}.")
            for i in range(3):
                InnQuestionRecord.serialize(writer, data._questions[i])
        finally:
            writer.string_sanitization_mode = old_string_sanitization_mode

    @staticmethod
    def deserialize(reader: EoReader) -> "InnRecord":
        """
        Deserializes an instance of `InnRecord` from the provided `EoReader`.

        Args:
            reader (EoReader): The writer that the data will be serialized to.

        Returns:
            InnRecord: The data to serialize.
        """
        data: InnRecord = InnRecord()
        old_chunked_reading_mode: bool = reader.chunked_reading_mode
        try:
            reader_start_position: int = reader.position
            data._behavior_id = reader.get_short()
            data._name_length = reader.get_char()
            data._name = reader.get_fixed_string(data._name_length, False)
            data._spawn_map = reader.get_short()
            data._spawn_x = reader.get_char()
            data._spawn_y = reader.get_char()
            data._sleep_map = reader.get_short()
            data._sleep_x = reader.get_char()
            data._sleep_y = reader.get_char()
            data._alternate_spawn_enabled = reader.get_char() != 0
            data._alternate_spawn_map = reader.get_short()
            data._alternate_spawn_x = reader.get_char()
            data._alternate_spawn_y = reader.get_char()
            data._questions = []
            for i in range(3):
                data._questions.append(InnQuestionRecord.deserialize(reader))
            data._byte_size = reader.position - reader_start_position
            return data
        finally:
            reader.chunked_reading_mode = old_chunked_reading_mode

    def __repr__(self):
        return f"InnRecord(byte_size={repr(self._byte_size)}, behavior_id={repr(self._behavior_id)}, name={repr(self._name)}, spawn_map={repr(self._spawn_map)}, spawn_x={repr(self._spawn_x)}, spawn_y={repr(self._spawn_y)}, sleep_map={repr(self._sleep_map)}, sleep_x={repr(self._sleep_x)}, sleep_y={repr(self._sleep_y)}, alternate_spawn_enabled={repr(self._alternate_spawn_enabled)}, alternate_spawn_map={repr(self._alternate_spawn_map)}, alternate_spawn_x={repr(self._alternate_spawn_x)}, alternate_spawn_y={repr(self._alternate_spawn_y)}, questions={repr(self._questions)})"
