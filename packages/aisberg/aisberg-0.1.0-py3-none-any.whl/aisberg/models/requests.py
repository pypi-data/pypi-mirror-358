from typing import List, Any

from pydantic import BaseModel, RootModel, ConfigDict


class AnyDict(BaseModel):
    model_config = ConfigDict(extra="allow")


class AnyList(RootModel[List[Any]]):
    pass
