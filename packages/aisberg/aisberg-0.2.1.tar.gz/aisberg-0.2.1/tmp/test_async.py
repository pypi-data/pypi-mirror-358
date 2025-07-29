from aisberg import AisbergAsyncClient
from aisberg.models.chat import SystemMessage, HumanMessage, AIMessage
from aisberg.models.tools import make_tool

aisberg = AisbergAsyncClient()


def rag_example():
    # Example of using the AisbergClient to perform a RAG operation
    collections = aisberg.collections.get_by_group("free-pro")
    for collection in collections:
        print(f"Collection: {collection.name}")
    chosen_collection = str(input("Enter the collection name to use: "))
    query = str(input("Enter your query: "))

    print("\n\nRetrieving documents...\n")
    docs = aisberg.embeddings.retrieve(
        query=query,
        collections_names=[chosen_collection],
        limit=5,
    )

    print("\nReranking documents...\n")
    reranked_docs = aisberg.embeddings.rerank(
        query=query,
        documents=docs,
        model="BAAI/bge-reranker-v2-m3",
        threshold=0.75,  # Keep only 75% accurate documents
    )

    print("\nGenerating response...\n")
    response = aisberg.chat.complete(
        input=f"Answer the following question using the provided documents: {query}\n\nDocuments:\n{reranked_docs}\n\nAnswer:",
        model="Llama4-Scout-Q4",
        temperature=0.1,
    )

    print(response.choices[0].message.content)


def chat_example():
    # Example of using the AisbergClient to perform a chat operation
    print("\n\nChat with the AI assistant. Type 'exit' to quit.\n")

    history: list = [
        SystemMessage(
            content="You are a helpful assistant. You can answer questions and provide information on various topics."
        )
    ]

    while True:
        query = str(input("You : "))

        if query.lower() == "exit":
            print("Exiting chat. Goodbye!")
            break

        history.append(HumanMessage(content=query))

        response = aisberg.chat.complete(
            input=history,
            model="Llama4-Scout-Q4",
            temperature=0.1,
        )
        print(f"Assistant: {response.choices[0].message.content}")
        history.append(AIMessage(content=response.choices[0].message.content))
        print("\n")


def tool_call():
    def get_weather(location: str) -> str:
        # Simulate a tool call to get weather information
        return (
            f"Tool Response : The weather in {location} is sunny with a high of 25°C."
        )

    def get_shipment_status(shipment_id: str) -> str:
        return f"Tool Response : The shipment status for {shipment_id} is in transit and expected to arrive on time."

    tools = [
        make_tool(
            name="get_weather",
            description="Get the current weather in a given location",
            params={"location": "The location to get the weather for"},
        ),
        make_tool(
            name="get_shipment_status",
            description="Get the shipment status",
            params={"shipment_id": "The ID of the shipment to check status for"},
        ),
    ]

    aisberg.tools.register("get_weather", get_weather)
    aisberg.tools.register("get_shipment_status", get_shipment_status)

    print("Hello! I can help you with various tasks.")
    while True:
        user_input = str(input("> "))
        response = aisberg.chat.complete(
            input=[
                SystemMessage(
                    content="You are a helpful assistant. To answer questions accurately, you may call external tools when needed. Use `get_weather` to retrieve the current weather for a specific location and `get_shipment_status` to check the status of a shipment by its ID."
                ),
                HumanMessage(content=user_input),
            ],
            model="Llama4-Scout-Q4",
            temperature=0.5,
            tools=tools,
            auto_execute_tools=True,
        )
        print(f"Assistant: {response.choices[0].message.content}")


def encode(text: str):
    embeddings = aisberg.embeddings.encode(
        input=text,
        model="BAAI/bge-m3",
    )
    print(f"Encoded text: {embeddings}")


if __name__ == "__main__":
    rag_example()
    # chat_example()
    # tool_call()
    # encode("This is a test sentence for encoding.")
