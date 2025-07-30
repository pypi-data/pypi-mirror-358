"""
Intent Routing Module.

This module provides classes and methods for categorizing textual content into predefined intents using embedding-based similarity.

Note:
    - Methods starting with an underscore (`_`) are private helper methods and should not be called directly.
"""

from typing import Dict, List, Type, Optional
from enum import Enum
from uuid import uuid4
from dataclasses import dataclass
from hashlib import sha256
from chromadb import Collection, QueryResult
from chromadb.api.types import Metadata, Document

from agentsociety.embedding import get_collection_supplier
from agentsociety.log import logger


class CategoricalIntentContext:
    """
    Defines the context for categorical intent routing, including categories and their associated sample texts.
    """

    def __init__(self, categories: Type[Enum], category_samples: Dict[Enum, List[str]]) -> None:
        """
        Initializes a CategoricalIntentContext instance.

        Args:
            categories (Type[Enum]): An enumeration of intent categories.
            category_samples (Dict[Enum, List[str]]): A dictionary mapping each category to a list of sample texts.

        Raises:
            AssertionError: If any category does not have associated samples or if the sample list is empty.
        """
        self.category_samples = category_samples
        self.categories = categories

        for category in categories:
            assert category in category_samples, (
                f"Category {category} has no samples. Every category needs samples."
            )
            assert len(category_samples[category]) > 0, (
                f"Category {category} has no samples. Every category needs samples."
            )


@dataclass
class IntentRouterResult:
    """
    Represents the result of an intent routing query, including the matched category, content, and distance.
    """
    category: Enum
    content: str
    distance: float


@dataclass
class EnumSample:
    """
    Represents a sample associated with a specific enumeration category.
    """
    sample_id: str
    type_enum: Enum
    sample: str


class IntentRouter:
    """
    Handles intent routing by categorizing textual content into predefined intents using embedding similarity.

    Note:
        - Methods starting with an underscore (`_`) are private helper methods and should not be called directly.
    """

    def __init__(
        self,
        intent_context: CategoricalIntentContext,
        top_n: int = 3,
        max_distance: float = 1.4
    ) -> None:
        """
        Initializes an IntentRouter instance.

        Args:
            intent_context (CategoricalIntentContext): The context defining intent categories and samples.
            top_n (int, optional): The number of top similar intents to consider. Defaults to 3.
            max_distance (float, optional): The maximum distance threshold for considering a match. Defaults to 1.4.

        Initializes the ChromaDB collection for intent routing, migrating existing collections if necessary.
        """
        supplier = get_collection_supplier()
        self.collection: Collection = None
        self.intent_context = intent_context
        self.top_n = top_n
        self.max_distance = max_distance
        self.router_name: str = f"collection-{intent_context.categories.__name__}"

        if supplier.has_collection(self.router_name):
            logger.info(f"Found collection '{self.router_name}'")
            self.collection = supplier.get_collection(self.router_name)
            self._migrate_collection()
        else:
            logger.info(f"Creating collection '{self.router_name}'")
            self.collection = supplier.create_collection(self.router_name)
            self._create_collection()

    def _migrate_collection(self):
        """
        Updates the existing collection by synchronizing it with the current intent context.

        This involves removing outdated embeddings and adding new ones based on the provided intent categories and samples.

        Note:
            This is a private helper method and should not be called directly.
        """
        logger.info(f"Starting collection migration for '{self.router_name}'")
        sample_data: Dict[str, EnumSample] = {}
        for category in self.intent_context.categories:
            for sample in self.intent_context.category_samples[category]:
                sample_id = sha256(f"{category.value}: {sample}".encode('utf-16')).hexdigest()
                sample_data[sample_id] = EnumSample(sample_id, category, sample)

        existing_data = self.collection.get()
        ids_to_delete = []
        existing_ids = existing_data['ids']

        for sid in existing_ids:
            if sid not in sample_data:
                ids_to_delete.append(sid)
            if sid in sample_data:
                del sample_data[sid]

        if len(ids_to_delete) > 0:
            logger.info(f"Removing {len(ids_to_delete)} embeddings from collection")
            self.collection.delete(ids=ids_to_delete)

        new_ids = []
        new_metas = []
        new_docs = []

        if len(sample_data) > 0:
            for sample in sample_data.values():
                new_ids.append(sample.sample_id)
                new_metas.append({"type": sample.type_enum.value})
                new_docs.append(sample.sample)

            logger.info(f"Adding {len(sample_data)} embeddings to collection")
            self.collection.add(new_ids, metadatas=new_metas, documents=new_docs)
        logger.info(f"Collection migration done for '{self.router_name}'")

    def _create_collection(self):
        """
        Creates a new collection and populates it with embeddings based on the intent context.

        Note:
            This is a private helper method and should not be called directly.
        """
        for category in self.intent_context.categories:
            for sample in self.intent_context.category_samples[category]:
                metadata = {
                    "type": category.value
                }
                new_id = str(uuid4())
                self.collection.add(new_id, metadatas=[metadata], documents=[sample])

    def _convert_query_result(self, result: QueryResult) -> List[IntentRouterResult]:
        """
        Converts a ChromaDB QueryResult into a list of IntentRouterResult instances.

        Args:
            result (QueryResult): The result returned from a ChromaDB query.

        Returns:
            List[IntentRouterResult]: A list of converted intent routing results.

        Note:
            This is a private helper method and should not be called directly.
        """
        documents = result['documents']
        distances = result['distances']
        metadatas = result['metadatas']

        results = []

        for i, dist in enumerate(distances[0]):
            doc = documents[0][i]
            meta = metadatas[0][i]

            enum_instance = self.intent_context.categories(meta["type"])
            r = IntentRouterResult(enum_instance, doc, dist)
            results.append(r)

        return results

    def query(
        self,
        content: str,
        top_n: Optional[int] = None,
        max_distance: float = 1.4
    ) -> List[Enum]:
        """
        Queries the collection to find the top N intent categories most similar to the provided content.

        Args:
            content (str): The textual content to categorize.
            top_n (Optional[int], optional): The number of top similar intents to retrieve. If not provided, uses the instance's `top_n`. Defaults to None.
            max_distance (float, optional): The maximum distance threshold for considering a match. Defaults to 1.4.

        Returns:
            List[Enum]: A list of intent categories that match the content within the specified distance.
        """
        result = self.collection.query(query_texts=content, n_results=top_n or self.top_n)
        converted = self._convert_query_result(result)

        filtered = [c for c in converted if c.distance < max_distance]
        in_order = sorted(filtered, key=lambda x: x.distance)

        return [c.category for c in in_order[:top_n or self.top_n]]

    def determine_category(
        self,
        content: str,
        threshold: float = 0.55
    ) -> Optional[Enum]:
        """
        Determines the most appropriate intent category for the given content based on query results.

        Args:
            content (str): The textual content to categorize.
            threshold (float, optional): The confidence threshold required to assign a category. Defaults to 0.55.

        Returns:
            Optional[Enum]: The determined intent category if confidence exceeds the threshold; otherwise, None.
        """
        votes = {c: 0 for c in self.intent_context.categories}
        results = self.query(content, top_n=self.top_n, max_distance=self.max_distance)
        if len(results) == 0:
            return None

        total_votes = len(results)

        for r in results:
            votes[r] += 1 / total_votes

            if votes[r] > threshold:
                return r

        return None