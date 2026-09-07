"""One-command worksheet builder.

Pipeline:
raw lesson text -> model-generated worksheet JSON -> optional image generation ->
student/teacher DOCX files.

Examples
--------
# Full automatic flow (requires OPENAI_API_KEY)
python build_worksheet.py lesson.txt --title 幸福筆記本 --grade 5 --level 3C --auto-images

# Produce 3B, 3C, 3D in one run
python build_worksheet.py lesson.txt --title 幸福筆記本 --grade 5 --level 3B --level 3C --level 3D --auto-images

# Test the orchestration without a text-model call, using an existing worksheet JSON
python build_worksheet.py --worksheet-json sample_3c.json --auto-images

Environment
-----------
OPENAI_API_KEY     Required for text generation and image generation.
OPENAI_TEXT_MODEL  Optional. Defaults to gpt-6-astra.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from generate_word import generate as generate_docx


LEVEL_INFO = {
    "1": "Level 1｜圖像理解型",
    "2": "Level 2｜關鍵訊息型",
    "3A": "Level 3A｜原文閱讀策略版",
    "3B": "Level 3B｜30%簡化版",
    "3C": "Level 3C｜50%簡化版",
    "3D": "Level 3D｜60%高度簡化＋實用識字版",
    "4": "Level 4｜推論整合型",
}


def normalize_level(value: str) -> str:
    v = value.strip().upper().replace("LEVEL", "").replace("｜", "").strip()
    v = v.replace(" ", "")
    aliases = {
        "1": "1", "L1": "1",
        "2": "2", "L2": "2",
        "3A": "3A", "L3A": "3A",
        "3B": "3B", "L3B": "3B",
        "3C": "3C", "L3C": "3C",
        "3D": "3D", "L3D": "3D",
        "4": "4", "L4": "4",
    }
    if v not in aliases:
        raise ValueError(f"Unsupported level: {value}. Choose from 1, 2, 3A, 3B, 3C, 3D, 4.")
    return aliases[v]


def safe_name(value: str, fallback: str = "worksheet") -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "_", (value or "").strip())
    value = re.sub(r"\s+", "_", value)
    return value[:80] or fallback


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def question_schema_note(level: str) -> str:
    if level in {"3A", "3B"}:
        return "選擇題固定4個選項；錯誤選項必須取自同段的次要訊息、相近因果或部分正確概念。"
    if level == "3C":
        return "選擇題固定3個選項；錯誤選項不可離題，須與同段內容高度相關。"
    if level == "3D":
        return "選擇題以2個選項為主，必要時3個；答案需能藉由短文與圖片直接理解。"
    if level == "2":
        return "選擇題2至3個選項，直接理解為主。"
    if level == "1":
        return "選擇題2個選項，圖像與直接理解為主。"
    return "選擇題4個選項，包含合理且與文本相關的干擾項。"


def level_instructions(level: str) -> str:
    common = """
所有主要段落都要規劃情境圖片。圖片不是裝飾，而是閱讀理解鷹架。
不要在圖片中放任何文字；只需在 JSON 裡提供 visual_brief，之後由圖片生成模組自動生圖。
文章核心人物、主要事件、重要因果、人物感受和全文主旨都要保留。
簡化百分比代表閱讀負荷降低程度，不代表機械式刪除相同比例字數。
""".strip()

    details = {
        "1": """
高度簡化；一句一概念；常用生活語詞；高圖片支持。題型以看圖選答案、二選一、圖文配對、是非與口頭回答為主。
""",
        "2": """
簡化短文；長句拆短；聚焦誰、何時、哪裡、做什麼、為什麼、結果與人物感受。每段至少一張情境圖。
""",
        "3A": """
完整保留原文，不得改寫或刪除原文。可分段、標記關鍵語詞、加入閱讀策略。固定區塊名稱：從課文名稱預測課文內容、念一念課文、重點提問、重點內容填寫、課文內容、整理表格、課文內容小挑戰。訓練找證據、因果、推論與主旨。
""",
        "3B": """
約降低30%閱讀負荷。適度拆長句、刪非必要修飾、生難詞換常用詞，但保留大部分原文細節、因果與推論要求。固定區塊名稱同3A。關鍵語詞每段1至4個，僅做提示。
""",
        "3C": """
約降低50%閱讀負荷。長句拆短、一句一重點、生難詞換常用詞、刪較多次要描述、抽象表達具體化。閱讀理解為主，關鍵語詞每段1至3個，後續在Word以淺灰呈現。固定區塊名稱同3A。不加入「我會說／我會寫」。
""",
        "3D": """
約降低60%閱讀負荷。只保留核心訊息、短句、一句一概念、常用生活詞彙、高圖片支持。每段固定1個核心語詞，須包含：word、bopomofo、example、visual_brief，以及實用識字練習：看圖選詞、圈目標語詞、描一描或寫一次、詞庫填空。不要提供詞義解釋。每段再加1題簡單閱讀理解。不加入事件排序、全文找詞、今天我學會了、大量開放書寫。
""",
        "4": """
原文為主。圖片用於預測、比較和推論；題型涵蓋找證據、跨段整合、人物觀點、推論、主旨與生活應用。
""",
    }
    return common + "\n" + details[level].strip()


def json_contract(level: str) -> str:
    vocab = ""
    if level == "3D":
        vocab = '''
      "vocab": {
        "word": "核心語詞",
        "bopomofo": "臺灣注音",
        "example": "生活化例句",
        "visual_brief": "可直接看懂核心語詞的生活情境圖描述",
        "exercises": [ question, question, question, question ]
      },'''

    return f'''
只輸出一個合法 JSON object，不要 Markdown code fence，不要額外說明。Schema：
{{
  "title": "課文名稱",
  "level": "{LEVEL_INFO[level]}",
  "prediction": {{
    "type": "choice",
    "prompt": "從課文名稱預測課文內容的題目",
    "choices": ["..."],
    "answer": 0,
    "visual_brief": "主題預測情境圖，提供3至5個同主題視覺線索"
  }},
  "sections": [
    {{
      "title": "段落主題",
      "text": ["第一句", "第二句"],
      "visual_brief": "這段情境圖片應呈現的人物、動作、情緒與場景",
      "keywords": ["關鍵語詞"],{vocab}
      "questions": [question],
      "fills": [question],
      "content_questions": [question]
    }}
  ],
  "summary_table": {{
    "headers": ["欄位1", "欄位2"],
    "rows": [["內容", "________"]],
    "answers": [["", "教師答案"]]
  }},
  "challenge": [question]
}}

question可為：
1. 選擇題：{{"type":"choice","prompt":"題目","choices":["A","B"],"answer":0}}
2. 填空題：{{"type":"fill","prompt":"題目","line":"________________","word_bank":["詞1","詞2"],"answer_text":"答案"}}
3. 短答題：{{"type":"short","prompt":"題目","lines":2,"answer_text":"參考答案"}}

不要輸出 image 欄位；圖片路徑由後續程式自動寫入。
'''.strip()


def build_model_prompt(*, title: str, article: str, grade: str, level: str,
                       supports: list[str], literacy: str, reading: str,
                       writing: str, image_support: str, question_count: str) -> str:
    return f"""
你是臺灣國小特殊教育閱讀教材設計專家。請依學生實際能力，將下列原始課文轉成個別化閱讀理解學習單 JSON。

【基本設定】
課名：{title}
年級：國小{grade}年級
閱讀Level：{LEVEL_INFO[level]}
支持需求：{'、'.join(supports) if supports else '未特別指定'}
識字能力：{literacy}
朗讀能力：{reading}
書寫能力：{writing}
圖片支持：{image_support}
題量：{question_count}

【Level規則】
{level_instructions(level)}

【選擇題規則】
{question_schema_note(level)}
所有錯誤選項都必須與課文同段或全文內容相關，不使用荒謬、明顯離題或不讀文章即可排除的答案。選項長度盡量接近。

【教學與版面規則】
- 使用繁體中文與臺灣用語。
- 每段都需提供 visual_brief 供自動情境圖片生成。
- Level 3A/3B/3C 的 keywords 必須只是閱讀提示；不要把答案直接塞進關鍵語詞。
- Level 3D 每段固定1個實用核心語詞，情境圖需能讓低識字學生直接理解該詞。
- 題目應從直接理解逐步到因果、感受、證據、推論或主旨；低Level不必包含全部層次。
- 教師答案寫在 answer、answer_text 或 summary_table.answers 中。

【原始課文】
{article}

【輸出契約】
{json_contract(level)}
""".strip()


def create_worksheet_json(prompt: str, model: str) -> dict[str, Any]:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for automatic worksheet generation.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the OpenAI Python SDK: pip install openai") from exc
    client = OpenAI()
    response = client.responses.create(
        model=model,
        instructions="Return only valid JSON matching the user's schema. Do not use markdown fences.",
        input=prompt,
    )
    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise RuntimeError("Text model returned no output_text.")
    return extract_json(output_text)


def ensure_metadata(data: dict[str, Any], *, title: str | None = None, level: str | None = None) -> dict[str, Any]:
    if title:
        data["title"] = title
    if level:
        data["level"] = LEVEL_INFO[level]
    return data


def generate_images_in_memory(data: dict[str, Any], *, image_dir: Path, cache_dir: Path,
                              model: str, quality: str, overwrite: bool) -> None:
    from generate_images import OpenAIImageGenerator, cached_generate, plan_images
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required when --auto-images is enabled.")
    generator = OpenAIImageGenerator(model)
    jobs = plan_images(data, image_dir)
    for n, job in enumerate(jobs, 1):
        path = cached_generate(
            generator,
            job["prompt"],
            job["path"],
            cache_dir=cache_dir,
            size=job["size"],
            quality=quality,
            overwrite=overwrite,
        )
        target, key = job["target"]
        target[key] = str(path.resolve())
        print(f"  [image {n}/{len(jobs)}] {path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build individualized reading worksheets from raw text in one command.")
    p.add_argument("article_file", nargs="?", type=Path, help="UTF-8 text/Markdown file containing the original article.")
    p.add_argument("--worksheet-json", type=Path, help="Bypass text generation and use an existing worksheet JSON (testing mode).")
    p.add_argument("--title", help="Lesson title. If omitted, uses the first non-empty line of the article file.")
    p.add_argument("--grade", default="5", choices=[str(i) for i in range(1, 7)])
    p.add_argument("--level", action="append", help="Repeatable: 1, 2, 3A, 3B, 3C, 3D, 4. Default: 3C")
    p.add_argument("--support", action="append", default=[], help="Repeatable support need, e.g. 學習障礙 / 識字困難 / ADHD")
    p.add_argument("--literacy", default="C｜可認讀大部分課文字詞")
    p.add_argument("--reading", default="C｜可讀短段落")
    p.add_argument("--writing", default="C｜可短答或完成短句")
    p.add_argument("--image-support", default="中圖片支持")
    p.add_argument("--question-count", default="一般版｜8～10題")
    p.add_argument("--text-model", default=os.getenv("OPENAI_TEXT_MODEL", "gpt-6-astra"))
    p.add_argument("--auto-images", action="store_true")
    p.add_argument("--image-model", default="gpt-image-2")
    p.add_argument("--image-quality", choices=["low", "medium", "high"], default="medium")
    p.add_argument("--overwrite-images", action="store_true")
    p.add_argument("--output-dir", type=Path, default=Path("output"))
    p.add_argument("--spec-dir", type=Path, default=Path("generated_specs"))
    p.add_argument("--image-dir", type=Path, default=Path("images/generated"))
    p.add_argument("--image-cache-dir", type=Path, default=Path("images/cache"))
    p.add_argument("--student-only", action="store_true")
    p.add_argument("--teacher-only", action="store_true")
    p.add_argument("--prompt-only", action="store_true", help="Write model prompts but do not call the text model.")
    return p.parse_args()


def read_article(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8").strip()


def infer_title(article: str) -> str:
    for line in article.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean:
            return clean[:80]
    return "閱讀理解學習單"


def main() -> int:
    args = parse_args()
    if not args.article_file and not args.worksheet_json:
        print("ERROR: provide article_file or --worksheet-json.", file=sys.stderr)
        return 2
    if args.student_only and args.teacher_only:
        print("ERROR: --student-only and --teacher-only cannot both be used.", file=sys.stderr)
        return 2

    levels = [normalize_level(x) for x in (args.level or ["3C"])]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.spec_dir.mkdir(parents=True, exist_ok=True)

    # Testing mode: existing worksheet JSON is rendered as-is.
    if args.worksheet_json:
        data = json.loads(args.worksheet_json.read_text(encoding="utf-8"))
        raw_level = data.get("level", "")
        detected = next((k for k in LEVEL_INFO if f"Level {k}" in raw_level), levels[0])
        title = data.get("title", args.title or "閱讀理解學習單")
        batches = [(detected, data)]
    else:
        article = read_article(args.article_file)
        title = args.title or infer_title(article)
        batches = []
        for level in levels:
            print(f"[text] Building {LEVEL_INFO[level]} ...")
            prompt = build_model_prompt(
                title=title,
                article=article,
                grade=args.grade,
                level=level,
                supports=args.support,
                literacy=args.literacy,
                reading=args.reading,
                writing=args.writing,
                image_support=args.image_support,
                question_count=args.question_count,
            )
            prompt_path = args.spec_dir / f"{safe_name(title)}_{level}_prompt.txt"
            prompt_path.write_text(prompt, encoding="utf-8")
            if args.prompt_only:
                print(f"  prompt: {prompt_path}")
                continue
            data = create_worksheet_json(prompt, args.text_model)
            ensure_metadata(data, title=title, level=level)
            batches.append((level, data))

        if args.prompt_only:
            return 0

    created: list[Path] = []
    for level, data in batches:
        tag = safe_name(f"{title}_{level}")
        if args.auto_images:
            print(f"[images] {LEVEL_INFO[level]}")
            generate_images_in_memory(
                data,
                image_dir=args.image_dir,
                cache_dir=args.image_cache_dir,
                model=args.image_model,
                quality=args.image_quality,
                overwrite=args.overwrite_images,
            )

        spec_path = args.spec_dir / f"{tag}.json"
        spec_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[spec] {spec_path}")

        if not args.teacher_only:
            student_path = args.output_dir / f"{tag}_學生版.docx"
            out = Path(generate_docx(data, str(student_path), teacher=False))
            created.append(out)
            print(f"[docx] {out}")
        if not args.student_only:
            teacher_path = args.output_dir / f"{tag}_教師版.docx"
            out = Path(generate_docx(data, str(teacher_path), teacher=True))
            created.append(out)
            print(f"[docx] {out}")

    print("\nCompleted:")
    for pth in created:
        print(f"- {pth}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
