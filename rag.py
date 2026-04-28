from retriever import retrieve_chunks
from formatter import format_docs
from chat_complettion import chat_with_model

def rag_chain(question: str, retriever, previous_answer: str = None) -> str:
    retrieved_docs = retrieve_chunks(retriever, question)
    formatted_context = format_docs(retrieved_docs)

    history_context = f"\nPrevious answer: {previous_answer}\n" if previous_answer else ""

    prompt = f"""
You are a precise document assistant. Answer questions strictly based on the document text below.

Rules:
- Only use information explicitly written in the context. Do not infer or assume anything beyond what is stated.
- Never answer questions about ownership, legal status, or roles unless the document uses those exact words. If someone asks "who owns X" but the document only mentions a landlord or housing provider, say the document does not state ownership information.
- If the user asks about something not in the document, reply: "That topic isn't covered in this document. I can only answer questions about its contents."
- If the user asks what the document is about or what you can help with, give a brief factual summary of the document contents.
- Do not say "According to the document" or "Based on the context." Just answer directly and factually.
- Keep answers short and precise.

{history_context}
Context:
{formatted_context}

Question:
{question}
"""
    response = chat_with_model(prompt)

    if not response.strip():
        raise ValueError("Empty response from model")

    return response