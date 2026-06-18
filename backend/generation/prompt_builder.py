class PromptBuilder:

    @staticmethod
    def build_prompt(
        query,
        retrieved_chunks
    ):

        context = "\n\n".join(

            chunk["text"]

            for chunk

            in retrieved_chunks
        )

        prompt = f"""
You are a helpful AI assistant.

Use ONLY the information provided in the context.

Rules:
1. Do not use outside knowledge.
2. If the answer is not present in the context, reply exactly:
   "I could not find the answer in the provided content."
3. When the context contains a list, steps, components, features, benefits, or examples, include ALL relevant items.
4. Preserve structure from the context whenever possible.
5. When code examples are present, include the code.
6. When multiple relevant chunks are provided, combine them into a complete answer.
7. Be concise but complete.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

        return prompt