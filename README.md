# 🎓 Sistem Akademik Terpadu - Odoo Module

**Custom Odoo 17 Module** untuk mengelola sistem informasi akademik perguruan tinggi, mencakup manajemen mahasiswa, KRS, jadwal kuliah, nilai, hingga proses tesis.

> Dibangun menggunakan **Odoo 17 Community Edition** dengan Python dan XML.


## 👥 Peran & Hak Akses (Roles & Permissions)

Sistem ini memiliki 3 peran utama, masing-masing dengan hak akses yang berbeda:

| Peran | Group ID | Deskripsi |
|-------|----------|-----------|
| 🛠️ **Officer** | `group_akademik_officer` | Admin Akademik - akses penuh semua data |
| 👨‍🏫 **Dosen** | `group_akademik_dosen` | Dosen - Input nilai, klaim jadwal, kelola tesis |
| 🎓 **Mahasiswa** | `group_akademik_student` | Mahasiswa - Lihat KRS, Jadwal, dan Nilai sendiri |

---

## 🗂️ Panduan Penggunaan Per Menu & Per Role

### ────────────────────────────────
### 🛠️ ROLE: OFFICER (Admin Akademik)
### ────────────────────────────────

Officer memiliki akses ke **SELURUH** menu sistem.

#### 📋 Menu: Academic > Student
- Melihat, menambah, dan mengedit data mahasiswa.
- Mengubah Status Mahasiswa (Aktif / Cuti / Lulus).
- Filter mahasiswa berdasarkan Prodi & Angkatan.

#### 📋 Menu: Academic > Lecturers
- Melihat data semua dosen.
- Mengedit data dosen (Prodi Homebase, Jenjang Pendidikan).

#### 📋 Menu: Academic > KRS > KRS List
- Melihat **semua** KRS dari **semua** mahasiswa.
- Filter berdasarkan Semester, Prodi, Angkatan.

#### 📋 Menu: Academic > KRS > Generate KRS (Wizard)
- **Generate KRS Massal**: Pilih Tahun Akademik, Angkatan, Prodi, dan Semester.
- Sistem otomatis mendistribusikan mahasiswa ke kelas berdasarkan kapasitas ruangan.

#### 📋 Menu: Academic > KRS > Subjects
- Mengelola Master Data Mata Kuliah.
- Input Nama MK, SKS, Semester, dan Prodi.

#### 📋 Menu: Academic > KRS > Class Schedules
- Membuat Jadwal Kelas (MK + Ruangan + Hari + Jam).
- Memilih Prodi untuk memfilter Mata Kuliah yang muncul.
- Melihat indikator **Enrolled / Remaining Quota**.

#### 📋 Menu: Academic > Thesis
- Melihat semua data pengajuan tugas akhir.
- Approve / Reject pengajuan tesis mahasiswa.
- Monitor status bimbingan.

#### 📋 Menu: Academic > Dashboard
- **Completion Duration Trend**: Grafik rata-rata lama mahasiswa menyelesaikan skripsi.
- **Student Status Ratio**: Pie chart perbandingan mahasiswa Aktif/Lulus/DO.

#### 📋 Menu: Academic > Configuration
- **Entry Year**: Master tahun akademik.
- **Study Program**: Master Program Studi.
- **Rooms**: Master Ruangan Kuliah + Kapasitas.

---

### ────────────────────────────────
### 👨‍🏫 ROLE: DOSEN
### ────────────────────────────────

#### 📋 Menu: Academic > KRS > Class Schedules
- Melihat daftar jadwal di **Prodi sendiri** saja.
- Klik tombol **"Claim Schedule"** untuk mengambil kelas yang kosong.
- Klik tombol **"Release Schedule"** jika ingin melepas kelas yang sudah diklaim.
- > ⚠️ Tidak bisa mengambil jadwal di luar Prodi sendiri.

#### 📋 Menu: Academic > Thesis
- Melihat daftar mahasiswa yang sedang mengajukan tesis.
- Berperan sebagai **Pembimbing**: Approve / Reject pengajuan.
- Monitor progress bimbingan mahasiswa yang dibimbing.

---

### ────────────────────────────────
### 🎓 ROLE: MAHASISWA
### ────────────────────────────────

#### 📋 Menu: Academic > KRS > KRS List
- Melihat **KRS milik sendiri saja**.
- Tidak bisa melihat KRS mahasiswa lain.
- Melihat detail mata kuliah, jadwal, dan nilai yang sudah diinput dosen.

#### 📋 Menu: Academic > KRS > Class Schedules
- Melihat **semua jadwal kuliah di Prodi sendiri**.
- Bisa melihat informasi kelas: Ruangan, Dosen, Hari, Jam, dan Sisa Kuota.
- Tidak bisa membuat atau mengubah jadwal.

#### 📋 Menu: Academic > Thesis
- Mengajukan judul tugas akhir.
- Memilih Dosen Pembimbing (dari daftar dosen aktif yang tersedia).
- Monitor status pengajuan (Draft / In Progress / Approved / Rejected).

---

## 🔐 Ringkasan Access Control (Security Matrix)

| Fitur | Officer | Dosen | Mahasiswa |
|-------|---------|-------|-----------|
| Kelola Data Mahasiswa | ✅ Full | ❌ | ❌ |
| Lihat Data Dosen | ✅ Full | ✅ Own | ❌ |
| Generate KRS Massal | ✅ | ❌ | ❌ |
| Lihat KRS | ✅ Semua | ❌ | ✅ Sendiri |
| Kelola Mata Kuliah | ✅ | ❌ | ❌ |
| Buat Jadwal Kuliah | ✅ | ❌ | ❌ |
| Klaim Jadwal Kuliah | ❌ | ✅ Prodi Sendiri | ❌ |
| Lihat Jadwal Kuliah | ✅ Semua | ✅ Prodi Sendiri | ✅ Prodi Sendiri |
| Input Nilai | ✅ | ✅ | ❌ |
| Pengajuan Tesis | ❌ | ❌ | ✅ |
| Approve Tesis | ✅ | ✅ (Pembimbing) | ❌ |
| Lihat Dashboard | ✅ | ❌ | ❌ |
| Konfigurasi Master Data | ✅ | ❌ | ❌ |

---

## 🗃️ Struktur Data (ERD Sederhana)

```
res.partner (Mahasiswa)
  ├── study_program_id -> akademik.prodi
  └── entry_year_id   -> akademik.tahun

akademik.krs (KRS Header)
  ├── student_id      -> res.partner
  ├── academic_year_id -> akademik.tahun
  └── line_ids        -> akademik.krs.line

akademik.krs.line (Detail KRS)
  ├── krs_id          -> akademik.krs
  ├── subject_id      -> akademik.subject
  ├── jadwal_id       -> akademik.jadwal
  └── grade           -> (A/B/C/D/E)

akademik.jadwal (Jadwal Kuliah)
  ├── subject_id      -> akademik.subject
  ├── study_program_id -> akademik.prodi
  ├── ruangan_id      -> akademik.ruangan
  └── dosen_id        -> hr.employee

akademik.tesis (Tesis)
  ├── student_id      -> res.partner
  └── supervisor_id   -> hr.employee (Dosen Pembimbing)
```

---

## 🛣️ Roadmap (Coming Soon)

- [ ] Sistem Prasyarat Mata Kuliah
- [ ] Perhitungan IPK & IPS Otomatis
- [ ] Transkrip Nilai (PDF)
- [ ] Presensi Perkuliahan (QR Code)
- [ ] Modul Keuangan (Tagihan SPP)
- [ ] Modul Penggajian Dosen (Custom Payroll)
- [ ] Kalender Akademik Terintegrasi
- [ ] Yudisium & Manajemen Wisudawan

---

## 🧰 Tech Stack

- **Platform**: Odoo 17 Community Edition
- **Language**: Python 3.11, XML (Odoo Views)
- **Database**: PostgreSQL 14
- **ORM**: Odoo ORM (Models, Fields, API)
- **Security**: Record Rules, Access Control Lists (ACL)

---

## 👤 Author

| Field | Info |
|-------|------|
| **Nama** | Hajril Malik|
| **Odoo Version** | 17 Community |
| **Type** | Custom Module (Custom Development) |
