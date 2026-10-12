# Analisis Sentimen Ulasan Pengguna Aplikasi DANA (Lexicon-Based)

Kode pendukung naskah *"Analisis Sentimen Ulasan Pengguna Aplikasi DANA Menggunakan Pendekatan
Lexicon-Based untuk Evaluasi Layanan"* (JUMISTIK). Repositori ini berisi aplikasi web Flask untuk
menganalisis sentimen teks ulasan dan menampilkan dashboard hasil analisis 9.999 ulasan.

## Isi repositori

| Berkas / folder | Keterangan |
|---|---|
| `app.py` | Aplikasi Flask: pra-pemrosesan, perhitungan skor InSet Lexicon, dan halaman web |
| `test_app.py` | Pengujian otomatis (pytest) untuk skenario T1-T10 pada Tabel 8 naskah |
| `lexicon/` | `positive.tsv` dan `negative.tsv` (InSet Lexicon) |
| `data/dana_hasil_sentimen.csv` | Hasil pelabelan sentimen 9.999 ulasan (dipakai dashboard) |
| `templates/`, `static/` | Tampilan web |
| `requirements.txt` | Daftar pustaka Python |

## Cara menjalankan

```bash
pip install -r requirements.txt
python app.py
```

Buka `http://127.0.0.1:5000/` untuk analisis teks dan `http://127.0.0.1:5000/dashboard` untuk dashboard.

## Cara menjalankan pengujian

```bash
python -m pytest -v test_app.py
```

Pengujian berjalan pada klien uji bawaan Flask (server tidak perlu menyala) dan memeriksa teks bersih,
skor, label, status HTTP, angka dashboard, serta konsistensi jumlah kelas terhadap berkas hasil.

## Metode singkat

1. Pra-pemrosesan: huruf kecil, hapus URL/mention/hashtag/angka/tanda baca/emoji, normalisasi slang,
   hapus stopword, dan stemming berbasis aturan (*Simple Stemmer*).
2. Skor ulasan = jumlah bobot kata yang ditemukan pada InSet Lexicon. Untuk kata yang ada di kedua
   daftar, bobot dengan nilai mutlak lebih besar dipakai.
3. Label: skor > 0 positif, skor < 0 negatif, skor = 0 netral.

## Keterbatasan

Tidak ada label rujukan (*ground truth*), sehingga akurasi tidak diukur. Nama aplikasi "dana" berbobot
positif pada kamus, kata penyangkal dibuang sebagai stopword, dan aplikasi belum memvalidasi input kosong.
Rincian ada pada naskah.

## Sumber kamus

InSet Lexicon (Koto & Rahmaningtyas, 2017). Cantumkan sumber resmi dan lisensinya sesuai ketentuan penyedia.
