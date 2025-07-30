import datetime
from typing import Iterator, Tuple

class BatchInterface:

    def get(self, date: datetime) -> Iterator[list[any]]:
        pass

class BatchesInterface:
    def get_batches(self) -> list[Tuple[str, type[BatchInterface]]]:
        pass