from typing import Protocol, Literal
from datetime import datetime

class IVistockSearch(Protocol):
    def search(
        self, 
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ):
        ...

class AsyncIVistockSearch(Protocol):
    async def search(
        self, 
        code: str,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ):
        ...