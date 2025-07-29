from aisberg import AisbergClient
from aisberg.api.endpoints import parse_document

client = AisbergClient()

def test_doc():
    file_bytes = b"Hello, this is a test document."
    doc = parse_document(client._client, (file_bytes, "test.txt"), source="test_source")
    print(doc)

if __name__ == "__main__":
    test_doc()