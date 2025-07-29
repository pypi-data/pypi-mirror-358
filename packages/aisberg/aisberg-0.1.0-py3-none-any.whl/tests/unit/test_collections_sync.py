import pytest
from unittest.mock import patch, MagicMock

from aisberg.models.collections import (
    GroupCollections,
    Collection,
    CollectionDetails,
)
from aisberg.modules import SyncCollectionsModule


# Données factices pour les tests
@pytest.fixture
def mock_collections_data():
    return [
        GroupCollections(
            group="group1",
            collections=[
                Collection(name="col1"),
                Collection(name="col2"),
            ],
        ),
        GroupCollections(
            group="group2",
            collections=[
                Collection(name="col3"),
            ],
        ),
    ]


@pytest.fixture
def mock_points_data():
    return [
        {
            "id": "pt1",
            "payload": {
                "method": "m1",
                "norm": "normA",
                "filetype": "txt",
                "filename": "test.txt",
                "dense_encoder": "encoderA",
                "Category": "cat1",
                "text": "Ceci est un texte",
                "timestamp": "2024-06-21T10:00:00",
                "collection_name": "col1",
                "sparse_encoder": "spA",
            },
        }
    ]


@pytest.fixture
def module():
    # Un parent factice, client factice
    parent = MagicMock()
    client = MagicMock()
    return SyncCollectionsModule(parent, client)


def test_list_collections(module, mock_collections_data):
    with patch("aisberg.api.endpoints.collections", return_value=mock_collections_data):
        result = module.list()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].group == "group1"
        assert result[1].collections[0].name == "col3"


def test_list_collections_empty(module):
    with patch("aisberg.api.endpoints.collections", return_value=[]):
        result = module.list()
        assert result == []


def test_get_by_group_success(module, mock_collections_data):
    with patch("aisberg.api.endpoints.collections", return_value=mock_collections_data):
        collections = module.get_by_group("group1")
        assert isinstance(collections, list)
        assert len(collections) == 2
        assert collections[0].name == "col1"


def test_get_by_group_not_found(module, mock_collections_data):
    with patch("aisberg.api.endpoints.collections", return_value=mock_collections_data):
        with pytest.raises(ValueError, match="No collections found for group ID"):
            module.get_by_group("groupX")


def test_details_success(module, mock_points_data):
    with patch("aisberg.api.endpoints.collection", return_value=mock_points_data):
        details = module.details("col1", "group1")
        assert isinstance(details, CollectionDetails)
        assert details.name == "col1"
        assert details.group == "group1"
        assert len(details.points) == 1
        assert details.points[0].id == "pt1"
        assert details.points[0].payload.text == "Ceci est un texte"


def test_details_not_found(module):
    with patch("aisberg.api.endpoints.collection", return_value=None):
        with pytest.raises(ValueError, match="No collection found"):
            module.details("col2", "group1")
