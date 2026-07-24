from langchain_core.prompts import PromptTemplate


def create_rag_pipeline(retriever, llm):

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an AI PDF assistant.
Answer the question using only the information from the document.

Context:
{context}

Question:
{question}

Answer:
"""
    )


    def ask_question(question):

        
        docs = retriever.invoke(question)

        context = "\n\n".join(
            doc.page_content for doc in docs
        )

        final_prompt = prompt.format(
            context=context,
            question=question
        )

        response = llm.invoke(final_prompt)
        return response.content


    return ask_question