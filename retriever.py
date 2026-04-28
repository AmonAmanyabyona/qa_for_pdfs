def get_retriever(vectorstore):
    return vectorstore.as_retriever(search_type="similarity")

def retrieve_chunks(retriever, query):
    return retriever.invoke(query)
