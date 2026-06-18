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

Answer ONLY using the provided context.

If the answer cannot be found in the context,
say:

"I could not find the answer in the provided content."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

        return prompt