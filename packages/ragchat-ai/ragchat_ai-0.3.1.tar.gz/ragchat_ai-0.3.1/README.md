# RagChat

RagChat enables interaction between large language models and unstructured data. It addresses challenges such as dynamic content updates, varied data sources, and retrieval accuracy by using an upsert-first architecture, filtering mechanisms, and a combination of knowledge graphs with vector search. It supports multi-user, custom models, and self-hosting to provide operational control.

---

## Features
- **Upsert-first design:** Supports constant updates.
- **Flexible metadata filtering:** Information retrieval allows using custom fields.
- **Efficient knowledge graph:** Graph is built using small models, promoting efficiency and scalability.
- **Multiuser support:** Knowledge bases can be isolated or shared.
- **Language consistency:** Prompts and examples use the specified language, improving reliability.
- **Async batch processing:** Ingestion of multiple documents can be done in parallel with streaming progress updates.
- **Pluggable LLMs and Embedding models:** Supports the use of custom models or connection to API endpoints; providers are easily swappable.
- **Open source & self-hostable:** Operation occurs locally in Docker or directly on a machine, ensuring privacy.

## Use Cases
- Casual chat sessions with memories
- Technical documentation search
- Chat+file hybrid RAG with citations
- Personal use
- Multi-user setups

---

## Quick start
Docker Compose is required for the easiest setup.

Install RagChat with pip:
```bash
pip install ragchat-ai
```

Recommended local models:
- `bge-m3` for embeddings
- `qwen3:4b` or `qwen3:8b` for LLM -- *Make sure 8k context length is supported.*

Configure environment variables:
```bash
git clone https://github.com/raul3820/ragchat.git
cd ragchat
cp .env.example .env
```

## Example: Open Webui

Run dependencies with:
```bash
docker compose up --build
```

After startup, the web chat UI is accessible at http://localhost:3001 (refer to .env for port).

Retrieval will be applied to all models. Two flows are presented:
- Casual chat with memories (default)
- Formal RAG with citations (triggered by writing `#` in the chat and selecting a file)

For file ingestion use: http://localhost:3001/workspace/knowledge


## Example: Lihua benchmark with Python SDK

Run dependencies with:
```bash
docker compose up neo4j qdrant --build
```

Once the DB has started, run the file ingestion with:
```python
python -m examples.lihua.step0_index --full
```

and the Q&A with
```python
python -m examples.lihua.step1_qa --test recall --limit 5
```

---

## Contributing
Contributions welcomed! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to contribute.

- Bug reports (issues)
- Feature suggestions
- Pull requests (inclusion of tests requested)


<details>
<summary>Roadmap</summary>

**Performance:**
- [x] Quick retrieval
- [x] Hybrid search
- [x] Multi-hop fact search
- [ ] Query intent classification
- [x] Recency weighting
- [ ] Better reranking
- [ ] Structured aggregates
- [ ] 3 phase ingestion (bm25, summaries, fact-entities)
- [ ] Graph traversal
- [ ] Custom tuning

**Flows:**
- [x] Chat
- [x] File
- [ ] Group chat
- [ ] Code
- [ ] Web search

**Integrations:**
- [x] Python SDK
- [ ] REST API server
- [x] Neo4j
- [x] Qdrant
- [ ] Memgraph? (lower priority)
- [ ] Docling
- [ ] MCP
- [x] Open-Webui (pipelines)

**Testing & Evals:**
- [x] LiHua benchmark setup
- [ ] LiHua benchmark comparison with other libraries
- [x] Integration test
- [ ] Increase test coverage

**Security:**
- [x] Custom fields sanitization

**Documentation:**
- [x] Readme/Quick start
- [ ] Library documentation
- [ ] API documentation

</details>

---

## Open Source & License
RagChat is MIT-licensed (see LICENSE). Self-hosting and extension are permitted. Certain features may require user-provided LLM/API keys.
