from typing import Protocol

class IViStockParser(Protocol):
    def _parse_url_path(
        self,
        code: str,
        start_date: str,
        end_date: str,
        limit: int = 1
    ) -> str:
        ...