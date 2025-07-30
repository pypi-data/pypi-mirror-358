import datetime
from typing import Iterator

class BatchInterface:

    def get(self, date: datetime) -> Iterator[list[any]]:
        pass

class BatchesInterface:
    def get_batches(self) -> list[(str, BatchInterface)]:
        pass