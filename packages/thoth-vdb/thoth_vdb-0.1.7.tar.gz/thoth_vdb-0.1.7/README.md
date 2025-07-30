# Thoth Virtual Database Management
A library for managing vector databases inside the Thoth project.
## Features

- Unified interface for multiple vector database backends
- Easy integration with Thoth project components
- Support for CRUD operations on vector data
- Extensible and modular design

## Installation

```bash
pip install thoth-vdb
```

## Usage

```python
from thoth_vdb import vdbmanager

# Initialize the manager
manager = vdbmanager.QdrantHaystackStore(
    host="localhost",
    port=6333,
    api_key=None,  # or your Qdrant API key if required
    collection_name="my_collection"  # specify your collection name
)
# Thoth Documents managed
    - ThothType(Enum): An enumeration defining the types of documents supported:
        * COLUMN_NAME: For descriptions of database columns.
        * HINT: For general hints or suggestions.
        * SQL: For SQL query examples.
        * DOCUMENTATION: For general documentation text.
    - BaseThothDocument(BaseModel): The base class for all document types. It includes common fields like id (UUID string), thoth_type (from ThothType), and text (the content used for embedding/searching).
    - ColumnNameDocument(BaseThothDocument): Represents a column description. Inherits from BaseThothDocument and adds specific fields: table_name, column_name, original_column_name, column_description, value_description. Its thoth_type is fixed to ThothType.COLUMN_NAME.
    - SqlDocument(BaseThothDocument): Represents an SQL example. Inherits from BaseThothDocument and adds question and sql fields. Its thoth_type is fixed to ThothType.SQL.
    - HintDocument(BaseThothDocument): Represents a hint. Inherits from BaseThothDocument and adds a hint field. Its thoth_type is fixed to ThothType.HINT.
    - DocumentationDocument(BaseThothDocument): Represents general documentation. Inherits from BaseThothDocument and adds a content field. Its thoth_type is fixed to ThothType.DOCUMENTATION.

# API

The `ThothHaystackVectorStore` provides a unified API for managing specialized document types within a vector database. It allows adding individual or bulk documents (Column Descriptions, SQL Examples, Hints, Documentation), retrieving specific documents by ID or type, performing semantic searches based on text queries, and fetching information about the underlying database collection.

## Adding Documents:
    - add_column_description(doc: ColumnNameDocument) -> str: Adds a column description document. (Abstract)
    - add_sql(doc: SqlDocument) -> str: Adds an SQL example document. (Abstract)
    - add_hint(doc: HintDocument) -> str: Adds a hint document. (Abstract)
    - add_documentation(doc: DocumentationDocument) -> str: Adds a documentation document. (Abstract)
    - bulk_add_documents(documents: List[BaseThothDocument]) -> List[str]: Adds multiple documents of potentially different types in a single batch operation.

## Retrieving Documents:
    - search_similar(query: str, doc_type: ThothType, top_k: int = 5, score_threshold: float = 0.7) -> List[BaseThothDocument]: Performs a similarity search for documents of a specific type based on a query string. (Abstract)
    - get_document(doc_id: str) -> Optional[BaseThothDocument]: Retrieves a single document by its unique ID, regardless of type. (Abstract)
    - get_all_documents(doc_type: ThothType) -> List[BaseThothDocument]: Retrieves all documents of a specific type.
    - get_all_column_documents() -> List[ColumnNameDocument]: Retrieves all column description documents.
    - get_all_sql_documents() -> List[SqlDocument]: Retrieves all SQL example documents.
    - get_all_hint_documents() -> List[HintDocument]: Retrieves all hint documents.
    - get_all_documentation_documents() -> List[DocumentationDocument]: Retrieves all documentation documents.
    - get_columns_document_by_id(doc_id: str) -> Optional[ColumnNameDocument]: Retrieves a specific column document by ID.
    - get_sql_document_by_id(doc_id: str) -> Optional[SqlDocument]: Retrieves a specific SQL document by ID.
    - get_hint_document_by_id(doc_id: str) -> Optional[HintDocument]: Retrieves a specific hint document by ID.
    - get_documentation_document_by_id(doc_id: str) -> Optional[DocumentationDocument]: Retrieves a specific documentation document by ID.

## Collection Information:
    - get_collection_info() -> Dict[str, Any]: Retrieves metadata or information about the underlying vector store collection. (Abstract)

## Supported Backends
- **Qdrant**: Implemented via `QdrantHaystackStore`.
    - Initializes connection using `collection` name, `host`, and `port`.
    - Uses `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) for text embeddings by default, managed through Haystack components.
    - Implements `search_similar` using Haystack's `QdrantEmbeddingRetriever`.
    - `get_collection_info` fetches details directly from the Qdrant collection.

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
