from langchain_core.prompts import PromptTemplate


def create_rag_pipeline(retriever, llm):
    """
    Creates an end-to-end RAG pipeline that retrieves top matching document chunks,
    preserves page metadata for citations, maintains conversational history context,
    and returns a clean structured response.
    """
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template="""You are DocuMind AI, an intelligent and precise document assistant.
Answer the user's question accurately and concisely using ONLY the provided document context.
If the information is not present in the context, say: "I could not find this information in the document."

Document Context:
{context}

{chat_history}User Question:
{question}

Helpful Answer:""",
    )

    def ask_question(question, chat_history=None):
        docs = retriever.invoke(question)

        context_parts = []
        sources = []

        for doc in docs:
            page = doc.metadata.get("page")
            if page is not None:
                sources.append(page)
                page_header = f"[Page {page}]"
            else:
                page_header = "[Document Section]"

            context_parts.append(f"{page_header}\n{doc.page_content.strip()}")

        context = "\n\n---\n\n".join(context_parts)

        # Format recent chat history if provided
        history_text = ""
        if chat_history and len(chat_history) > 0:
            formatted_history = []
            for item in chat_history[-6:]:  # Include up to last 3 conversation turns
                role = "User" if item.get("role") == "user" else "Assistant"
                formatted_history.append(f"{role}: {item.get('content', '')}")
            history_text = "Recent Conversation History:\n" + "\n".join(formatted_history) + "\n\n"

        final_prompt = prompt.format(
            context=context if context.strip() else "No relevant context found.",
            chat_history=history_text,
            question=question,
        )

        response = llm.invoke(final_prompt)

        return {
            "answer": response.content,
            "sources": sorted(list(set(sources))),
            "docs": docs,
        }

    return ask_question