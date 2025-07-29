from aisberg import AisbergClient, AisbergAsyncClient
import json


def test_coll():
    client = AisbergClient()
    # client.collections.delete('test_aisberg_sdk')
    #
    # colls = client.collections.create('test_aisberg_sdk', {
    #     "chunks": [
    #         "This is a test chunk 1",
    #         "This is a test chunk 2",
    #         "This is a test chunk 3"
    #     ],
    #     "metadata": [
    #         {"source": "test1.txt", "author": "Author 1"},
    #         {"source": "test2.txt", "author": "Author 2"},
    #         {"source": "test3.txt", "author": "Author 3"}
    #     ]
    # })


    points = client.collections.insert_points('test_aisberg_sdk', {
        "chunks": [
            "LKFJELZFKJZLEsdfsdfKFJZLKEJF chunk 1",
            "LKFJELZFKJZsdfsdfLEKFJZLKEJF chunk 2",
            "LKFJELZFsdfsdfsdfKJZLEKFJZLsdfsdfKEJF chunk 3"
        ],
        "metadata": [
            {"source": "test1.txt", "author": "Author 1"},
            {"source": "test2.txt", "author": "Author 2"},
            {"source": "test3.txt", "author": "Author 3"}
        ]
    }).points

    print(f"### Collection Created: {points}\n")

    points_to_delete = []
    for i in range(2):
        points_to_delete.append(points[i].id)
    print(f"### Points to delete: {points_to_delete}\n")
    a = client.collections.delete_points('test_aisberg_sdk', points_to_delete)
    print(f"### Points Deleted: {a}\n")

    c = client.collections.clear('test_aisberg_sdk')
    print(f"### Collection Cleared: {c}\n")




async def async_test_coll():
    client = AisbergAsyncClient()
    await client.collections.delete('test_aisberg_sdk')

    colls = await client.collections.create('test_aisberg_sdk', './tmp/test.json')

    print(f"### Collection Created: {colls}\n")


if __name__ == "__main__":
    test_coll()
    #
    # import asyncio
    #
    # asyncio.run(async_test_coll())
