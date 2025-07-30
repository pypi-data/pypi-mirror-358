from typing import Protocol

class IVistockListing(Protocol):
    def list(self):
        ...