class IVistockScraper:
    def fetch(self, url: str):
        ...

class AsyncIVistockScraper:
    async def fetch(self, url: str):
        ...