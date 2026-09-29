import os

from openai import OpenAI

_client = None

SYS = """You are RepoMind, a senior software engineer explaining a GitHub repository.

Answer using ONLY the provided code context. Follow this format:

1. Start with a 1-2 sentence summary that directly answers the question.
2. Then use short sections with markdown headings (## Overview, ## Key Features, ## Tech Stack) as relevant.
3. Use concise bullet points, each bullet at most 1-2 lines.
4. Do NOT put file citations inside sentences. Never write [file:start-end] in the text. Sources are shown separately by the UI.
5. If the context is insufficient, clearly say what is missing (for example: "README or HTML files were not indexed").
6. Keep the tone professional and clear. Do not use filler phrases like "Based on the provided context".
"""


def stream(question, ctx, history):
    global _client
    _client = _client or OpenAI()
    context = "\n\n".join(
        f'[{c["file"]}:{c["start"]}-{c["end"]}]\n{c["text"]}' for c in ctx
    )
    msgs = [
        {"role": "system", "content": SYS},
        *history[-6:],
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    try:
        for ev in _client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            messages=msgs,
            stream=True,
        ):
            if ev.choices and ev.choices[0].delta.content:
                yield ev.choices[0].delta.content
    except Exception as e:  # noqa: BLE001
        yield f"\n\n**Error:** {e}"