from aisberg import AisbergClient, AisbergAsyncClient
import json


def test_doc():
    client = AisbergClient()
    print(client.models.list())
    stt = str(input("STT model to use (default: tts-1.5): ") or "tts-1.5")
    docs = client.documents.parse(
        ["./tmp/test.mp3", "./tmp/test.png"],
        stt_model=stt,
        vlm_model="pixtral-12b-2409",
        input="Que vois tu en haut à droite de l'image ?"
    )

    print(f"### MP3 Content: {docs[0].content.data}\n")
    # print(f"### PDF Content: {docs[1].content.data}\n")
    # print(f"### JSON Content: {json.dumps(docs[2].content.data, indent=2)}\n")


async def async_test_doc():
    client = AisbergAsyncClient()
    docs = await client.documents.parse(["./tmp/test.mp3", "./tmp/test.pdf", "./tmp/test.json"])

    img = await client.documents.parse("./tmp/test.png", input="Que vois tu en haut à droite de l'image ?")

    print(f"### MP3 Content: {docs[0].content.data}\n")
    print(f"### PDF Content: {docs[1].content.data}\n")
    print(f"### JSON Content: {json.dumps(docs[2].content.data, indent=2)}\n")


if __name__ == "__main__":
    test_doc()

    # import asyncio
    # asyncio.run(async_test_doc())
