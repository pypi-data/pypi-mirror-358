import pytest
import pytest_asyncio

from aisberg.modules import AsyncCollectionsModule, SyncCollectionsModule


## Fixtures for asynchronous tests
@pytest_asyncio.fixture
async def async_parent():
    from aisberg import AisbergAsyncClient

    return await AisbergAsyncClient().initialize()


@pytest_asyncio.fixture
async def async_collections_module(async_parent):
    return AsyncCollectionsModule(parent=async_parent, client=async_parent._client)


## Fixtures for synchronous tests
@pytest.fixture()
def sync_parent():
    from aisberg import AisbergClient

    return AisbergClient()


@pytest.fixture
def sync_collections_module(sync_parent):
    return SyncCollectionsModule(parent=sync_parent, client=sync_parent._client)


## ---------------------------------------------------------
## Tests for asynchronous collections module
## ---------------------------------------------------------
@pytest.mark.asyncio
async def test_async_list_returns_groups(async_collections_module):
    result = await async_collections_module.list()
    assert isinstance(result, list)
    assert len(result) > 0, "Aucune collection trouvée sur l'API réelle."
    assert hasattr(result[0], "group")
    assert hasattr(result[0], "collections")


@pytest.mark.asyncio
async def test_async_get_by_group(async_collections_module):
    groups = await async_collections_module.list()
    group_id = groups[0].group
    collections = await async_collections_module.get_by_group(group_id)
    assert isinstance(collections, list)
    assert len(collections) > 0
    assert hasattr(collections[0], "name")


@pytest.mark.asyncio
async def test_async_details(async_collections_module):
    groups = await async_collections_module.list()
    group_id = groups[0].group
    collection = groups[0].collections[0]
    details = await async_collections_module.details(
        collection_id=collection.name, group_id=group_id
    )
    assert hasattr(details, "name")
    assert hasattr(details, "group")
    assert details.name == collection.name
    assert details.group == group_id
    assert isinstance(details.points, list)


@pytest.mark.asyncio
async def test_async_get_by_group_not_found(async_collections_module):
    with pytest.raises(ValueError):
        await async_collections_module.get_by_group("THIS_GROUP_DOES_NOT_EXIST")


## ---------------------------------------------------------
## Tests for synchronous collections module
## ---------------------------------------------------------
def test_sync_list_returns_groups(sync_collections_module):
    result = sync_collections_module.list()
    assert isinstance(result, list)
    assert len(result) > 0, "Aucune collection trouvée sur l'API réelle."
    assert hasattr(result[0], "group")
    assert hasattr(result[0], "collections")


def test_sync_get_by_group(sync_collections_module):
    # On prend le premier groupe connu
    groups = sync_collections_module.list()
    group_id = groups[0].group
    collections = sync_collections_module.get_by_group(group_id)
    assert isinstance(collections, list)
    assert len(collections) > 0
    assert hasattr(collections[0], "name")


def test_sync_details(sync_collections_module):
    # On prend le premier groupe et sa première collection
    groups = sync_collections_module.list()
    group_id = groups[0].group
    collection = groups[0].collections[0]
    details = sync_collections_module.details(
        collection_id=collection.name, group_id=group_id
    )
    assert hasattr(details, "name")
    assert hasattr(details, "group")
    assert details.name == collection.name
    assert details.group == group_id
    assert isinstance(details.points, list)


def test_sync_get_by_group_not_found(sync_collections_module):
    # On teste un groupe inexistant
    with pytest.raises(ValueError):
        sync_collections_module.get_by_group("THIS_GROUP_DOES_NOT_EXIST")
