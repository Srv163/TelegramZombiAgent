import os, random
from tenacity import retry, wait_random_exponential, stop_after_attempt
from .config import settings
from .prompts import SYSTEM_PROMPT

def _stub_transform(text: str, level: int = 2, length: str = "medium") -> str:
    # Fallback when no OPENAI_API_KEY provided
    tag = {1: "слегка испортили", 2: "мрачная версия", 3: "абсурдный кошмар"}.get(level, "зомби-версия")
    prefix = f"[{tag}] "
    # very naive inversion
    repl = text.replace("хорош", "плох").replace("отличн", "сомн").replace("успех", "провал")
    return prefix + (repl if repl else "Сегодня отличный день, чтобы напомнить себе, что всё идёт под откос.")

@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
def zombify(text: str, style_profile: dict | None, level: int, length: str) -> str:
    if not settings.OPENAI_API_KEY:
        return _stub_transform(text, level, length)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        user_prompt = f"""Исходный пост (язык: ru):
"""{text}"""

Контекст канала-источника (JSON): {style_profile or {}}
Требования:
- Степень зомбификации: {level}
- Длина: {length}
- Добавь 1-2 чёрные шутки без запрещённого.
- Избегай копирования буквальных оборотов из исходника.
- Если пост — новость, сделай мрачный прогноз.
"""
        resp = client.chat.completions.create(
            model="gpt-5-thinking",
            messages=[{"role":"system","content": SYSTEM_PROMPT},
                      {"role":"user","content": user_prompt}],
            temperature=0.9,
            presence_penalty=0.6,
            frequency_penalty=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # fallback
        return _stub_transform(text, level, length)

def safety_guard(text: str) -> dict:
    # TODO: integrate moderation endpoint; simple placeholder
    flags = {}
    blocked_terms = ["суицид", "убей", "ненависть к", "разжиг"]
    if any(bt in (text or "").lower() for bt in blocked_terms):
        flags["blocked"] = True
    return flags

def is_too_similar(src: str, out: str) -> bool:
    if not src or not out:
        return False
    src_set = set(src.lower().split())
    out_set = set(out.lower().split())
    if not src_set:
        return False
    overlap = len(src_set & out_set) / max(1, len(out_set))
    return overlap > 0.7