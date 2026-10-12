"""
Skrip pengujian black-box aplikasi Analisis Sentimen Ulasan DANA (Flask).

Letakkan berkas ini sejajar dengan app.py (satu folder dengan lexicon/, data/, templates/), lalu jalankan:

    pip install pytest
    pytest -v test_app.py

Nilai yang diharapkan (skor dan label) diambil dari Tabel 8 naskah dan dihitung dari
InSet Lexicon yang dimuat app.py. Tangkapan layar terminal hasil `pytest -v` dapat
dipakai sebagai bukti pengujian pada naskah.
"""
import os
import time

import pytest

# app.py membaca lexicon/ dan data/ dengan path relatif -> pindah ke folder berkas ini
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app, df, preprocessing, hitung_sentimen, label_sentimen  # noqa: E402


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    return app.test_client()


# (id, teks masukan, teks bersih yang diharapkan, skor yang diharapkan, label keluaran sistem)
SKENARIO_ANALISIS = [
    ("T2", "Wah bagus sekali dana pengiriman sangat cepat!!",
     "wah bagus kal dana pengirim cepat", 7.0, "positif"),
    ("T3", "Jelek saat pengiriman selalu gagal padahal tidak ada gangguan dari jaringan !!!",
     "jelek saat pengirim lalu gagal padahal ganggu jaring", -6.0, "negatif"),
    ("T4", "gk bisa login, saldo ilang, tolong dong",
     "login saldo ilang tolong", 0.0, "netral"),
    ("T5", "aplikasi dana",
     "aplikas dana", 4.0, "positif"),
    ("T7", "Mantap!!! \U0001F44D cek https://dana.id @admin 12345 bagus banget",
     "mantap cek bagus banget", -2.0, "negatif"),
]


def test_T1_halaman_utama_tanpa_hasil(client):
    r = client.get("/")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Hasil Analisis" not in html          # form tampil, belum ada hasil


@pytest.mark.parametrize("kode,teks,bersih,skor,label", SKENARIO_ANALISIS,
                         ids=[s[0] for s in SKENARIO_ANALISIS])
def test_analisis_teks(client, kode, teks, bersih, skor, label):
    # lapisan fungsi
    assert preprocessing(teks) == bersih
    assert hitung_sentimen(bersih) == pytest.approx(skor)
    assert label_sentimen(skor) == label
    # lapisan HTTP (POST ke form)
    r = client.post("/", data={"ulasan": teks})
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert str(float(skor)) in html


def test_T6_input_kosong_tidak_error(client):
    r = client.post("/", data={"ulasan": ""})
    assert r.status_code == 200                   # tidak error
    assert preprocessing("") == ""
    assert label_sentimen(hitung_sentimen("")) == "netral"   # belum ada pesan validasi


def test_T8_teks_panjang_dan_waktu(client):
    teks = "wah bagus sekali dana pengiriman sangat cepat " * 220    # sekitar 10.000 karakter
    assert len(teks) >= 10000
    r = client.post("/", data={"ulasan": teks})
    assert r.status_code == 200
    mulai = time.perf_counter()
    for _ in range(100):
        hitung_sentimen(preprocessing(teks))
    rata2_ms = (time.perf_counter() - mulai) / 100 * 1000
    print(f"\nRata-rata waktu pemrosesan teks panjang: {rata2_ms:.2f} ms")


def test_T9_dashboard_sesuai_berkas_hasil(client):
    r = client.get("/dashboard")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    total = len(df)
    hitung = df["label_sentimen"].value_counts().to_dict()
    assert total == 9999
    assert (hitung["positif"], hitung["negatif"], hitung["netral"]) == (4917, 4609, 473)
    for angka in (total, hitung["positif"], hitung["negatif"], hitung["netral"]):
        assert str(angka) in html
    for kelas in ("positif", "negatif", "netral"):
        assert f"{round(hitung[kelas] / total * 100, 2)}" in html


def test_konsistensi_jumlah_dan_pembulatan():
    hitung = df["label_sentimen"].value_counts().to_dict()
    assert sum(hitung.values()) == len(df)        # jumlah kelas = jumlah ulasan
    persen = [round(hitung[k] / len(df) * 100, 2) for k in ("positif", "negatif", "netral")]
    assert abs(sum(persen) - 100) <= 0.011        # selisih hanya karena pembulatan 2 desimal


def test_T10_alamat_tidak_ada_404(client):
    assert client.get("/halaman-tidak-ada").status_code == 404
