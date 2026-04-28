#from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings

# def get_embedding_function():
#     return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
from langchain_openai import OpenAIEmbeddings

def get_embedding_function():
    return OpenAIEmbeddings(model="text-embedding-3-small")