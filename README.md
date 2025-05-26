# 診所醫療資訊系統

這是一個基於 Flask 的診所醫療資訊系統，提供病患管理、醫師管理、掛號管理和藥品管理等功能。

## 功能特點

- 病患資料管理
- 醫師資料與排班管理
- 掛號與看診管理
- 藥品庫存管理
- 診斷與處方管理

## 系統需求

- Python 3.8 或以上版本
- Flask 3.0.2
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Flask-WTF 1.2.1
- SQLAlchemy 2.0.28

## 安裝步驟

1. 克隆專案：
```bash
git clone [專案網址]
cd clinic
```

2. 建立虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安裝依賴：
```bash
pip install -r requirements.txt
```

4. 初始化資料庫：
```bash
flask db init
flask db migrate
flask db upgrade
```

5. 執行應用程式：
```bash
python app.py
```

## 使用說明

1. 開啟瀏覽器訪問 http://localhost:5000
2. 使用系統提供的功能進行操作：
   - 病患管理：新增、編輯、刪除病患資料
   - 醫師管理：管理醫師資料與排班
   - 掛號管理：處理病患掛號與看診
   - 藥品管理：管理藥品庫存與處方

## 資料庫結構

系統使用 SQLite 資料庫，主要包含以下資料表：
- Patients（病患資料）
- Doctors（醫師資料）
- Appointments（掛號紀錄）
- Diagnoses（診斷紀錄）
- Prescriptions（處方紀錄）
- Medicines（藥品資料）

## 開發者

[您的名字]

## 授權

本專案採用 MIT 授權條款 