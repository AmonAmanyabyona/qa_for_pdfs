from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    """Formats retrieved documents into plain text."""
    return "\n\n".join(doc.page_content for doc in docs)
