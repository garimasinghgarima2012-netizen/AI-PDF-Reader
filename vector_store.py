import cassio
from langchain_community.vectorstores import Cassandra

from config import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_ID


def create_vector_store(embedding_model):

    cassio.init(
        token=ASTRA_DB_APPLICATION_TOKEN,
        database_id=ASTRA_DB_ID
    )

    vector_store = Cassandra(
    embedding=embedding_model,
    table_name="pdf_documents",
    keyspace="default_keyspace"
)

    return vector_store


def store_chunks(vector_store, chunks):

    vector_store.add_texts(chunks)

    print("Chunks stored successfully!")