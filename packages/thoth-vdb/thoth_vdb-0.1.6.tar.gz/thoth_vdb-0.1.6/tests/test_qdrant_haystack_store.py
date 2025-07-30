import pytest
import uuid
from typing import List
import time # Added import

# Assuming Qdrant is running on localhost:6333
# Assuming sentence-transformers model is available

from vdbmanager.impl.QdrantHaystackStore import QdrantHaystackStore
from vdbmanager.ThothVectorStore import (
    BaseThothDocument,
    ColumnNameDocument,
    SqlDocument,
    HintDocument,
    DocumentationDocument,
    ThothType,
)

# Use a unique collection name for testing to avoid conflicts
TEST_COLLECTION_NAME = f"test_collection_{uuid.uuid4()}"

@pytest.fixture(scope="module")
def vector_store():
    """Fixture to create and cleanup the QdrantHaystackStore instance."""
    store = QdrantHaystackStore(collection=TEST_COLLECTION_NAME)
    # Ensure the collection is empty before tests
    store.delete_collection()
    yield store
    # Cleanup after tests
    print(f"\nCleaning up test collection: {TEST_COLLECTION_NAME}")
    try:
        store.delete_collection()
        # Attempt to delete the collection itself via the client if possible
        # This might require accessing the underlying client directly
        # store.store._client.delete_collection(collection_name=TEST_COLLECTION_NAME)
        print(f"Test collection {TEST_COLLECTION_NAME} cleaned up.")
    except Exception as e:
        print(f"Error during cleanup of collection {TEST_COLLECTION_NAME}: {e}")


@pytest.fixture
def sample_column_doc() -> ColumnNameDocument:
    """Sample ColumnNameDocument."""
    return ColumnNameDocument(
        table_name="customers",
        column_name="email_address",
        original_column_name="EMAIL",
        column_description="The primary email address of the customer.",
        value_description="Must be a valid email format.",
    )

@pytest.fixture
def sample_sql_doc() -> SqlDocument:
    """Sample SqlDocument."""
    return SqlDocument(
        question="show me total sales per region",
        sql="SELECT region, SUM(sales) FROM orders GROUP BY region;",
    )

@pytest.fixture
def sample_hint_doc() -> HintDocument:
    """Sample HintDocument."""
    return HintDocument(
        hint="Remember to filter out inactive users for most reports.",
    )

@pytest.fixture
def sample_doc_doc() -> DocumentationDocument:
    """Sample DocumentationDocument."""
    return DocumentationDocument(
        content="The user authentication system uses JWT tokens with a 15-minute expiry.",
    )


# --- Basic Add and Get Tests ---

def test_add_and_get_column_doc(vector_store: QdrantHaystackStore, sample_column_doc: ColumnNameDocument):
    """Test adding and retrieving a ColumnNameDocument."""
    doc_id = vector_store.add_column_description(sample_column_doc)
    assert isinstance(doc_id, str)
    # Use the specific getter
    retrieved_doc = vector_store.get_columns_document_by_id(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc_id # Check if ID matches (might be overwritten by Haystack)
    assert retrieved_doc.thoth_type == ThothType.COLUMN_NAME
    assert retrieved_doc.table_name == sample_column_doc.table_name
    assert retrieved_doc.column_name == sample_column_doc.column_name
    assert retrieved_doc.column_description == sample_column_doc.column_description

    # Use the generic getter
    retrieved_generic = vector_store.get_document_by_id(doc_id, output_type=ColumnNameDocument)
    assert retrieved_generic is not None
    assert retrieved_generic.id == doc_id


def test_add_and_get_sql_doc(vector_store: QdrantHaystackStore, sample_sql_doc: SqlDocument):
    """Test adding and retrieving an SqlDocument."""
    doc_id = vector_store.add_sql(sample_sql_doc)
    assert isinstance(doc_id, str)
    retrieved_doc = vector_store.get_sql_document_by_id(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc_id
    assert retrieved_doc.thoth_type == ThothType.SQL
    assert retrieved_doc.question == sample_sql_doc.question
    assert retrieved_doc.sql == sample_sql_doc.sql


def test_add_and_get_hint_doc(vector_store: QdrantHaystackStore, sample_hint_doc: HintDocument):
    """Test adding and retrieving a HintDocument."""
    doc_id = vector_store.add_hint(sample_hint_doc)
    assert isinstance(doc_id, str)
    retrieved_doc = vector_store.get_hint_document_by_id(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc_id
    assert retrieved_doc.thoth_type == ThothType.HINT
    assert retrieved_doc.hint == sample_hint_doc.hint


def test_add_and_get_doc_doc(vector_store: QdrantHaystackStore, sample_doc_doc: DocumentationDocument):
    """Test adding and retrieving a DocumentationDocument."""
    doc_id = vector_store.add_documentation(sample_doc_doc)
    assert isinstance(doc_id, str)
    retrieved_doc = vector_store.get_documentation_document_by_id(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc_id
    assert retrieved_doc.thoth_type == ThothType.DOCUMENTATION
    assert retrieved_doc.content == sample_doc_doc.content


def test_get_non_existent_doc(vector_store: QdrantHaystackStore):
    """Test retrieving a non-existent document."""
    non_existent_id = "non-existent-id"
    assert vector_store.get_document_by_id(non_existent_id) is None
    assert vector_store.get_columns_document_by_id(non_existent_id) is None
    assert vector_store.get_sql_document_by_id(non_existent_id) is None
    assert vector_store.get_hint_document_by_id(non_existent_id) is None
    assert vector_store.get_documentation_document_by_id(non_existent_id) is None


# --- Update Tests ---

def test_update_column_doc(vector_store: QdrantHaystackStore, sample_column_doc: ColumnNameDocument):
    """Test updating a ColumnNameDocument."""
    doc_id = vector_store.add_column_description(sample_column_doc)
    retrieved_doc = vector_store.get_columns_document_by_id(doc_id)
    assert retrieved_doc is not None
    assert retrieved_doc.column_description == sample_column_doc.column_description

    # Update the description
    updated_description = "Updated: The primary email address used for login and notifications."
    retrieved_doc.column_description = updated_description
    # The update method in ThothHaystackVectorStore uses add_document with OVERWRITE
    vector_store.update_document(retrieved_doc) # Use the generic update method

    # Retrieve again and check update
    retrieved_after_update = vector_store.get_columns_document_by_id(doc_id)
    assert retrieved_after_update is not None
    assert retrieved_after_update.id == doc_id
    assert retrieved_after_update.column_description == updated_description
    # Ensure other fields remain the same
    assert retrieved_after_update.table_name == sample_column_doc.table_name


# --- Delete Tests ---

def test_delete_sql_doc(vector_store: QdrantHaystackStore, sample_sql_doc: SqlDocument):
    """Test deleting an SqlDocument."""
    doc_id = vector_store.add_sql(sample_sql_doc)
    assert vector_store.get_sql_document_by_id(doc_id) is not None

    vector_store.delete_document(doc_id)
    assert vector_store.get_sql_document_by_id(doc_id) is None


# --- Bulk Add and Get All Tests ---

def test_bulk_add_and_get_all_hints(vector_store: QdrantHaystackStore):
    """Test bulk adding and retrieving all HintDocuments."""
    hints = [
        HintDocument(hint="Hint 1: Check data types."),
        HintDocument(hint="Hint 2: Use appropriate JOINs."),
        HintDocument(hint="Hint 3: Index frequently queried columns."),
    ]
    # Assign specific IDs for easier checking if needed, otherwise rely on generated ones
    # hints[0].id = "hint-id-1"
    # hints[1].id = "hint-id-2"
    # hints[2].id = "hint-id-3"

    doc_ids = vector_store.bulk_add_documents(hints)
    assert len(doc_ids) == len(hints)
    assert all(isinstance(doc_id, str) for doc_id in doc_ids)

    # Allow some time for indexing if necessary (though Qdrant is usually fast)
    import time
    time.sleep(1)

    all_hints = vector_store.get_all_hint_documents()
    assert len(all_hints) >= len(hints) # Use >= in case other tests added hints

    # Check if the added hints are present
    added_hints_retrieved = {h.hint for h in all_hints if h.id in doc_ids}
    expected_hints = {h.hint for h in hints}
    assert added_hints_retrieved == expected_hints


def test_get_all_when_empty(vector_store: QdrantHaystackStore):
    """Test get_all methods when no documents of that type exist."""
    # Ensure clean state for a specific type (e.g., SQL) by deleting any existing ones
    existing_sql_docs = vector_store.get_all_sql_documents()
    if existing_sql_docs:
        vector_store.delete_documents([doc.id for doc in existing_sql_docs])
        time.sleep(0.5) # Give time for deletion

    assert vector_store.get_all_sql_documents() == []


# --- Search Tests ---

# Helper to add docs and wait for indexing
def add_docs_for_search(vector_store: QdrantHaystackStore, docs: List[BaseThothDocument]):
    vector_store.bulk_add_documents(docs)
    # Wait a bit to ensure documents are indexed before searching
    # Adjust sleep time if needed based on Qdrant performance/setup
    time.sleep(2)


def test_search_similar_column_docs(vector_store: QdrantHaystackStore):
    """Test similarity search for ColumnNameDocuments."""
    docs_to_add = [
        ColumnNameDocument(table_name="users", column_name="user_id", original_column_name="ID", column_description="Unique identifier for the user.", value_description="Integer"),
        ColumnNameDocument(table_name="users", column_name="username", original_column_name="user_name", column_description="Login name for the user.", value_description="String, unique"),
        ColumnNameDocument(table_name="products", column_name="product_id", original_column_name="prod_id", column_description="Unique identifier for the product.", value_description="Integer"),
        ColumnNameDocument(table_name="products", column_name="price", original_column_name="PRICE", column_description="Retail price of the product.", value_description="Decimal"),
    ]
    add_docs_for_search(vector_store, docs_to_add)

    query = "identifier for users"
    results = vector_store.search_similar(query, ThothType.COLUMN_NAME, top_k=2, score_threshold=0.5) # Lower threshold for testing

    assert len(results) > 0
    assert len(results) <= 2
    assert all(isinstance(doc, ColumnNameDocument) for doc in results)
    # Expect the 'user_id' document to be the most relevant
    assert results[0].column_name == "user_id"
    # Check if 'username' or 'product_id' might also appear depending on embedding similarity
    result_cols = {doc.column_name for doc in results}
    assert "user_id" in result_cols


def test_search_similar_sql_docs(vector_store: QdrantHaystackStore):
    """Test similarity search for SqlDocuments."""
    docs_to_add = [
        SqlDocument(question="Find all customers in California", sql="SELECT * FROM customers WHERE state = 'CA';"),
        SqlDocument(question="Count orders per customer", sql="SELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id;"),
        SqlDocument(question="Show customers from Texas", sql="SELECT name, city FROM customers WHERE state = 'TX';"),
    ]
    add_docs_for_search(vector_store, docs_to_add)

    query = "list customers by state"
    results = vector_store.search_similar(query, ThothType.SQL, top_k=2, score_threshold=0.5)

    assert len(results) > 0
    assert len(results) <= 2
    assert all(isinstance(doc, SqlDocument) for doc in results)
    # Expect 'California' and 'Texas' examples to be most relevant
    result_questions = {doc.question for doc in results}
    assert "Find all customers in California" in result_questions or "Show customers from Texas" in result_questions


def test_search_similar_hint_docs(vector_store: QdrantHaystackStore):
    """Test similarity search for HintDocuments."""
    docs_to_add = [
        HintDocument(hint="Optimize queries using indexes."),
        HintDocument(hint="Normalize database tables to reduce redundancy."),
        HintDocument(hint="Use connection pooling for better performance."),
    ]
    add_docs_for_search(vector_store, docs_to_add)

    query = "database performance tips"
    results = vector_store.search_similar(query, ThothType.HINT, top_k=2, score_threshold=0.5)

    assert len(results) > 0
    assert len(results) <= 2
    assert all(isinstance(doc, HintDocument) for doc in results)
    result_hints = {doc.hint for doc in results}
    assert "Use connection pooling for better performance." in result_hints or "Optimize queries using indexes." in result_hints


def test_search_similar_doc_docs(vector_store: QdrantHaystackStore):
    """Test similarity search for DocumentationDocuments."""
    docs_to_add = [
        DocumentationDocument(content="API rate limits are 100 requests per minute."),
        DocumentationDocument(content="The reporting module generates PDF reports."),
        DocumentationDocument(content="User passwords must be at least 12 characters long."),
    ]
    add_docs_for_search(vector_store, docs_to_add)

    query = "information about api limits"
    results = vector_store.search_similar(query, ThothType.DOCUMENTATION, top_k=1, score_threshold=0.5)

    assert len(results) == 1
    assert isinstance(results[0], DocumentationDocument)
    assert "API rate limits" in results[0].content


def test_search_with_no_results(vector_store: QdrantHaystackStore):
    """Test search when no relevant documents are found."""
    query = "non_existent_topic_xyz_123"
    results = vector_store.search_similar(query, ThothType.COLUMN_NAME, top_k=5, score_threshold=0.9)
    assert len(results) == 0


def test_search_different_types(vector_store: QdrantHaystackStore, sample_column_doc, sample_sql_doc):
    """Test that search only returns docs of the specified type."""
    vector_store.add_column_description(sample_column_doc)
    vector_store.add_sql(sample_sql_doc)
    time.sleep(2) # Indexing time

    # Search for something related to the column doc, but specify SQL type
    query = sample_column_doc.column_description
    results = vector_store.search_similar(query, ThothType.SQL, top_k=5, score_threshold=0.1) # Very low threshold

    # Should not find the column doc because we filtered by SQL type
    assert all(doc.thoth_type == ThothType.SQL for doc in results)
    column_doc_found = any(doc.id == sample_column_doc.id for doc in results)
    assert not column_doc_found

    # Search for something related to the SQL doc, but specify COLUMN type
    query = sample_sql_doc.question
    results = vector_store.search_similar(query, ThothType.COLUMN_NAME, top_k=5, score_threshold=0.1)

    # Should not find the SQL doc
    assert all(doc.thoth_type == ThothType.COLUMN_NAME for doc in results)
    sql_doc_found = any(doc.id == sample_sql_doc.id for doc in results)
    assert not sql_doc_found
