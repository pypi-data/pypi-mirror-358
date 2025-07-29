from typing import List
from abc import ABC

from ..models.document import GroupDocument, Collection, CollectionDetails

from abc import abstractmethod
from ..abstract.modules import SyncModule, AsyncModule
from ..api import endpoints, async_endpoints


class AbstractDocumentModule(ABC):
    def __init__(self, parent, client):
        self._parent = parent
        self._client = client

    @abstractmethod
    def list(self) -> List[GroupDocument]:
        """
        Get a list of available collections. Document are grouped by your belonging groups.

        Returns:
            List[GroupDocument]: A list of available collections.

        Raises:
            ValueError: If no collections are found.
            Exception: If there is an error fetching the collections.
        """
        pass

    @abstractmethod
    def get_by_group(self, group_id: str) -> List[Collection]:
        """
        Get collections by group ID.

        Args:
            group_id (str): The ID of the group for which to retrieve collections.

        Returns:
            List[Collection]: A list of collections for the specified group.

        Raises:
            ValueError: If no collections are found for the specified group ID.
            Exception: If there is an error fetching the collections.
        """
        pass

    @abstractmethod
    def details(self, collection_id: str, group_id: str) -> CollectionDetails:
        """
        Get details of a specific collection.

        Args:
            collection_id (str): The ID of the collection to retrieve.
            group_id (str): The ID of the group to which the collection belongs.

        Returns:
            CollectionDetails: The details of the specified collection.

        Raises:
            ValueError: If the specified collection is not found.
        """
        pass

    @staticmethod
    def _get_collections_by_group(
        collections: List[GroupDocument], group_id: str
    ) -> List[Collection]:
        for group in collections:
            if group.group == group_id:
                return group.collections
        raise ValueError("No collections found for group ID")


class SyncDocumentModule(SyncModule, AbstractDocumentModule):
    def __init__(self, parent, client):
        SyncModule.__init__(self, parent, client)
        AbstractDocumentModule.__init__(self, parent, client)

    def list(self) -> List[GroupDocument]:
        return endpoints.collections(self._client)

    def get_by_group(self, group_id: str) -> List[Collection]:
        collections = self.list()
        return self._get_collections_by_group(collections, group_id)

    def details(self, collection_id: str, group_id: str) -> CollectionDetails:
        points = endpoints.collection(self._client, collection_id, group_id)
        if points is None:
            raise ValueError("No collection found")
        return CollectionDetails(
            name=collection_id,
            group=group_id,
            points=points,
        )


class AsyncDocumentModule(AsyncModule, AbstractDocumentModule):
    def __init__(self, parent, client):
        AsyncModule.__init__(self, parent, client)
        AbstractDocumentModule.__init__(self, parent, client)

    async def list(self) -> List[GroupDocument]:
        return await async_endpoints.collections(self._client)

    async def get_by_group(self, group_id: str) -> List[Collection]:
        collections = await self.list()
        return self._get_collections_by_group(collections, group_id)

    async def details(self, collection_id: str, group_id: str) -> CollectionDetails:
        points = await async_endpoints.collection(self._client, collection_id, group_id)
        if points is None:
            raise ValueError("No collection found")
        return CollectionDetails(
            name=collection_id,
            group=group_id,
            points=points,
        )
