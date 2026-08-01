import uuid

from domain.system.uuid_generator import UUIDGenerator


class SystemUUIDGenerator(UUIDGenerator):
    def generate(self) -> str:
        return str(uuid.uuid4())
