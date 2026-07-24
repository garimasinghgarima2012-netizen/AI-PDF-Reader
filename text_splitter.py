from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(raw_text):
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=100,
        length_function=len
    )

    chunks = text_splitter.split_text(raw_text)

    return chunks