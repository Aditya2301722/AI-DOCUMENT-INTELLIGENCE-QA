from __future__ import annotations

import ollama


class OllamaGenerator:
    """
    Local LLM generation service using Ollama.
    """

    def __init__(
        self,
        model: str = "qwen3:8b",
    ) -> None:
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generate a grounded answer using Ollama.
        """

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response["message"]["content"].strip()