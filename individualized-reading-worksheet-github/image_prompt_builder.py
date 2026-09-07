"""Prompt builder for individualized-reading-worksheet image generation.

The Skill/LLM is responsible for pedagogy and text adaptation. This module turns
already-prepared worksheet JSON into consistent, low-distraction educational
image prompts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


BASE_STYLE = """
Create a warm, gentle educational storybook illustration for a Taiwanese elementary-school
special-education reading worksheet. Clean composition, soft harmonious colors, low visual
clutter, clear facial expressions and body actions, age-appropriate realistic proportions,
and one obvious focal action. The image must support reading comprehension rather than serve
as decoration. No text, no letters, no captions, no speech bubbles, no labels, no watermark,
no logo. Avoid busy backgrounds, tiny decorative objects, dramatic lighting, or distracting
patterns.
""".strip()


@dataclass(frozen=True)
class PromptConfig:
    audience: str = "elementary special-education students"
    locale: str = "Taiwan"
    style: str = BASE_STYLE


def _join_text(lines: str | Sequence[str]) -> str:
    if isinstance(lines, str):
        return lines.strip()
    return " ".join(x.strip() for x in lines if x and x.strip())


def _join_keywords(keywords: Iterable[str] | None) -> str:
    if not keywords:
        return ""
    cleaned = [str(x).strip() for x in keywords if str(x).strip()]
    return "、".join(cleaned)


def build_prediction_prompt(title: str, prediction_prompt: str = "", *, config: PromptConfig | None = None) -> str:
    config = config or PromptConfig()
    return f"""
{config.style}

Illustration purpose: pre-reading prediction from a lesson title.
Lesson title concept: {title}
Teacher's prediction question/context: {prediction_prompt or 'Predict the likely topic from the lesson title.'}

Show 3-5 coherent visual clues that belong to the same overall theme, arranged naturally in one scene.
Do not reveal a multiple-choice answer through written text. Keep the scene understandable at a glance.
""".strip()


def build_section_prompt(
    section_title: str,
    text: str | Sequence[str],
    *,
    keywords: Iterable[str] | None = None,
    level: str = "",
    visual_brief: str = "",
    config: PromptConfig | None = None,
) -> str:
    config = config or PromptConfig()
    body = _join_text(text)
    kw = _join_keywords(keywords)
    level_note = level or "individualized reading worksheet"

    return f"""
{config.style}

Illustration purpose: paragraph comprehension for {level_note}.
Section/topic: {section_title or 'Reading paragraph'}
Paragraph meaning: {body}
Important concepts: {kw or 'Use the paragraph to identify the central people, action, emotion, and setting.'}
Additional visual brief: {visual_brief or 'Depict only the main event and emotion from this paragraph.'}

Composition requirements:
- Show the central character(s), main action, and emotional tone clearly.
- Use a simple, plausible setting that matches the paragraph.
- Make the important action visually unambiguous.
- Include only details supported by the paragraph; do not invent extra events.
- Keep background secondary and uncluttered.
- No text of any kind inside the image.
""".strip()


def build_vocab_prompt(
    word: str,
    example: str,
    *,
    paragraph_context: str = "",
    visual_brief: str = "",
    config: PromptConfig | None = None,
) -> str:
    config = config or PromptConfig()
    return f"""
{config.style}

Illustration purpose: practical vocabulary recognition for a learner with low literacy.
Target concept/word: {word}
Everyday example sentence: {example}
Paragraph context: {paragraph_context}
Additional visual brief: {visual_brief or 'Show one concrete everyday situation that makes the target concept obvious.'}

Vocabulary-card requirements:
- One simple scene and one clear action/emotion.
- The concept must be understandable from the picture without reading.
- Prefer familiar home, school, neighborhood, family, or daily-life situations.
- No written version of the target word and no other text inside the image.
""".strip()
