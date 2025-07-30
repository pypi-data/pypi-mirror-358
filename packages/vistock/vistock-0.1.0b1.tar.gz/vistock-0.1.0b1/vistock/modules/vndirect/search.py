from vistock.core.constants import (
    DEFAULT_VNDIRECT_BASE_URL, DEFAULT_VNDIRECT_DOMAIN, DEFAULT_TIMEOUT
)
from vistock.modules.vndirect.scrapers import VistockVnDirectScraper
from vistock.modules.vndirect.parsers import VistockVnDirectParser
from vistock.core.utils import VistockValidator
from typing import Literal, Any, overload
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class VistockVnDirectSearch:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, **kwargs: Any) -> None:
        if timeout <= 0:
            raise ValueError(
                'Invalid configuration: "timeout" must be a strictly positive integer value representing the maximum allowable wait time for the operation.'
            )
        self._timeout = timeout

        if 'semaphore_limit' in kwargs and (not isinstance(kwargs['semaphore_limit'], int) or kwargs['semaphore_limit'] <= 0):
            raise ValueError(
                'Invalid configuration: "semaphore_limit" must be a positive integer, indicating the maximum number of concurrent asynchronous operations permitted.'
            )

        self._semaphore_limit = kwargs.get('semaphore_limit', 5)
        self._base_url = DEFAULT_VNDIRECT_BASE_URL
        self._domain = DEFAULT_VNDIRECT_DOMAIN
        self._scraper = VistockVnDirectScraper()
        self._parser = VistockVnDirectParser()
        self._semaphore = asyncio.Semaphore(self._semaphore_limit)

    @property
    def timeout(self) -> int:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value: int) -> None:
        if value <= 0:
            raise ValueError(
                'Invalid value: "timeout" must be a positive integer greater than zero.'
            )
        self._timeout = value

    @overload
    def search(
        self,
        code: str,
        start_date: str,
        end_date: str
    ):
        ...

    @overload
    def search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year']
    ):
        ...

    @overload
    def search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool
    ):
        ...

    @overload
    def search(
        self,
        code: str,
        *,
        start_date: str,
        end_date: str,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool,
        ascending: bool
    ):
        ...

    def search(
        self,
        code: str,
        *,
        start_date: str = '2012-01-01',
        end_date: str = datetime.now().strftime('%Y-%m-%d'),
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ):
        try:
            if not VistockValidator.validate_resolution(resolution):
                raise ValueError(
                    'Invalid resolution: "resolution" must be one of the following values: "day", "week", "month", or "year". Please ensure that the resolution is specified correctly.'
                )

            initial_url = f"{self._base_url}{self._parser._parse_url_path(code=code, start_date=start_date, end_date=end_date)}"
            total_elements = self._scraper.fetch(url=initial_url).get('totalElements', 0)

            url = f"{self._base_url}{self._parser._parse_url_path(code=code, start_date=start_date, end_date=end_date, limit=total_elements)}"
            data = self._scraper.fetch(url=url).get('data', [])
            
            if not data:
                raise ValueError(
                    'No data found for the given parameters. Please check the code, start date, and end date to ensure they are correct and that data exists for the specified range.'
                )
            
            if not VistockValidator.validate_json_data(data):
                raise ValueError(
                    'Invalid data format: The fetched data does not conform to the expected JSON structure. Please ensure that the API response is valid and contains the necessary fields.'
                )
            
            data.sort(key=lambda x: x.get("date", ""), reverse=not ascending)

            if advanced:
                return data

            filtered_fields = [
                'code', 'date', 'time', 'floor', 'type',
                'adOpen', 'adHigh', 'adLow', 'adClose', 'adAverage', 'nmVolume'
            ]

            return [{field: item[field] for field in filtered_fields if field in item} for item in data]

        except Exception:
            logger.error("An unexpected error occurred during the search operation.", exc_info=True)
            raise

    @overload
    async def async_search(
        self,
        code: str,
        start_date: str,
        end_date: str
    ):
        ...

    @overload
    async def async_search(
        self,
        code: str,
        start_date: str,
        end_date: str,
        *,
        resolution: Literal['day', 'week', 'month', 'year']
    ):
        ...

    @overload
    async def async_search(
        self,
        code: str,
        start_date: str,
        end_date: str,
        *,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool
    ):
        ...

    @overload 
    async def async_search(
        self,
        code: str,
        start_date: str,
        end_date: str,
        *,
        resolution: Literal['day', 'week', 'month', 'year'],
        advanced: bool,
        ascending: bool
    ):
        ...

    async def async_search(
        self,
        code: str,
        start_date: str,
        end_date: str,
        *,
        resolution: Literal['day', 'week', 'month', 'year'] = 'day',
        advanced: bool = True,
        ascending: bool = False
    ):
        pass