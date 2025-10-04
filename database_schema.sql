-- Database Schema untuk Sistem Irigasi Fuzzy Logic
-- Jalankan script ini untuk membuat database dan tabel yang diperlukan

-- 1. Buat database (jalankan sebagai root atau user dengan privilege CREATE)
CREATE DATABASE IF NOT EXISTS fuzzy_irrigation 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. Gunakan database
USE fuzzy_irrigation;

-- 3. Buat tabel untuk menyimpan hasil perhitungan fuzzy logic
CREATE TABLE IF NOT EXISTS fuzzy_calculations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    kelembaban_input DECIMAL(5,2) NOT NULL COMMENT 'Input kelembaban tanah (%)',
    cuaca_input VARCHAR(50) NOT NULL COMMENT 'Kondisi cuaca (Cerah, Berawan, Hujan Ringan, Hujan Lebat)',
    durasi_output DECIMAL(5,2) NOT NULL COMMENT 'Output durasi irigasi (menit)',
    tingkat_kebutuhan VARCHAR(20) NOT NULL COMMENT 'Tingkat kebutuhan air (Rendah, Sedang, Tinggi)',
    kelembaban_tanah DECIMAL(5,2) COMMENT 'Kelembaban tanah hasil sensor (%)',
    suhu DECIMAL(4,1) COMMENT 'Suhu lingkungan (°C)',
    kelembaban_udara DECIMAL(5,2) COMMENT 'Kelembaban udara (%)',
    curah_hujan DECIMAL(5,2) COMMENT 'Curah hujan (mm)',
    status_pompa VARCHAR(20) COMMENT 'Status pompa (Aktif/Tidak Aktif)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_cuaca (cuaca_input),
    INDEX idx_created_at (created_at),
    INDEX idx_tingkat_kebutuhan (tingkat_kebutuhan)
) ENGINE=InnoDB COMMENT='Tabel untuk menyimpan hasil perhitungan fuzzy logic irigasi';

-- 4. Buat tabel untuk insights dan analisis (opsional)
CREATE TABLE IF NOT EXISTS calculation_insights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL COMMENT 'Jenis insight (weather_analysis, humidity_trend, dll)',
    insight_data JSON COMMENT 'Data insight dalam format JSON',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_insight_type (insight_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='Tabel untuk menyimpan hasil analisis dan insights';

-- 5. Buat user khusus untuk aplikasi (opsional, untuk keamanan)
-- Ganti 'your_password' dengan password yang kuat
-- CREATE USER 'fuzzy_app'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON fuzzy_irrigation.* TO 'fuzzy_app'@'localhost';
-- FLUSH PRIVILEGES;

-- 6. Insert data contoh (opsional)
INSERT INTO fuzzy_calculations 
(kelembaban_input, cuaca_input, durasi_output, tingkat_kebutuhan, kelembaban_tanah, suhu, kelembaban_udara, curah_hujan, status_pompa) 
VALUES 
(25.0, 'Cerah', 40.0, 'Tinggi', 25.0, 32.0, 45.0, 0.0, 'Aktif'),
(45.0, 'Berawan', 25.0, 'Sedang', 45.0, 28.0, 60.0, 2.0, 'Aktif'),
(65.0, 'Hujan Ringan', 10.0, 'Rendah', 65.0, 25.0, 80.0, 15.0, 'Tidak Aktif');

-- Tampilkan struktur tabel
DESCRIBE fuzzy_calculations;
DESCRIBE calculation_insights;

-- Tampilkan data contoh
SELECT * FROM fuzzy_calculations ORDER BY created_at DESC LIMIT 5;