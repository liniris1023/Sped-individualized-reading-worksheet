# GitHub 上架設定建議

## Repository name

推薦：

`sped-individualized-reading-worksheet`

備選：

- `individualized-reading-worksheet`
- `sped-reading-worksheet-generator`
- `taiwan-sped-reading-worksheet`

首選名稱的優點：同時包含 `sped`、`individualized`、`reading`、`worksheet`，用途清楚，也較容易和一般閱讀學習單專案區分。

## Description

建議填入：

`臺灣國小特教個別化閱讀理解學習單生成 Skill｜依閱讀能力分層、自動簡化課文、出題、生成情境圖片與學生／教師版 Word`

較短版本：

`特教個別化閱讀理解學習單生成器：分層課文、閱讀鷹架、情境圖片與 Word 輸出。`

## Website

第一版可先留白。若未來部署教學網站、文件網站或 GitHub Pages，再補上網址。

## Topics

建議加入：

- special-education
- sped
- reading-comprehension
- differentiated-instruction
- worksheet-generator
- education
- elementary-education
- taiwan-education
- chinese-language
- accessibility
- inclusive-education
- ai-education
- python
- docx

GitHub Topics 建議控制在約 8～14 個最相關標籤即可。

## About 區塊建議

Description：使用上方短版 Description。

勾選：

- Releases：之後需要發版本再開
- Packages：目前不需要
- Deployments：目前不需要

## 第一個 commit

推薦：

`feat: initial release of individualized reading worksheet skill`

中文也可使用：

`feat: 建立個別化閱讀理解學習單生成 Skill 初版`

## 建議的第一個 Release

版本：

`v0.1.0`

標題：

`v0.1.0 - First public prototype`

Release 說明重點：

- Level 1～4 閱讀分層架構
- Level 3A／3B／3C／3D 差異化文本規則
- 自動生成段落情境圖片
- Level 3D 實用識字模組
- 學生版／教師版 Word
- 《幸福筆記本》測試案例

## GitHub 首頁建議順序

1. 一句話說明用途
2. 核心特色
3. Level 表格
4. 快速開始
5. Level 3D 實用識字
6. 自動圖片生成
7. 專案結構
8. 使用範例
9. 設計核心
10. License

目前 README 已依此方向整理。

## 建議是否公開

若目前主要目的是自己使用、持續測試，可以先設為 Private。

若希望其他特教老師一起測試，可設為 Public，但發布前應先確認：

- 不含學生姓名、評量資料或其他個資
- examples 使用公開教材時符合著作權使用條件
- API Key 不在任何檔案或 commit history 中
- 選擇並加入 LICENSE（若希望他人可合法修改與再散布）

## 上傳步驟

1. GitHub → New repository
2. Repository name 填入 `sped-individualized-reading-worksheet`
3. 填入 Description
4. 選擇 Public 或 Private
5. 不要勾選自動建立 README（本專案已有 README）
6. 建立 repository
7. 解壓縮 ZIP
8. 將資料夾內容上傳到 repo 根目錄
9. Commit message 使用上方建議
10. 到右側 About → 齒輪 → 加入 Description 與 Topics
