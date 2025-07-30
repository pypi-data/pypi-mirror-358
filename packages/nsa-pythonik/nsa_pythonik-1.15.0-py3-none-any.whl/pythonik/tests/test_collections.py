import uuid
import requests_mock

from pythonik.models.base import Status, ObjectType
from pythonik.client import PythonikClient
from pythonik.models.assets.collections import (
    Collection,
    CollectionContents,
    CustomOrderStatus,
    CollectionContentInfo,
    Content,
    AddContentResponse,
)
from pythonik.specs.collection import (
    BASE,
    GET_URL,
    GET_INFO,
    GET_CONTENTS,
    POST_CONTENT,
    CollectionSpec,
)


def test_get_info():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        collection_id = str(uuid.uuid4())

        model = CollectionContentInfo(assets_count=1000, collections_count=5)
        mock_address = CollectionSpec.gen_url(GET_INFO.format(collection_id))
        m.get(mock_address, json=model.model_dump())

        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.collections().get_info(collection_id)


def test_get_contents():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        collection_id = str(uuid.uuid4())

        model = CollectionContents(objects=[])
        mock_address = CollectionSpec.gen_url(GET_CONTENTS.format(collection_id))
        m.get(mock_address, json=model.model_dump())

        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.collections().get_contents(collection_id)


def test_create_collection():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        collection_id = str(uuid.uuid4())

        model = Collection(
            id=collection_id,
            title="Enders Game",
            status=Status.ACTIVE,
            custom_order_status=CustomOrderStatus.ENABLED,
        )
        mock_address = CollectionSpec.gen_url(BASE)
        m.post(mock_address, json=model.model_dump())

        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.collections().create(body=model)


def test_get_collection():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        collection_id = str(uuid.uuid4())

        model = Collection(
            id=str(uuid.uuid4()),
            title="Enders Game",
            status=Status.ACTIVE,
            custom_order_status=CustomOrderStatus.ENABLED,
        )
        mock_address = CollectionSpec.gen_url(GET_URL.format(collection_id))
        m.get(mock_address, json=model.model_dump())

        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.collections().get(collection_id)


def test_delete_collection():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        collection_id = str(uuid.uuid4())

        mock_address = CollectionSpec.gen_url(GET_URL.format(collection_id))
        m.delete(mock_address)

        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        client.collections().delete(collection_id)


def test_add_content():
    with requests_mock.Mocker() as m:
        app_id = str(uuid.uuid4())
        auth_token = str(uuid.uuid4())
        collection_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())

        # Create test content object
        content = Content(
            object_id=asset_id,
            object_type=ObjectType.ASSETS.value,
        )

        # Create expected response model
        model = AddContentResponse()

        # Mock the POST request
        mock_address = CollectionSpec.gen_url(POST_CONTENT.format(collection_id))
        m.post(mock_address, json=model.model_dump(), status_code=201)

        # Make the request
        client = PythonikClient(app_id=app_id, auth_token=auth_token, timeout=3)
        response = client.collections().add_content(collection_id, body=content)

        # Verify response
        assert response.data == model
