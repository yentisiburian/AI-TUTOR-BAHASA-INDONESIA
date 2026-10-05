import streamlit as st
import os
import re
import json
import pandas as pd
from collections import Counter

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia",
    page_icon="📚",
    layout="wide"
)

# =========================================================
# FOLDER & FILE PENYIMPANAN DATA
# =========================================================

FOLDER_DATABASE = "database"
FILE_KUIS = "data_kuis.json"
FILE_MEDIA = "data_media.json"
FILE_NILAI = "data_nilai.json"

if not os.path.exists(FOLDER_DATABASE):
    os.makedirs(FOLDER_DATABASE)

def load_json(filepath, default_value):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_value
    return default_value

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Load data kuis, media, dan nilai
data_kuis = load_json(FILE_KUIS, [])
data_media = load_json(FILE_MEDIA, [])
data_nilai = load_json(FILE_NILAI, [])

# =========================================================
# FUNGSI MANAJEMEN DATABASE TXT
# =========================================================

def baca_database():
    data = []
    daftar_file = os.listdir(FOLDER_DATABASE)
    for nama_file in daftar_file:
        if nama_file.lower().endswith(".txt"):
            lokasi_file = os.path.join(FOLDER_DATABASE, nama_file)
            try:
                with open(lokasi_file, "r", encoding="utf-8") as file:
                    isi = file.read()
                data.append({"nama_file": nama_file, "isi": isi})
            except Exception as error:
                st.error(f"Gagal membaca {nama_file}: {error}")
    return data

def bersihkan_teks(teks):
    teks = teks.lower()
    teks = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", teks)
    teks = re.sub(r"\s+", " ", teks)
    return teks.strip()

STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "pada", "dengan", "untuk", "dalam", 
    "adalah", "itu", "ini", "atau", "apa", "bagaimana", "mengapa", "sebutkan", 
    "jelaskan", "jelaskanlah", "tentang", "suatu", "sebuah", "secara", "merupakan", 
    "dapat", "akan", "sebagai", "oleh", "lebih", "juga", "tidak", "tersebut"
}

def ambil_kata_kunci(pertanyaan):
    teks = bersihkan_teks(pertanyaan)
    kata = teks.split()
    return [item for item in kata if len(item) > 2 and item not in STOPWORDS]

def hitung_relevansi(pertanyaan, isi):
    kata_kunci = ambil_kata_kunci(pertanyaan)
    if not kata_kunci:
        return 0
    teks_database = bersihkan_teks(isi)
    frekuensi = Counter(teks_database.split())
    skor = sum(min(frekuensi[kata], 10) for kata in kata_kunci if kata in frekuensi)
    
    if bersihkan_teks(pertanyaan) in teks_database:
        skor += 20
        
    baris_awal = teks_database[:500]
    for kata in kata_kunci:
        if kata in baris_awal:
            skor += 5
    return skor

def cari_materi(pertanyaan, database):
    hasil = []
    for data in database:
        skor = hitung_relevansi(pertanyaan, data["isi"])
        if skor > 0:
            hasil.append({"nama_file": data["nama_file"], "isi": data["isi"], "skor": skor})
    hasil.sort(key=lambda x: x["skor"], reverse=True)
    return hasil

def ambil_potongan_relevan(pertanyaan, isi, jumlah_maksimal=1200):
    kata_kunci = ambil_kata_kunci(pertanyaan)
    paragraf = re.split(r"\n\s*\n|\r\n", isi)
    paragraf_relevan = []
    
    for p in paragraf:
        p_bersih = bersihkan_teks(p)
        skor = sum(1 for kata in kata_kunci if kata in p_bersih)
        if skor > 0:
            paragraf_relevan.append((skor, p.strip()))
            
    paragraf_relevan.sort(key=lambda x: x[0], reverse=True)
    
    hasil = ""
    for skor, p in paragraf_relevan:
        if len(hasil) + len(p) <= jumlah_maksimal:
            hasil += p + "\n\n"
            
    return hasil.strip() if hasil.strip() else isi[:jumlah_maksimal]

database = baca_database()

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.title("📚 AI Tutor Bahasa Indonesia")
    
    st.subheader("Pilih Panel Akses:")
    panel_akses = st.radio(
        "",
        ["🎓 PANEL SISWA", "👨‍🏫 PANEL GURU"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if panel_akses == "🎓 PANEL SISWA":
        st.subheader("Menu Navigasi")
        menu = st.radio(
            "",
            [
                "🏠 Beranda Siswa",
                "📖 Lihat Materi",
                "💬 Tanya AI Tutor",
                "📝 Kerjakan Kuis Pilihan Ganda",
                "🎬 Media Pembelajaran"
            ],
            label_visibility="collapsed"
        )
    else:
        st.subheader("Menu Navigasi Guru")
        menu = st.radio(
            "",
            [
                "🏠 Beranda Guru",
                "📂 Kelola Database Materi",
                "📝 Kelola Bank Soal Kuis",
                "🎬 Kelola Media Pembelajaran",
                "📊 Rekap Nilai Siswa"
            ],
            label_visibility="collapsed"
        )

# =========================================================
# PANEL SISWA
# =========================================================

if panel_akses == "🎓 PANEL SISWA":
    
    if menu == "🏠 Beranda Siswa":
        st.title("👋 Selamat Datang di Panel Siswa")
        st.write("Aplikasi AI Tutor Bahasa Indonesia siap membantu proses belajar Anda secara mandiri dan interaktif.")
        
        st.info(
            "Gunakan menu di sebelah kiri untuk melihat materi, bertanya kepada AI, "
            "mengerjakan kuis pilihan ganda tanpa batas, atau mengakses media pembelajaran."
        )

    elif menu == "📖 Lihat Materi":
        st.title("📖 Daftar Materi Pembelajaran")
        if len(database) > 0:
            for data in database:
                nama = data["nama_file"].replace(".txt", "").replace("_", " ").title()
                with st.expander(f"📄 {nama}"):
                    st.write(data["isi"])
        else:
            st.warning("Belum ada materi di folder database. Minta guru untuk menambahkannya.")

    elif menu == "💬 Tanya AI Tutor":
        st.title("💬 Tanya AI Tutor")
        st.write("Sistem pencarian dan pemahaman materi otomatis berbasis database TXT.")
        
        pertanyaan = st.text_area(
            "Masukkan pertanyaan Anda:",
            placeholder="Contoh: Apa yang dimaksud dengan kalimat efektif?",
            height=120
        )
        
        if st.button("🔍 TANYAKAN", use_container_width=True):
            if not pertanyaan.strip():
                st.warning("Silakan masukkan pertanyaan terlebih dahulu.")
            elif not database:
                st.error("Database TXT belum ditemukan.")
            else:
                with st.spinner("Sedang mencari materi..."):
                    hasil = cari_materi(pertanyaan, database)
                    
                if hasil:
                    hasil_utama = hasil[0]
                    st.success("Materi yang paling relevan ditemukan.")
                    st.subheader("💡 Jawaban")
                    jawaban = ambil_potongan_relevan(pertanyaan, hasil_utama["isi"])
                    st.info(jawaban)
                    
                    st.subheader("📚 Sumber Materi")
                    st.write(f"**{hasil_utama['nama_file']}**")
                    
                    if len(hasil) > 1:
                        st.subheader("📑 Materi Terkait")
                        for item in hasil[1:4]:
                            with st.expander(item["nama_file"]):
                                st.write(ambil_potongan_relevan(pertanyaan, item["isi"], 800))
                else:
                    st.warning("Maaf, materi yang Anda tanyakan belum ditemukan dalam database.")

    elif menu == "📝 Kerjakan Kuis Pilihan Ganda":
        st.title("📝 Kuis Pilihan Ganda Interaktif")
        
        if not data_kuis:
            st.warning("Belum ada soal kuis yang tersedia. Tunggu guru menambahkan soal.")
        else:
            nama_siswa = st.text_input("Masukkan Nama Anda sebelum memulai:")
            
            if nama_siswa.strip():
                st.divider()
                with st.form("form_kuis"):
                    jawaban_user = {}
                    for idx, item in enumerate(data_kuis):
                        st.write(f"**Soal {idx+1}: {item['soal']}**")
                        jawaban_user[idx] = st.radio(
                            "Pilih jawaban:",
                            item["opsi"],
                            key=f"soal_{idx}",
                            index=0
                        )
                        st.write("---")
                    
                    submit_kuis = st.form_submit_button("🚀 Kirim Jawaban", use_container_width=True)
                    
                    if submit_kuis:
                        benar = 0
                        total = len(data_kuis)
                        for idx, item in enumerate(data_kuis):
                            pilihan = jawaban_user[idx]
                            jawaban_benar = item["opsi"][item["kunci"]]
                            if pilihan == jawaban_benar:
                                benar += 1
                        
                        nilai = round((benar / total) * 100, 2)
                        st.balloons()
                        st.success(f"Kuis Selesai! Skor Anda: **{nilai} / 100** (Benar {benar} dari {total} soal)")
                        
                        # Simpan Nilai
                        data_nilai.append({
                            "nama": nama_siswa.strip(),
                            "nilai": nilai,
                            "benar": benar,
                            "total": total
                        })
                        save_json(FILE_NILAI, data_nilai)
                        st.info("Nilai Anda telah tersimpan di rekap nilai guru.")

    elif menu == "🎬 Media Pembelajaran":
        st.title("🎬 Media Pembelajaran")
        if not data_media:
            st.warning("Belum ada media pembelajaran yang diunggah.")
        else:
            for item in data_media:
                st.subheader(f"📌 {item['judul']}")
                st.caption(item['deskripsi'])
                
                if "youtube.com" in item['url'] or "youtu.be" in item['url']:
                    st.video(item['url'])
                else:
                    st.markdown(f"🔗 [Buka Tautan Pembelajaran]({item['url']})")
                st.divider()

# =========================================================
# PANEL GURU
# =========================================================

else:
    st.title("👨‍🏫 Panel Manajemen Guru")
    
    if menu == "🏠 Beranda Guru":
        st.write("Selamat datang di **Panel Manajemen Pembelajaran Guru**.")
        st.info("Di panel ini Anda dapat mengelola database materi teks (`.txt`), membuat soal kuis, menambahkan link media pembelajaran, dan memantau rekap nilai siswa.")

    elif menu == "📂 Kelola Database Materi":
        st.subheader("📂 Kelola File Teks Materi (.txt)")
        
        # Upload Teks
        with st.expander("➕ Tambah File Materi Baru (.txt)"):
            uploaded_file = st.file_uploader("Pilih file TXT dari komputer Anda", type=["txt"])
            if uploaded_file is not None:
                content = uploaded_file.read().decode("utf-8")
                path = os.path.join(FOLDER_DATABASE, uploaded_file.name)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                st.success(f"File **{uploaded_file.name}** berhasil disimpan!")
                st.rerun()

        st.divider()
        st.write("### Daftar Materi Tersimpan:")
        files = os.listdir(FOLDER_DATABASE)
        txt_files = [f for f in files if f.endswith(".txt")]
        
        if txt_files:
            for f in txt_files:
                col1, col2 = st.columns([4, 1])
                col1.write(f"📄 **{f}**")
                if col2.button("🗑️ Hapus", key=f"del_{f}"):
                    os.remove(os.path.join(FOLDER_DATABASE, f))
                    st.success(f"File {f} terhapus!")
                    st.rerun()
        else:
            st.warning("Belum ada file TXT di folder database.")

    elif menu == "📝 Kelola Bank Soal Kuis":
        st.subheader("📝 Kelola Bank Soal Kuis Pilihan Ganda")
        
        with st.form("form_tambah_soal"):
            soal = st.text_area("Masukkan Pertanyaan / Soal:")
            opsi_a = st.text_input("Opsi A:")
            opsi_b = st.text_input("Opsi B:")
            opsi_c = st.text_input("Opsi C:")
            opsi_d = st.text_input("Opsi D:")
            kunci_jawaban = st.selectbox("Kunci Jawaban Benar:", ["Opsi A", "Opsi B", "Opsi C", "Opsi D"])
            
            simpan_soal = st.form_submit_button("💾 Simpan Soal")
            if simpan_soal:
                if soal and opsi_a and opsi_b and opsi_c and opsi_d:
                    kunci_idx = {"Opsi A": 0, "Opsi B": 1, "Opsi C": 2, "Opsi D": 3}[kunci_jawaban]
                    soal_baru = {
                        "soal": soal,
                        "opsi": [opsi_a, opsi_b, opsi_c, opsi_d],
                        "kunci": kunci_idx
                    }
                    data_kuis.append(soal_baru)
                    save_json(FILE_KUIS, data_kuis)
                    st.success("Soal berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Semua field wajib diisi!")

        st.divider()
        st.write("### Daftar Soal Kuis Saat Ini:")
        if data_kuis:
            for idx, item in enumerate(data_kuis):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"**{idx+1}. {item['soal']}**")
                    for i, op in enumerate(item['opsi']):
                        kategori = " (Kunci Jawaban)" if i == item['kunci'] else ""
                        st.write(f" - {chr(65+i)}. {op}{kategori}")
                with col2:
                    if st.button("🗑️ Hapus", key=f"del_soal_{idx}"):
                        data_kuis.pop(idx)
                        save_json(FILE_KUIS, data_kuis)
                        st.rerun()
                st.write("---")
        else:
            st.info("Belum ada soal kuis tersimpan.")

    elif menu == "🎬 Kelola Media Pembelajaran":
        st.subheader("🎬 Kelola Link Media Pembelajaran")
        
        with st.form("form_media"):
            judul_media = st.text_input("Judul Media Pembelajaran:")
            url_media = st.text_input("Link / URL (YouTube atau web):")
            deskripsi_media = st.text_area("Deskripsi Singkat:")
            
            simpan_media = st.form_submit_button("💾 Tambahkan Media")
            if simpan_media:
                if judul_media and url_media:
                    data_media.append({
                        "judul": judul_media,
                        "url": url_media,
                        "deskripsi": deskripsi_media
                    })
                    save_json(FILE_MEDIA, data_media)
                    st.success("Media pembelajaran berhasil disimpan!")
                    st.rerun()
                else:
                    st.error("Judul dan URL tidak boleh kosong!")

        st.divider()
        st.write("### Daftar Media Pembelajaran:")
        if data_media:
            for idx, m in enumerate(data_media):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"**{m['judul']}** - [Link]({m['url']})")
                    st.caption(m['deskripsi'])
                with col2:
                    if st.button("🗑️ Hapus", key=f"del_media_{idx}"):
                        data_media.pop(idx)
                        save_json(FILE_MEDIA, data_media)
                        st.rerun()
                st.write("---")

    elif menu == "📊 Rekap Nilai Siswa":
        st.subheader("📊 Rekap Hasil Pengerjaan Kuis Siswa")
        if data_nilai:
            df_nilai = pd.DataFrame(data_nilai)
            st.dataframe(df_nilai, use_container_width=True)
            
            if st.button("🗑️ Hapus Semua Rekap Nilai"):
                save_json(FILE_NILAI, [])
                st.success("Rekap nilai berhasil dibersihkan!")
                st.rerun()
        else:
            st.info("Belum ada siswa yang mengerjakan kuis.")

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption("AI Tutor Bahasa Indonesia | Python + Streamlit + TXT Knowledge Base")