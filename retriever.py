def get_retriever(vector_store, k=4, search_type="similarity"):
    """
    Returns a retriever configured from the vector store with top-k retrieval.
    """
    return vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k}
    )