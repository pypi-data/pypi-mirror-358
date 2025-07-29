import asyncio
import uuid
from typing import Dict, Hashable, List, Optional, Sequence, Set, Type, cast

from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client import AsyncQdrantClient, models
from rapidfuzz import distance, fuzz

from ragchat.definitions import (
    EmbeddingName,
    Id,
    IndexedFilters,
    NodeType,
    Operator,
    Point,
    QueryPoint,
    Relation,
    SemanticType,
    decode_kv,
    encode_kv,
)
from ragchat.log import DEBUG, INFO, abbrev, get_logger
from ragchat.utils import (
    is_iso_datetime_string,
    rescale_similarity,
    retry,
    timeit,
)

logger = get_logger(__name__)


class QdrantSettings(BaseSettings):
    url: Optional[str] = None
    local_hosts: Optional[List[str]] = ["localhost", "host.docker.internal"]
    port: int = 6333
    grpc_port: int = 6334
    p2p_port: int = 6335
    api_key: Optional[str] = None
    idx_on_disk: bool = True
    vec_on_disk: bool = True
    quantile: float = 0.99

    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="QDRANT_")

    async def initialize(self) -> None:
        """
        Attempts to connect to Qdrant using the provided URL or default local hosts.
        Sets the `url` attribute to the first successful connection URL.
        Raises ConnectionError if no connection can be established.
        """
        urls_to_check = set()
        if self.url:
            urls_to_check.add(self.url)

        for host in self.local_hosts or []:
            urls_to_check.add(f"http://{host}:{self.port}")

        connection_attempts = [self._attempt_connection(url) for url in urls_to_check]
        results = await asyncio.gather(*connection_attempts, return_exceptions=True)
        successful_results = [result for result in results if isinstance(result, str)]
        self.url = next((result for result in successful_results if result), None)
        if not self.url:
            raise ConnectionError(
                f"Could not connect to Qdrant using any of the default hosts or the provided URL: {self.url}"
            )

        logger.info(f"Connection established using {self.url.split('@')[-1]}")

    async def _attempt_connection(self, url: str) -> str | None:
        """
        Attempts to connect to Qdrant at the given URL and returns the URL if successful.
        """
        client = None
        try:
            client = AsyncQdrantClient(url=url)
            await client.info()
            return url
        except Exception as e:
            logger.debug(f"Failed to connect to {url}: {e}")
            return None
        finally:
            if client:
                await client.close()


class Qdrant:
    def __init__(self, settings: Optional[QdrantSettings] = None):
        """
        Initializes the Qdrant client with specified settings.
        """
        self.settings = settings or QdrantSettings()
        self.retry_on: List[Type[Exception]] = []

    async def initialize(self, embedding_model: str, embedding_dims: int) -> None:
        """
        Initializes the Qdrant database, creating or updating a collection
        based on the embedding model and dimensions.
        """
        await self.settings.initialize()
        assert self.settings.url, "Missing settings.url"
        self.embedding_dims = embedding_dims
        self.embedding_model = embedding_model
        self.client = AsyncQdrantClient(self.settings.url)
        self.collection = encode_kv(self.embedding_model, str(self.embedding_dims))

        sparse_index = models.SparseIndexParams(
            on_disk=self.settings.idx_on_disk,
            datatype=models.Datatype.UINT8,
        )

        sparse_configs = {
            "classifiers": models.SparseVectorParams(
                index=sparse_index,
                modifier=models.Modifier.NONE,
            ),
            f"{NodeType.CHUNK}_{EmbeddingName.CONTENT}": models.SparseVectorParams(
                index=sparse_index,
                modifier=models.Modifier.IDF,
            ),
            f"{NodeType.CHUNK}_{EmbeddingName.SUMMARY}": models.SparseVectorParams(
                index=sparse_index,
                modifier=models.Modifier.NONE,
            ),
            f"{NodeType.FACT}_{EmbeddingName.CONTENT}": models.SparseVectorParams(
                index=sparse_index,
                modifier=models.Modifier.IDF,
            ),
            f"{NodeType.FACT}_{EmbeddingName.SUMMARY}": models.SparseVectorParams(
                index=sparse_index,
                modifier=models.Modifier.NONE,
            ),
        }

        exists = await self.client.collection_exists(collection_name=self.collection)
        if exists:
            collection_info = await self.client.get_collection(
                collection_name=self.collection
            )
            if collection_info.status == models.CollectionStatus.RED:
                raise ValueError(
                    f"Collection '{self.collection}' is in RED status. Please check and resolve the issue"
                )

            logger.info(
                f"Updating sparse vector config in existing collection: '{self.collection}'."
            )
            await self.client.update_collection(
                collection_name=self.collection,
                sparse_vectors_config=sparse_configs,
            )

        else:
            logger.info(f"Creating new collection '{self.collection}'")
            await self.client.create_collection(
                collection_name=self.collection,
                sparse_vectors_config=sparse_configs,
            )

        await self.client.create_payload_index(
            collection_name=self.collection,
            field_name="search_space",
            field_schema=models.UuidIndexParams(
                type=models.UuidIndexType.UUID,
                is_tenant=True,
                on_disk=self.settings.idx_on_disk,
            ),
        )
        logger.info("Qdrant initialized successfully.")

    @retry()
    async def upsert_points(
        self,
        points: List[Point],
        collection_name: Optional[str] = None,
        wait: bool = True,
    ) -> None:
        """
        Upserts a list of Point objects into a Qdrant collection.
        """
        if not points:
            logger.debug("No points provided for upsert. Skipping.")
            return

        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)  # Validate collection name format

        if not self.client:
            raise RuntimeError(
                "Qdrant client not initialized. Call initialize() first."
            )

        qdrant_points: List[models.PointStruct] = []
        for point in points:
            if not point.node_id:
                raise ValueError("Missing node_id for a point during upsert.")
            if not point.embeddings:
                raise ValueError("Missing embeddings for a point during upsert.")

            qdrant_points.append(
                models.PointStruct(
                    id=str(point.node_id),
                    payload=point.payload,
                    vector=cast(models.VectorStruct, point.embeddings),
                )
            )

        try:
            await self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points,
                wait=wait,
            )
            logger.debug(
                f"Successfully upserted {len(qdrant_points)} points into collection '{collection_name}'."
            )
        except Exception as e:
            if not any(isinstance(e, e_type) for e_type in self.retry_on):
                logger.exception(
                    f"Qdrant upsert_points failed for collection '{collection_name}', first node: {points[0].node_id}."
                )
            raise

    @retry()
    async def upsert_relation(
        self,
        relation: Relation,
        collection_name: Optional[str] = None,
        wait: bool = True,
    ) -> None:
        """
        Upserts a Relation object (chunk, facts, facts) as points into a Qdrant collection.
        """
        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)

        chunk = relation.chunk
        fact_nodes = relation.facts
        for e in fact_nodes:
            if not e.node_id:
                raise ValueError("Missing node_id")

        try:
            await self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=str(cast(Id, chunk.node_id)),
                        payload=chunk.this_indexed_fields() | {"custom": chunk.custom},
                        vector=cast(models.VectorStruct, chunk.embeddings),
                    )
                ]
                + [
                    models.PointStruct(
                        id=str(cast(Id, n.node_id)),
                        payload={"search_space": n.search_space, "content": n.content},
                        vector=cast(models.VectorStruct, n.embeddings),
                    )
                    for n in fact_nodes
                ],
                wait=wait,
            )

            logger.debug(
                f"Successfully upserted {2 + len(fact_nodes)} vectors into collection '{collection_name}'."
            )

        except Exception as e:
            if not any(isinstance(e, e_type) for e_type in self.retry_on):
                logger.exception(
                    f"Qdrant upsert failed for collection '{collection_name}', nodes: {abbrev(relation)}."
                )
            raise

    @retry()
    @timeit(log_level=DEBUG, laps=1)
    async def classify(
        self,
        query_points: List[QueryPoint],
        pool: List[SemanticType],
        collection_name: Optional[str] = None,
    ) -> List[QueryPoint]:
        """
        Classifies query points by finding the most similar point in Qdrant using the 'classifiers' vector.
        """
        if not query_points:
            return []
        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)

        filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="semantic_type",
                    match=models.MatchAny(any=[t.value for t in pool]),
                )
            ]
        )

        try:
            for q in query_points:
                if bool(q.embeddings) == bool(q.node_id):
                    raise ValueError("Provide either embeddings or node_id")

                # Call query_points_groups for each individual query point
                groups_results = await self.client.query_points_groups(
                    collection_name=collection_name,
                    query=models.SparseVector(
                        **q.embeddings[
                            f"{q.node_type.value}_{EmbeddingName.SUMMARY.value}"
                        ]
                    ),
                    group_by="semantic_type",
                    limit=999,
                    group_size=1,
                    using="classifiers",
                    with_payload=True,
                    query_filter=filter,
                )

                q.semantic_types = set()
                max_score_for_query = 0.0
                semantic_type = None
                for group_result in groups_results.groups:
                    for hit in group_result.hits:
                        if not hit.score or hit.score < max_score_for_query:
                            continue

                        max_score_for_query = max(max_score_for_query, hit.score)
                        semantic_type = SemanticType(group_result.id)

                if semantic_type:
                    q.semantic_types.add(semantic_type)

        except Exception as e:
            if not any(isinstance(e, e_type) for e_type in self.retry_on):
                logger.exception(
                    f"Qdrant classification failed for collection '{collection_name}', nodes: {abbrev(query_points)}."
                )
            raise

        if logger.isEnabledFor(DEBUG):
            flat_results = [
                {"p": r, "node_type": p.node_type.value}
                for p in query_points
                if p.results
                for r in p.results
            ]

            if not flat_results:
                logger.debug("No classification results found.")
            else:
                log_msg = f"Classification results: {flat_results}"
                logger.debug(log_msg)

        return query_points

    @retry()
    @timeit(log_level=DEBUG, laps=1)
    async def get_points(
        self,
        query_points: List[QueryPoint],
        collection_name: Optional[str] = None,
        with_payload: bool | Sequence[str] = False,
    ) -> List[Point]:
        """
        Retrieves points from a Qdrant collection by their IDs.
        """
        if not query_points:
            return []
        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)

        results = await self.client.retrieve(
            collection_name=collection_name,
            ids=[q.node_id for q in query_points],
            with_payload=with_payload,
        )

        points = [Point(node_id=r.id, content=r.payload) for r in results]

        return points

    @retry()
    @timeit(log_level=DEBUG, laps=1)
    async def search_points(
        self,
        query_points: List[QueryPoint],
        search_space: uuid.UUID,
        threshold: float,
        limit: int = 30,
        oversampling: float = 2.0,
        collection_name: Optional[str] = None,
        explain: bool = False,
    ) -> List[QueryPoint]:
        """
        Finds matching points in Qdrant based on embedding similarity for a list of queries.
        Applies hybrid scoring if text_weight is provided.
        """
        if not query_points:
            return []
        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)

        try:
            filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="search_space",
                        match=models.MatchValue(value=str(search_space)),
                    ),
                ]
            )
            requests = []
            for q in query_points:
                if bool(q.embeddings) == bool(q.node_id):
                    raise ValueError("Provide either embeddings or node_id")
                requests += [
                    models.QueryRequest(
                        query=q.embeddings[
                            f"{q.node_type.value}_{EmbeddingName.CONTENT.value}"
                        ]
                        if q.embeddings
                        else q.node_id,
                        filter=filter,
                        limit=limit * oversampling,
                        using=f"{q.node_type.value}_{EmbeddingName.CONTENT.value}",
                        with_payload=True if q.text_weight or explain else None,
                    )
                ]

            if not requests:
                return []

            batch_results = await self.client.query_batch_points(
                collection_name=collection_name,
                requests=requests,
            )

            for i, response in enumerate(batch_results):
                results = query_points[i].results = [
                    Point(
                        node_id=r.id,
                        similarity=r.score,
                        content=(r.payload or {}).get("content"),
                    )
                    for r in response.points
                ]

                for r in results:
                    r.similarity = (
                        distance.JaroWinkler.similarity(
                            r.content, query_points[i].content
                        )
                        if r.content
                        else 0.0
                    )

                results = query_points[i].results = [
                    r for r in results if threshold <= cast(float, r.similarity)
                ]

                results.sort(key=lambda n: n.similarity or 0.0, reverse=True)
                results = query_points[i].results = results[:limit]

        except Exception as e:
            if not any(isinstance(e, e_type) for e_type in self.retry_on):
                logger.exception(
                    f"Qdrant query failed for collection '{collection_name}', nodes: {abbrev(query_points)}."
                )
            raise

        log_flat_results_needed = False
        if logger.isEnabledFor(DEBUG):
            log_flat_results_needed = True
        elif explain and logger.isEnabledFor(INFO):
            log_flat_results_needed = True

        if log_flat_results_needed:
            flat_results = [
                {"p": r, "node_type": p.node_type.value}
                for p in query_points
                if p.results
                for r in p.results
            ]

            if not flat_results:
                logger.debug("Nothing found.")

            log_msg = (
                f"Search space: {search_space}\nGraph entry points: {flat_results}"
            )
            if explain:
                logger.info(log_msg)
            else:
                logger.debug(log_msg)

        return query_points

    @retry()
    @timeit(log_level=DEBUG, laps=1)
    async def search_relations(
        self,
        query: QueryPoint,
        search_space: uuid.UUID,
        threshold: float,
        limit: int = 10,
        oversampling: float = 2.0,
        collection_name: Optional[str] = None,
        explain: bool = False,
    ) -> List[Point]:
        """
        Finds related points (chunks and facts) in Qdrant based on a query point.
        Applies hybrid scoring and groups facts results.
        """
        if query.node_type != NodeType.CHUNK:
            raise ValueError("Only `chunk` type is allowed in this function.")
        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)

        sample_size = max(1, int(limit * oversampling))

        conditions: List[models.Condition] = [
            models.FieldCondition(
                key="search_space",
                match=models.MatchValue(value=str(search_space)),
            ),
        ]
        filter = models.Filter(must=conditions)
        requests = [
            models.QueryRequest(
                prefetch=[
                    models.Prefetch(
                        query=query.embeddings[f"{NodeType.CHUNK.value}_{emb_type}"],
                        filter=filter,
                        limit=max(64, sample_size * 2),
                        using=f"{NodeType.CHUNK.value}_{emb_type.value}",
                    )
                    for emb_type in EmbeddingName
                ],
                query=models.FusionQuery(fusion=models.Fusion.DBSF),
                limit=max(32, sample_size),
                with_payload=True,
                score_threshold=threshold,
            ),
            models.QueryRequest(
                prefetch=[
                    models.Prefetch(
                        query=query.embeddings[f"{NodeType.CHUNK.value}_{emb_type}"],
                        filter=filter,
                        limit=max(64, sample_size * 2),
                        using=f"{NodeType.FACT.value}_{emb_type.value}",
                    )
                    for emb_type in EmbeddingName
                ],
                query=models.FusionQuery(fusion=models.Fusion.DBSF),
                limit=max(32, sample_size),
                with_payload=True,
                score_threshold=threshold,
            ),
        ]

        try:
            batch_response = await self.client.query_batch_points(
                collection_name=collection_name,
                requests=requests,
            )
            chunk_response, fact_response = batch_response[0], batch_response[1]

            chunk_results = [
                Point(
                    node_id=p.id,
                    similarity=p.score,
                    content=(p.payload or {}).get("content"),
                )
                for p in chunk_response.points
            ]

            fact_results = [
                Point(
                    node_id=p.id,
                    similarity=p.score,
                    content=(p.payload or {}).get("content"),
                )
                for p in fact_response.points
            ]

            rescale_similarity(fact_results, max_score=0.5)
            rescale_similarity(chunk_results, max_score=0.5)

            # logger.critical(f"chunks: {len(chunk_results)}")
            # logger.critical(f"facts: {len(fact_results)}")

            query.results = chunk_results + fact_results

        except Exception as e:
            if not any(isinstance(e, e_type) for e_type in self.retry_on):
                logger.exception(
                    f"Qdrant query failed for collection '{collection_name}', nodes: {abbrev(query)}."
                )
            raise

        if not query.results:
            logger.debug("Nothing found.")

        log_msg = f"Search space: {search_space}\nGraph entry points: {query.results}"
        if explain:
            logger.info(log_msg)
        else:
            logger.debug(log_msg)

        return query.results

    @retry()
    async def delete_points(
        self,
        point_ids: Sequence[uuid.UUID],
        collection_name: Optional[str] = None,
        flush_vectors: bool = True,
    ) -> Set[uuid.UUID]:
        """
        Deletes points from a Qdrant collection based on their IDs.
        Returns the IDs of the points that were targeted for deletion.
        """
        if not collection_name:
            collection_name = self.collection
        else:
            _ = decode_kv(collection_name)

        if not point_ids:
            logger.debug(
                f"No point IDs provided for deletion in collection '{collection_name}'. Skipping operation."
            )
            return set()

        point_ids_str = [str(p) for p in point_ids]
        deleted_point_ids: Set[uuid.UUID] = set()
        log_message_suffix = f"by IDs: {abbrev(point_ids)}"
        deleted_point_ids.update(point_ids)

        update_operations = [
            models.DeleteVectorsOperation(
                delete_vectors=models.DeleteVectors(
                    points=point_ids_str,
                    vector=[
                        f"{node_type.value}_{emb_type.value}"
                        for node_type in NodeType
                        for emb_type in EmbeddingName
                    ],
                )
            )
        ] + (
            [
                models.DeleteOperation(
                    delete=models.PointIdsList(points=point_ids_str)
                ),
            ]
            if flush_vectors
            else []
        )
        try:
            await self.client.batch_update_points(
                collection_name=collection_name, update_operations=update_operations
            )
            logger.debug(
                f"Successfully deleted points from collection '{collection_name}' {log_message_suffix}."
            )
        except Exception as e:
            if not any(isinstance(e, e_type) for e_type in self.retry_on):
                logger.exception(
                    f"Qdrant delete failed for collection '{collection_name}' {log_message_suffix}."
                )
            raise

        return deleted_point_ids


def from_filters(filters: IndexedFilters) -> models.Filter:
    """
    Translates an `IndexedFilters` instance into a Qdrant `models.Filter` object.
    Supports EQ, IN, LT, LTE, GT, GTE operators for field conditions.
    """
    qdrant_field_conditions: List[models.FieldCondition] = []
    standardized_conditions = filters.std_conditions()

    for key, cond_list in standardized_conditions.items():
        current_range_params: Dict[str, float | str] = {}
        is_datetime_range_for_key = False

        for condition in cond_list:
            if condition.operator == Operator.EQ:
                qdrant_field_conditions.append(
                    models.FieldCondition(
                        key=key, match=models.MatchValue(value=condition.value)
                    )
                )
            elif condition.operator == Operator.IN:
                if not isinstance(condition.value, list):
                    raise ValueError(
                        f"Operator 'IN' for key '{key}' requires a list value, but got {type(condition.value).__name__}."
                    )
                qdrant_field_conditions.append(
                    models.FieldCondition(
                        key=key, match=models.MatchAny(any=condition.value)
                    )
                )
            elif condition.operator in (
                Operator.LT,
                Operator.LTE,
                Operator.GT,
                Operator.GTE,
            ):
                value = condition.value
                if not isinstance(value, (int, float, str)):
                    raise ValueError(
                        f"Range operator '{condition.operator.name}' for key '{key}' "
                        f"requires a numeric or string value, but got {type(value).__name__}."
                    )

                if isinstance(value, str):
                    if is_iso_datetime_string(value):
                        is_datetime_range_for_key = True
                    else:
                        raise ValueError(
                            f"String value '{value}' for range operator '{condition.operator.name}' "
                            f"on key '{key}' is not a valid ISO 8601 datetime string. "
                            f"Qdrant range filters require numeric or datetime strings."
                        )
                elif not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Range operator '{condition.operator.name}' for key '{key}' "
                        f"requires a numeric value, but got {type(value).__name__}."
                    )

                if condition.operator == Operator.LT:
                    current_range_params["lt"] = value
                elif condition.operator == Operator.LTE:
                    current_range_params["lte"] = value
                elif condition.operator == Operator.GT:
                    current_range_params["gt"] = value
                elif condition.operator == Operator.GTE:
                    current_range_params["gte"] = value

        if current_range_params:
            if is_datetime_range_for_key:
                qdrant_field_conditions.append(
                    models.FieldCondition(
                        key=key, range=models.DatetimeRange(**current_range_params)
                    )
                )
            else:
                qdrant_field_conditions.append(
                    models.FieldCondition(
                        key=key, range=models.Range(**current_range_params)
                    )
                )

    return models.Filter(must=qdrant_field_conditions)


class HybridScoring:
    @staticmethod
    def get_fuzz_similarities(
        query_content: str, points: List[Point], max_score: float = 1.0
    ) -> Dict[Hashable, float]:
        """
        Calculates and normalizes text similarity ratios for points using `rapidfuzz.fuzz.ratio`.
        """
        raw_similarities: Dict[Hashable, float] = {
            p.node_id: fuzz.ratio(query_content, p.content) / 100.0
            for p in points
            if p.content
        }

        if not raw_similarities:
            return {}

        current_max_raw_score = max(raw_similarities.values())

        normalized_scores: Dict[Hashable, float] = {}
        if current_max_raw_score > 0:
            for node_id, score in raw_similarities.items():
                normalized_scores[node_id] = (score / current_max_raw_score) * max_score
        else:
            for node_id in raw_similarities.keys():
                normalized_scores[node_id] = 0.0

        return normalized_scores

    @staticmethod
    def get_jaro_winkler_similarities(
        query_content: str, points: List[Point], max_score: float = 1.0
    ) -> Dict[Hashable, float]:
        """
        Calculates and normalizes text similarity ratios for points using `rapidfuzz.distance.JaroWinkler.similarity`
        on individual words.
        """
        query_words = query_content.lower().split() if query_content else []

        if not query_words:
            return {p.node_id: 0.0 for p in points}

        raw_similarities: Dict[Hashable, float] = {}
        for p in points:
            if not p.content:
                raw_similarities[p.node_id] = 0.0
                continue

            point_name_parts = p.content.lower().split()

            max_similarity = 0.0
            max_similarity = max(
                (
                    distance.JaroWinkler.similarity(q_word, p_word)
                    for q_word in query_words
                    for p_word in point_name_parts
                ),
                default=0.0,
            )
            raw_similarities[p.node_id] = max_similarity

        if not raw_similarities:
            return {}

        current_max_raw_score = max(raw_similarities.values())

        if current_max_raw_score == 0:
            return {node_id: 0.0 for node_id in raw_similarities.keys()}

        normalized_scores: Dict[Hashable, float] = {}
        for node_id, score in raw_similarities.items():
            normalized_scores[node_id] = (score / current_max_raw_score) * max_score

        return normalized_scores

    @staticmethod
    def ratio(
        semantic_similarity: float,
        text_similarity: float,
        text_weight: Optional[float],
    ) -> float:
        """
        Calculates a hybrid score by combining vector similarity and text similarity
        based on a given `text_weight`.
        """
        if text_weight and text_similarity:
            semantic_similarity *= 1.0 - text_weight
            return semantic_similarity + text_weight * text_similarity
        return semantic_similarity
