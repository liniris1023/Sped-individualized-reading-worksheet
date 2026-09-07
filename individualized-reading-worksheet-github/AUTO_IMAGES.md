# 自動情境圖片生成

這個專案可在產生 Word 前，自動為每個段落生成情境圖片。

## 安裝

```bash
pip install -r requirements.txt
```

## 設定 OpenAI API Key

Windows PowerShell：

```powershell
$env:OPENAI_API_KEY="你的_API_Key"
```

macOS / Linux：

```bash
export OPENAI_API_KEY="你的_API_Key"
```

## 一步完成：自動生圖＋產 Word

學生版：

```bash
python generate_word.py sample_3c.json \
  --output output/幸福筆記本_Level3C_學生版.docx \
  --auto-images
```

教師版：

```bash
python generate_word.py sample_3c.json \
  --output output/幸福筆記本_Level3C_教師版.docx \
  --teacher \
  --auto-images
```

Level 3D 會自動生成兩類圖片：

1. 每段閱讀情境圖
2. 每段核心語詞情境圖

## 只預覽會生成哪些圖片

不需要 API Key：

```bash
python generate_images.py sample_3d.json --dry-run
```

會輸出 `sample_3d_image_prompts.json`，可以先檢查每張圖片的提示詞。

## 預設模型與圖片大小

- 模型：`gpt-image-2`
- 段落圖：`1536x1024`
- 核心語詞圖：`1024x1024`
- 品質：`medium`

可調整：

```bash
python generate_word.py sample_3d.json \
  --output output/demo.docx \
  --auto-images \
  --image-quality low
```

## 圖片快取

已生成圖片會存放於：

```text
images/generated/<課名>/<Level>/
```

快取存放於：

```text
images/cache/
```

相同提示詞不會重複付費生成，除非加入：

```bash
--overwrite-images
```

## 圖片風格

系統固定要求：

- 溫暖兒童繪本教育插畫
- 適合臺灣國小特教閱讀教材
- 背景簡潔
- 人物動作與表情清楚
- 柔和色彩
- 低視覺干擾
- 不產生文字、標籤、浮水印

如果某段需要更精準的畫面，可在 JSON 的 section 加入：

```json
"visual_brief": "白髮爸爸走在前面，作者小跑步追上去，兩人走在人行道上"
```

Level 3D 核心語詞也可以加入：

```json
"vocab": {
  "word": "健康",
  "example": "每天運動，可以讓身體更健康。",
  "visual_brief": "精神很好的長輩在公園輕鬆散步"
}
```
