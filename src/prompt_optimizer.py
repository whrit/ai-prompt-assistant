from typing import Literal

def optimize(prompt: str, mode: Literal["baseline","optimized"]) -> str:
    if mode == "baseline":
        return prompt
    # simple micro-transforms; replace with model call later
    instructions = (
        "You are precise and concise. "
        "Clarify the goal, specify format, avoid speculation, and ask one clarifying question if needed."
    )
    return f"{instructions}\n\nTask:\n{prompt}\n\nOutput: Provide the answer. If missing info, ask one question first."