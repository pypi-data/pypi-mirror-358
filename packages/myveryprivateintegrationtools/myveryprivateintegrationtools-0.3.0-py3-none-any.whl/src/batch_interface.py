import datetime
from typing import Iterator

class BatchInterface:

    def get(self, date: datetime) -> Iterator[list[any]]:
        pass
