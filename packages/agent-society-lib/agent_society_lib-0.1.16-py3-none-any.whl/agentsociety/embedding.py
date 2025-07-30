import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb import ClientAPI, Collection, PersistentClient
from agentsociety.utils import load_api_key

class CollectionSupplier:

    def create_collection(self, name: str) -> Collection:
        pass

    def has_collection(self, name: str) -> bool:
        pass

    def get_collection(self, name: str) -> Collection:
        pass


class OpenAiCollectionSupplier(CollectionSupplier):

    def __init__(self) -> None:
        self.embedding_function = OpenAIEmbeddingFunction(api_key=load_api_key('openai_key'), model_name="text-embedding-3-small")
        self.client: ClientAPI = PersistentClient("chroma/")

    def create_collection(self, name: str) -> Collection:
        return self.client.create_collection(name=name, embedding_function=self.embedding_function)
    
    def has_collection(self, name: str) -> bool:
        collections = self.client.list_collections()

        collection_names = [c.name for c in collections]
        return name in collection_names
    
    def get_collection(self, name: str) -> Collection:
        return self.client.get_collection(name=name, embedding_function=self.embedding_function)


COLLECTION_SUPPLIER = None

def get_collection_supplier() -> CollectionSupplier:
    global COLLECTION_SUPPLIER

    if COLLECTION_SUPPLIER is None:
        collection_supplier_str = os.getenv("COLLECTION_SUPPLIER", "OPENAI")

        match collection_supplier_str:
            case "OPENAI":
                COLLECTION_SUPPLIER = OpenAiCollectionSupplier()
            case _:
                raise RuntimeError(f"Unknown collection supplier {collection_supplier_str}")
    return COLLECTION_SUPPLIER
