# 個人理財分析終端機 (Web 版)

單一 HTML 檔案的理財分析終端機，改寫自原本的 4 個 Streamlit 頁面：
- 首頁
- 📈 台灣經濟狀況（14 項總體經濟指標、外銷訂單 AI 分析、台經院報告 PDF AI 解讀）
- 🛢️ 原物料與匯率（VIX、原油、貴金屬、農產品、匯率即時報價與走勢圖）
- 💰 台灣股市投資（大盤 K 線、漲跌幅/爆量排行、三大法人籌碼 AI 解析、個股技術面+基本面+AI 研報）

純前端 vanilla JS，資料即時從瀏覽器抓取，不需要後端伺服器。

## 1. 上傳到 GitHub Pages

```bash
# 建立新 repo（或使用現有的）
git init finance-terminal
cd finance-terminal
cp finance_terminal.html index.html
git add index.html
git commit -m "個人理財分析終端機"
git branch -M main
git remote add origin https://github.com/cancri1823/finance-terminal.git
git push -u origin main
```

接著到 GitHub repo 的 **Settings → Pages**，Source 選擇 `main` 分支 `/ (root)`，
存檔後幾分鐘即可透過 `https://cancri1823.github.io/finance-terminal/` 開啟。

## 2. 設定 Gemini API 金鑰（AI 分析功能）

1. 到 https://aistudio.google.com/apikey 免費申請一組金鑰。
2. 開啟網站，點右上角「⚙️ 設定」，貼上金鑰後儲存。
3. 金鑰只存在瀏覽器的 `localStorage`（以及您自己的 Google Drive appdata，若有連線），不會經過任何第三方伺服器。

## 3. 設定 Google Drive 同步（將設定存到雲端硬碟）

因為這是全新的網站網域，需要您自己在 Google Cloud Console 建立一組 OAuth Client ID（和您其他專案 `invest-system` 用的是不同網域，不能共用）：

1. 到 https://console.cloud.google.com/apis/credentials
2. 建立「OAuth 用戶端 ID」，應用程式類型選「網頁應用程式」。
3. 在「已授權的 JavaScript 來源」加入：
   - `https://cancri1823.github.io`
   - （本機測試可加）`http://localhost:5500` 或您用的 Live Server 網址
4. 到「OAuth 同意畫面」新增範圍 `https://www.googleapis.com/auth/drive.appdata`（與您 invest-system 相同的 appdata 範圍，僅存取此 App 自己建立的隱藏資料夾，不會看到您雲端硬碟其他檔案）。
5. 複製產生的 Client ID，貼到網站「⚙️ 設定」的「Google OAuth Client ID」欄位並儲存。
6. 之後點右上角「☁️ Google Drive」即可登入並將設定（目前為 Gemini 金鑰）同步儲存到您的雲端硬碟 `appDataFolder` 中，檔名為 `finance_terminal_settings.json`。

## 4. 技術說明 / 已知限制

- **股市與原物料報價**：透過 Yahoo Finance 的公開 chart / quoteSummary API，經 `corsproxy.io` 代理以繞過瀏覽器 CORS 限制（`corsproxy.io` 為免費公開服務，穩定度可能略遜於付費方案，若常常抓不到資料可自行更換成其他 CORS 代理）。
- **總經指標**：對接國發會、主計總處、財政部的開放資料 CSV，同樣經 CORS 代理讀取並在瀏覽器端解析。GNP、薪資成長率、外銷訂單、M1B、M2 這幾項因原始 Python 版本也未接上實際資料源，維持顯示「未公布」，如需要可以之後再幫您串接對應的公開資料 API。
- **AI 分析**：直接從瀏覽器呼叫 Gemini API（`generativelanguage.googleapis.com`），支援上傳 PDF（用 pdf.js 擷取文字）、Excel/CSV（用 SheetJS 解析）、TXT 檔案，以及貼上文章網址。
- **K 線圖**：使用 Chart.js + chartjs-chart-financial 繪製蠟燭圖（紅漲綠跌，符合台股慣例）。
- 若某支股票同時掛牌上市與上櫃代碼相同，系統會依序嘗試 `.TW`（上市）與 `.TWO`（上櫃）。

## 5. 檔案結構

只有一個檔案 `finance_terminal.html`（改名為 `index.html` 上傳即可），所有 CSS/JS 都內嵌在同一份檔案中，符合單檔 HTML App 的慣例，方便直接部署到 GitHub Pages。
