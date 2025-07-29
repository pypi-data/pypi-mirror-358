from aisberg import AisbergClient, AisbergAsyncClient
import asyncio


client = AisbergClient()


# r = client.workflows.run("3de964bb-c98c-4c3a-9b27-8a2c6c8edc57", {})
# print(r)


async def main():
    async_client = AisbergAsyncClient()
    # r = await async_client.workflows.run(
    #     "943925fc-6561-4a01-8450-ada3ad7793f0",
    #     {
    #         "input": "Code la suite de Fibonacci en Python",
    #     },
    # )
    # print(r.response)
    models = await async_client.models.list()
    print(models)

    res = await async_client.chat.complete(
        "salut ",
        model="Qwen/Qwen3-30B-A3B",
        temperature=0.1,
    )
    print(res.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())
