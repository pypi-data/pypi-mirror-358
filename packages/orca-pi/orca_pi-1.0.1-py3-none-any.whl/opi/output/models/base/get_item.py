from typing import Any

from pydantic import BaseModel


class GetItem(BaseModel):
    """This class contains the get_item function for nearly all other classes"""

    def __getitem__(self, name: str) -> Any:
        return getattr(self, name.lower())
