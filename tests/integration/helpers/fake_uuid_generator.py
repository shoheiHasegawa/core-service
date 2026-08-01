from domain.system.uuid_generator import UUIDGenerator


class FakeUUIDGenerator(UUIDGenerator):
    def __init__(self, sequence: list[str] = None):
        self._sequence = sequence or []
        self._index = 0

    def generate(self) -> str:
        if self._index < len(self._sequence):
            val = self._sequence[self._index]
            self._index += 1
            return val
        return f"fake-uuid-{self._index}"
