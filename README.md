# 高鐵訂票小幫手

**!!--純研究用途，請勿用於不當用途--!!**

此程式提供另一種輕便的方式訂購高鐵車票，操作介面為命令列介面。相較於使用網頁訂購，本程式因為省卻了渲染網頁介面的時間，只保留最核心的訂購功能，因此能省下大量等待的時間。

**(2025/05/12 update)** 另有 Rust 版本提供執行檔，可以參考 [thsr-ticket-rs](https://github.com/BreezeWhite/thsr-ticket-rs)

**(2025/06 update [@Ryan Chung](https://github.com/RyanCCJ))** 新增自動填寫表單、自動辨識驗證碼、自動預約訂票排程等功能，詳見下方更新項目

## 執行

本程式由python語言所寫成，因此必須先安裝python才能夠使用。官方下載網址[點這裡](https://www.python.org/downloads/release/python-381/)

### 方法一 （快速）
在已經有安裝好python的環境下，執行以下指令
``` bash
pip install git+https://github.com/BreezeWhite/THSR-Ticket.git

# 執行
thsr-ticket
```

### 方法二
首先先將程式碼下載到本機，執行以下指令或是直接按右上方的下載按鈕

```
git clone https://github.com/BreezeWhite/THSR-Ticket.git
```

再來進入到資料夾中

```
cd thsr_ticket
```

安裝必要的套件

```
python -m pip install -r requirements.txt
```

最後執行程式

```
python thsr_ticket/main.py
```


## 注意事項!!!

本程式依舊有許多尚未完成的部分，僅具備基本訂購的功能，若是僅需要訂購成人票、且無特殊需求者，此程式對您而言是加速訂購流程的方便小工具。不符合以上描述者，目前仍建議使用官方網頁進行訂購。

#### ✅ 已提供功能

- [x] 選擇啟程、到達站
- [x] 選擇出發日期、時間
- [x] 選擇班次
- [x] 選擇**"成人"**票數
- [x] 輸入驗證碼
- [x] 輸入身分證字號
- [x] 輸入手機號碼
- [x] 保留此次輸入紀錄，下次可快速選擇此次紀錄
- [x] 早鳥票預訂【新增】
- [x] TGo 會員購票【新增】
- [x] 自動填入表單資料（讀取設定檔）【新增】
- [x] 自動辨識 reCAPTCHA 驗證碼（使用 EasyOCR）【新增】
- [x] 自動排程訂票【新增】

#### 🛠️ 未提供功能

以下功能為未提供輸入的選項，但程式具備相關功能，可依照自身需求、對程式進行修改

- [ ] 選擇車廂種類(標準/商務)
- [ ] 座位喜好(靠窗/走道)
- [ ] 訂位方式(依時間搜尋車次/直接輸入車次號碼)
- [ ] 輸入孩童/愛心/敬老/學生優惠票數
- [ ] 僅顯示早鳥優惠票

#### 🚧 未完成功能

- [ ] 重新產生認證碼（目前支援手動與 OCR，尚未整合 retry 機制）
- [ ] 語音播放認證碼
- [ ] 重新查詢車次
- [ ] 輸入護照號碼
- [ ] 輸入市話
- [ ] 輸入電子郵件
- [ ] 會員購票

## 實用新功能
### 🧠 自動辨識驗證碼 (OCR)
使用方式如下：

```bash
python thsr_ticket/main.py --OCR
```

OCR 模型採用 [EasyOCR](https://github.com/JaidedAI/EasyOCR)，搭配去除雜訊的前處理流程，是一個效能與辨識能力折衷的方案，目前辨識率約 60%。

### 🕐 自動排程 (Scheduler)

自動排程功能可讓你指定某個時間，自動啟動訂票程序 ~~（俗稱搶票）~~ 。

使用方式：
```bash
python thsr_ticket/scheduler.py
```
根據提示輸入執行時間即可 `(YYY-MM-DD HH:MM:SS)` 。目前預設會讀取 `history.json` 中的第一筆紀錄，並啟用 OCR 模式進行訂票。可以自行在 `scheduler.py` 中修改相關參數。

> [!TIP]
> 如有任何建議或 bug 回報，歡迎提出 Issue 或 PR，一起讓高鐵訂票流程更完善 🚄