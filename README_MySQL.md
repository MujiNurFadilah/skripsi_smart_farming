# Setup Database MySQL untuk Sistem Irigasi Fuzzy Logic

## Langkah-langkah Setup Database

### 1. Install MySQL Server
- Download dan install MySQL Server dari [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)
- Atau install menggunakan XAMPP/WAMP yang sudah include MySQL

### 2. Install Python MySQL Connector
```bash
pip install mysql-connector-python==8.2.0
```

### 3. Buat Database dan Tabel

#### Opsi A: Menggunakan MySQL Command Line
```bash
mysql -u root -p
```

Kemudian jalankan script dari file `database_schema.sql`:
```sql
source database_schema.sql
```

#### Opsi B: Menggunakan phpMyAdmin (jika menggunakan XAMPP)
1. Buka phpMyAdmin di browser: `http://localhost/phpmyadmin`
2. Klik tab "SQL"
3. Copy-paste isi file `database_schema.sql`
4. Klik "Go" untuk menjalankan

#### Opsi C: Menggunakan MySQL Workbench
1. Buka MySQL Workbench
2. Connect ke MySQL server
3. Buka file `database_schema.sql`
4. Execute script

### 4. Konfigurasi Koneksi Database

Edit file `app.py` pada bagian inisialisasi database:

```python
db_manager = FuzzyDatabase(
    host="localhost",           # Host MySQL server
    database="fuzzy_irrigation", # Nama database
    user="root",               # Username MySQL Anda
    password="your_password",   # Password MySQL Anda
    port=3306                  # Port MySQL (default: 3306)
)
```

### 5. Struktur Database

#### Tabel `fuzzy_calculations`
Menyimpan hasil perhitungan fuzzy logic dengan kolom:
- `id`: Primary key (AUTO_INCREMENT)
- `timestamp`: Waktu perhitungan
- `kelembaban_input`: Input kelembaban tanah (%)
- `cuaca_input`: Kondisi cuaca
- `durasi_output`: Output durasi irigasi (menit)
- `tingkat_kebutuhan`: Tingkat kebutuhan air
- `kelembaban_tanah`: Kelembaban tanah sensor (%)
- `suhu`: Suhu lingkungan (°C)
- `kelembaban_udara`: Kelembaban udara (%)
- `curah_hujan`: Curah hujan (mm)
- `status_pompa`: Status pompa
- `created_at`: Waktu pembuatan record

#### Tabel `calculation_insights` (Opsional)
Untuk menyimpan hasil analisis dan insights.

### 6. Testing Koneksi

Jalankan aplikasi untuk test koneksi:
```bash
python app.py
```

Jika berhasil, akan muncul pesan:
```
Successfully connected to MySQL database: fuzzy_irrigation
```

### 7. Troubleshooting

#### Error: "Access denied for user"
- Pastikan username dan password MySQL benar
- Pastikan user memiliki privilege untuk database `fuzzy_irrigation`

#### Error: "Can't connect to MySQL server"
- Pastikan MySQL server sudah running
- Periksa host dan port yang digunakan
- Jika menggunakan XAMPP, pastikan MySQL service sudah distart

#### Error: "Unknown database 'fuzzy_irrigation'"
- Pastikan sudah menjalankan script `database_schema.sql`
- Atau buat database manual: `CREATE DATABASE fuzzy_irrigation;`

### 8. Keamanan Database (Opsional)

Untuk production, buat user khusus untuk aplikasi:

```sql
CREATE USER 'fuzzy_app'@'localhost' IDENTIFIED BY 'password_yang_kuat';
GRANT SELECT, INSERT, UPDATE, DELETE ON fuzzy_irrigation.* TO 'fuzzy_app'@'localhost';
FLUSH PRIVILEGES;
```

Kemudian update konfigurasi di `app.py`:
```python
db_manager = FuzzyDatabase(
    host="localhost",
    database="fuzzy_irrigation",
    user="fuzzy_app",
    password="password_yang_kuat",
    port=3306
)
```

### 9. Backup Database

Untuk backup database:
```bash
mysqldump -u root -p fuzzy_irrigation > backup_fuzzy_irrigation.sql
```

Untuk restore:
```bash
mysql -u root -p fuzzy_irrigation < backup_fuzzy_irrigation.sql
```

## Perubahan dari SQLite ke MySQL

### Yang Berubah:
1. **Import**: `sqlite3` → `mysql.connector`
2. **Koneksi**: File path → Host, database, user, password
3. **SQL Syntax**: 
   - `?` placeholder → `%s` placeholder
   - `INTEGER PRIMARY KEY AUTOINCREMENT` → `INT AUTO_INCREMENT PRIMARY KEY`
   - `REAL` → `DECIMAL`
   - `TEXT` → `VARCHAR`
   - `datetime('now', '-7 days')` → `DATE_SUB(NOW(), INTERVAL 7 DAY)`
4. **Cursor**: `cursor.fetchall()` → `cursor.fetchall()` dengan `dictionary=True`
5. **Connection Management**: Persistent connection dengan reconnection handling

### Yang Tetap Sama:
- Struktur tabel dan kolom
- Logika aplikasi
- API endpoints
- Frontend interface

## File yang Dimodifikasi:
- `requirements.txt`: Ditambah `mysql-connector-python`
- `database.py`: Completely rewritten untuk MySQL
- `app.py`: Update inisialisasi database
- `database_schema.sql`: File baru untuk setup database
- `README_MySQL.md`: Dokumentasi setup (file ini)