import cassio
from langchain_community.vectorstores import Cassandra

from config import ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_ID


def create_vector_store(embedding_model):
    
    cassio.init(
        token=ASTRA_DB_APPLICATION_TOKEN,
        database_id=ASTRA_DB_ID
    )

    # Create vector store
    vector_store = Cassandra(
        embedding=embedding_model,
        table_name="pdf_documents",
        keyspace="default_keyspace"
    )

    return vector_store


def store_chunks(vector_store, chunks):
   
    try:
        vector_store.delete_collection()
        print("Old vectors deleted.")

        # Recreate the collection
        vector_store = create_vector_store(vector_store.embedding)
        print("New collection created.")

    except Exception as e:
        print(f"No previous collection found or couldn't delete it: {e}")

   
    vector_store.add_texts(chunks)

    print("Chunks stored successfully!")

    return vector_store
