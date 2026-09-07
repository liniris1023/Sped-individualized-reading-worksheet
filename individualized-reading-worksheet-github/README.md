# 個別化閱讀理解學習單生成器

**Individualized Reading Worksheet Generator**

專為臺灣國小特教、資源班與差異化閱讀教學設計的 Agent Skill。老師提供課文或閱讀文章後，可依學生的閱讀、識字、朗讀與書寫能力，產出不同層級的閱讀理解學習單，並自動規劃情境圖片、學生版與教師解答版 Word。

## ✨ 核心特色

- **能力導向分層**：支援 Level 1、2、3A、3B、3C、3D、4，不直接用障別決定難度。
- **Level 3 四階差異化**：
  - **3A**：完整保留原文，強化找證據、推論與主旨。
  - **3B**：約降低 30% 閱讀負荷，保留較高理解要求。
  - **3C**：約降低 50% 閱讀負荷，強化重點理解與明確鷹架。
  - **3D**：約降低 60% 閱讀負荷，加入高圖片支持與實用識字訓練。
- **自動情境圖片**：依段落內容建立圖片 prompt，可自動生成並插入 Word。
- **實用識字整合**：Level 3D 每段固定 1 個核心語詞，搭配情境圖、臺灣注音、生活例句與低書寫量練習。
- **特教友善題型**：選項數、書寫量、提示程度與圖片密度會依學生能力調整。
- **合理干擾選項**：錯誤選項優先取自課文人物、事件、感受或近似概念，避免一眼就能排除的離題答案。
- **雙版本輸出**：可產生學生版與教師解答版 Word。

## 🧭 閱讀 Level

| Level | 文本處理 | 主要學習需求 |
|---|---|---|
| **1 圖像理解型** | 高度簡化 | 低識字、報讀、高圖片支持 |
| **2 關鍵訊息型** | 簡化短文 | 六何法、直接理解、基本因果 |
| **3A 原文閱讀策略版** | 原文 100% 保留 | 找重點、找證據、推論、主旨 |
| **3B 30% 簡化版** | 輕度簡化 | 識字尚可、閱讀理解較弱 |
| **3C 50% 簡化版** | 中度簡化 | 識字率較低、朗讀慢、長句困難 |
| **3D 60% 高度簡化版** | 高度簡化＋實用識字 | 低認知、低識字、高圖片支持 |
| **4 推論整合型** | 原文為主 | 跨段整合、證據、主旨與高層推論 |

> 簡化百分比代表「閱讀負荷調整強度」，不是機械式刪除固定比例字數。

## 🖼️ 圖片設計原則

所有 Level 都可搭配符合課文內容的情境圖片。圖片是閱讀鷹架，不是裝飾。

圖片設計以以下原則為主：

- 人物、動作與情緒清楚
- 背景簡潔、低視覺干擾
- 溫暖兒童繪本／教育插畫風格
- 適合國小特殊需求學生理解
- 不加入多餘文字與浮水印

Level 3D 另外可為每段的核心語詞產生獨立情境圖。

## 📄 Level 3A～3C 固定學習單架構

1. **從課文名稱預測課文內容**
2. **念一念課文**
3. **重點提問**
4. **重點內容填寫**
5. **課文內容**
6. **整理表格**
7. **課文內容小挑戰**

Level 3A、3B、3C 使用相同學習流程，主要差異在文本難度、提示量、題目深度與作答方式。

### 關鍵語詞

Level 3A～3C 的關鍵語詞採低干擾提示：

- 淺灰字
- 字級略小於正文
- 不使用鮮豔底色與粗框
- 置於段落下方

## 🔤 Level 3D 實用識字模組

每一段固定包含：

1. 段落情境圖片
2. 高度簡化短文
3. 核心語詞情境圖片
4. 核心語詞＋臺灣注音
5. 生活例句
6. 看圖選詞
7. 圈出核心語詞
8. 描一描／寫一次
9. 詞庫完成句子
10. 簡單閱讀理解題

核心語詞不放詞典式解釋，以「情境圖＋生活例句」建立理解與實用識字連結。

## 🎯 選擇題設計

干擾選項必須與課文內容相關，優先使用：

- 課文中真正出現的次要事件
- 部分正確但不完整的訊息
- 容易混淆的人物感受
- 容易混淆的因果關係
- 與正確答案相近但範圍不同的概念

建議選項數：

- Level 1：2 個
- Level 2：2～3 個
- Level 3C：3 個
- Level 3B：4 個
- Level 3A：4 個
- Level 4：4 個

## 🚀 快速開始

### 1. 安裝

建議使用 Python 3.10+。

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

Linux / macOS：

```bash
export OPENAI_API_KEY="your_key"
```

Windows PowerShell：

```powershell
$env:OPENAI_API_KEY="your_key"
```

### 3. 準備課文

將原始課文儲存為 UTF-8 `.txt` 或 `.md`，例如：

```text
幸福筆記本

在我的床頭有一本「幸福筆記本」……
```

### 4. 一鍵生成 Level 3C

```bash
python build_worksheet.py lesson.txt \
  --title 幸福筆記本 \
  --grade 5 \
  --level 3C \
  --support 學習障礙 \
  --literacy C \
  --reading C \
  --writing C \
  --image-support medium \
  --question-count normal \
  --auto-images
```

程式會串接：

**原始課文 → 分層教材內容 → 題目 → 情境圖片 → 學生版 Word → 教師版 Word**

### 5. 一次產生多個 Level

`--level` 可重複使用：

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

## 🧪 不呼叫文字模型的測試模式

若已有 worksheet JSON，可直接測試 Word 與圖片流程：

```bash
python build_worksheet.py \
  --worksheet-json examples/幸福筆記本/sample_3c.json \
  --auto-images
```

也可以使用：

```bash
python build_worksheet.py lesson.txt --prompt-only
```

只輸出模型 prompt，不實際呼叫文字模型，方便檢查與除錯。

## ⚙️ 常用參數

```text
--grade 1..6
--level 1|2|3A|3B|3C|3D|4
--support <支持需求>        可重複
--literacy <識字能力>
--reading <朗讀能力>
--writing <書寫能力>
--image-support <圖片支持程度>
--question-count <題量>
--auto-images
--image-quality low|medium|high
--student-only
--teacher-only
--prompt-only
```

完整參數：

```bash
python build_worksheet.py --help
```

## 📁 專案結構

```text
individualized-reading-worksheet/
├── SKILL.md
├── README.md
├── build_worksheet.py
├── generate_word.py
├── generate_images.py
├── image_prompt_builder.py
├── requirements.txt
├── ONE_CLICK.md
├── AUTO_IMAGES.md
├── templates/
│   ├── level1.md
│   ├── level2.md
│   ├── level3a.md
│   ├── level3b.md
│   ├── level3c.md
│   ├── level3d.md
│   └── level4.md
├── examples/
├── images/
│   ├── generated/
│   └── cache/
└── output/
```

## 👩‍🏫 教師版

教師版除答案外，可包含：

- 可接受答案
- 每題評量能力
- 教學目標
- 口頭提示
- 學生常見錯誤
- 再降低難度的方法
- 再提高難度的方法

## 🧩 設計核心

> **閱讀能力決定難度。**  
> **障別與支持需求決定鷹架。**  
> **書寫能力決定回答方式。**  
> **圖片不是裝飾，而是閱讀理解工具。**

## 📚 更多說明

- `SKILL.md`：完整 Agent Skill 規格與分層規則
- `ONE_CLICK.md`：一鍵生成流程
- `AUTO_IMAGES.md`：自動情境圖片生成說明

## License

本專案目前尚未指定開源授權。若要公開供他人下載、修改或再散布，建議在正式發布前選擇合適的 LICENSE。
