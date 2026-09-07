# 一鍵生成閱讀理解學習單

`build_worksheet.py` 把整個流程串在一起：

**原始課文 → Level 分級/簡化 → 自動出題 → 自動情境圖片 → 學生版 Word → 教師版 Word**

## 1. 安裝

```bash
pip install -r requirements.txt
```

設定 API Key：

```bash
export OPENAI_API_KEY="你的 API Key"
```

Windows PowerShell：

```powershell
$env:OPENAI_API_KEY="你的 API Key"
```

## 2. 最簡單用法

把課文存成 `lesson.txt`：

```bash
python build_worksheet.py lesson.txt --title 幸福筆記本 --grade 5 --level 3C --auto-images
```

會自動建立：

- `generated_specs/幸福筆記本_3C.json`
- `output/幸福筆記本_3C_學生版.docx`
- `output/幸福筆記本_3C_教師版.docx`
- `images/generated/...` 情境圖片

## 3. 一次生成多個 Level

```bash
python build_worksheet.py lesson.txt \
  --title 幸福筆記本 \
  --grade 5 \
  --level 3A \
  --level 3B \
  --level 3C \
  --level 3D \
  --auto-images
```

## 4. 指定學生能力

```bash
python build_worksheet.py lesson.txt \
  --title 幸福筆記本 \
  --grade 5 \
  --level 3C \
  --support 學習障礙 \
  --support 識字困難 \
  --literacy "B｜可辨認常用字與部分課文字" \
  --reading "B｜可讀短句" \
  --writing "B｜低書寫量" \
  --image-support "中圖片支持" \
  --question-count "一般版｜8～10題" \
  --auto-images
```

## 5. 只測 Prompt，不呼叫文字模型

```bash
python build_worksheet.py lesson.txt --title 幸福筆記本 --level 3C --prompt-only
```

會把完整教材生成 prompt 寫進 `generated_specs/`，方便檢查 Skill 規則是否正確。

## 6. 只測 Word 排版

已有 JSON 時：

```bash
python build_worksheet.py --worksheet-json sample_3c.json
```

若要補自動圖片：

```bash
python build_worksheet.py --worksheet-json sample_3c.json --auto-images
```

## 7. 模型設定

文字模型預設由 `OPENAI_TEXT_MODEL` 決定；若未設定，程式目前使用 `gpt-6-astra`。
也可單次指定：

```bash
python build_worksheet.py lesson.txt --level 3C --text-model YOUR_MODEL_ID
```

圖片模型預設：`gpt-image-2`。

## 設計原則

- Level 由老師選擇，不由障別自動判斷。
- 3A 保留原文。
- 3B 約降低 30% 閱讀負荷。
- 3C 約降低 50% 閱讀負荷。
- 3D 約降低 60% 閱讀負荷，並加入每段 1 個核心語詞與實用識字。
- 所有 Level 都有符合課文情境的圖片。
- 錯誤選項必須與文章內容相關，避免一眼即可排除的離題答案。
