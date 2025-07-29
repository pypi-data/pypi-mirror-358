from typing import List

from ..models.object import Object
from ..filters.builder import EMPTY_OBJECT_FILTER

class ObjectsResource:
    def __init__(self, client):
        self._client = client

    def list(self, filters: list = EMPTY_OBJECT_FILTER) -> List[Object]:
        data = self._client.post("/api/project-service/filtered-projects", json=filters)
        return [Object.model_validate(item) for item in data]
