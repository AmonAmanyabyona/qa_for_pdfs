from langchain_chroma import Chroma

def create_vectorstore(chunks, embedding_function, vectorstore_path):
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=vectorstore_path
    )
    return vectorstore  

def load_vectorstore(vectorstore_path, embedding_function):
    return Chroma(persist_directory=vectorstore_path, embedding_function=embedding_function)
