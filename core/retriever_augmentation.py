def get_relevant_context(db, user_query: str, k: int = 3) -> str:
    docs = db.similarity_search(user_query, k=k)
    if not docs:
        return "No relevant context found for your question."
    return "\n\n".join([doc.page_content for doc in docs])