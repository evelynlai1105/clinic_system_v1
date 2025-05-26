-- 創建資料庫
CREATE DATABASE IF NOT EXISTS clinic_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE clinic_db;

-- 創建病患資料表
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '病患姓名',
    gender VARCHAR(10) NOT NULL COMMENT '性別',
    birthday DATE NOT NULL COMMENT '生日',
    phone VARCHAR(20) NOT NULL COMMENT '聯絡電話',
    address TEXT NOT NULL COMMENT '聯絡地址',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建醫師資料表
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '醫師姓名',
    department VARCHAR(50) NOT NULL COMMENT '科別',
    specialty VARCHAR(100) NOT NULL COMMENT '專長',
    schedule TEXT NOT NULL COMMENT '排班時段',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建掛號資料表
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL COMMENT '病患ID',
    doctor_id INT NOT NULL COMMENT '醫師ID',
    datetime DATETIME NOT NULL COMMENT '掛號時間',
    complaint TEXT NOT NULL COMMENT '主訴',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '狀態：pending/completed/cancelled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建診斷資料表
CREATE TABLE IF NOT EXISTS diagnoses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL COMMENT '掛號ID',
    diagnosis_text TEXT NOT NULL COMMENT '診斷內容',
    doctor_advice TEXT NOT NULL COMMENT '醫師建議',
    diagnosis_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '診斷時間',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建藥品資料表
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '藥品名稱',
    unit VARCHAR(20) NOT NULL COMMENT '單位',
    stock INT NOT NULL DEFAULT 0 COMMENT '庫存量',
    supplier VARCHAR(100) NOT NULL COMMENT '供應商',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建處方資料表
CREATE TABLE IF NOT EXISTS prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    diagnosis_id INT NOT NULL COMMENT '診斷ID',
    medicine_id INT NOT NULL COMMENT '藥品ID',
    dosage VARCHAR(50) NOT NULL COMMENT '劑量',
    days INT NOT NULL COMMENT '服用天數',
    frequency VARCHAR(50) NOT NULL COMMENT '服用頻率',
    prescribed_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '開立時間',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',
    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建索引
CREATE INDEX idx_patient_name ON patients(name);
CREATE INDEX idx_doctor_name ON doctors(name);
CREATE INDEX idx_appointment_datetime ON appointments(datetime);
CREATE INDEX idx_medicine_name ON medicines(name); 