from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)

# ── Load Lexicon ──────────────────────────────────────────
inset_pos = pd.read_csv('lexicon/positive.tsv', sep='\t', header=0, names=['word', 'weight'])
inset_neg = pd.read_csv('lexicon/negative.tsv', sep='\t', header=0, names=['word', 'weight'])

inset_pos = inset_pos[pd.to_numeric(inset_pos['weight'], errors='coerce').notna()].copy()
inset_neg = inset_neg[pd.to_numeric(inset_neg['weight'], errors='coerce').notna()].copy()

lexicon_pos = dict(zip(inset_pos['word'], inset_pos['weight'].astype(float)))
lexicon_neg = dict(zip(inset_neg['word'], inset_neg['weight'].astype(float)))

# ── Load Data Hasil ───────────────────────────────────────
df = pd.read_csv('data/dana_hasil_sentimen.csv')

# ── Preprocessing & Sentimen ──────────────────────────────
kamus_alay = {
    'gk': 'tidak', 'ga': 'tidak', 'gak': 'tidak', 'ngga': 'tidak',
    'nggak': 'tidak', 'tdk': 'tidak', 'udah': 'sudah', 'udh': 'sudah',
    'blm': 'belum', 'bgt': 'banget', 'sy': 'saya', 'gw': 'saya',
    'klo': 'kalau', 'kalo': 'kalau', 'utk': 'untuk', 'emang': 'memang',
    'msh': 'masih', 'bs': 'bisa', 'tp': 'tapi', 'jd': 'jadi',
    'app': 'aplikasi', 'apk': 'aplikasi', 'tf': 'transfer',
    'lemot': 'lambat', 'ribet': 'rumit', 'susah': 'sulit',
}

stopwords_id = set([
    'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'dengan',
    'untuk', 'pada', 'adalah', 'dalam', 'tidak', 'ada', 'juga',
    'saya', 'kami', 'kita', 'mereka', 'dia', 'sudah', 'akan',
    'bisa', 'karena', 'jadi', 'kalau', 'tapi', 'atau', 'lebih',
    'dapat', 'oleh', 'sangat', 'saja', 'seperti', 'lagi', 'semua',
    'maka', 'masih', 'setelah', 'ketika', 'namun', 'bahwa', 'belum',
    'pun', 'lah', 'kah', 'sih', 'deh', 'dong', 'nih', 'ya',
])

def simple_stem(kata):
    prefixes = ['memper', 'mempel', 'mempe', 'mem', 'men', 'meng',
                'meny', 'me', 'ber', 'per', 'ter', 'ke', 'se', 'di']
    suffixes = ['kan', 'an', 'i', 'nya', 'lah', 'kah', 'pun']
    for p in prefixes:
        if kata.startswith(p) and len(kata) > len(p) + 2:
            kata = kata[len(p):]
            break
    for s in suffixes:
        if kata.endswith(s) and len(kata) > len(s) + 2:
            kata = kata[:-len(s)]
            break
    return kata

def preprocessing(teks):
    teks = teks.lower()
    teks = re.sub(r'http\S+|www\S+', '', teks)
    teks = re.sub(r'@\w+|#\w+', '', teks)
    teks = re.sub(r'\d+', '', teks)
    teks = re.sub(r'[^\w\s]', '', teks)
    teks = re.sub(r'\s+', ' ', teks).strip()
    teks = ' '.join([kamus_alay.get(k, k) for k in teks.split()])
    teks = ' '.join([w for w in teks.split() if w not in stopwords_id])
    teks = ' '.join([simple_stem(k) for k in teks.split()])
    return teks

def hitung_sentimen(teks):
    skor = 0
    for kata in str(teks).split():
        p = lexicon_pos.get(kata, None)
        n = lexicon_neg.get(kata, None)
        if p is not None and n is not None:
            skor += p if abs(p) >= abs(n) else n
        elif p is not None:
            skor += p
        elif n is not None:
            skor += n
    return skor

def label_sentimen(skor):
    if skor > 0:
        return 'positif'
    elif skor < 0:
        return 'negatif'
    else:
        return 'netral'

# ── Routes ────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    if request.method == 'POST':
        teks_input = request.form.get('ulasan', '')
        teks_bersih = preprocessing(teks_input)
        skor = hitung_sentimen(teks_bersih)
        label = label_sentimen(skor)
        hasil = {
            'teks_asli': teks_input,
            'teks_bersih': teks_bersih,
            'skor': skor,
            'label': label
        }
    return render_template('index.html', hasil=hasil)

@app.route('/dashboard')
def dashboard():
    distribusi = df['label_sentimen'].value_counts().to_dict()
    total = len(df)
    stats = {
        'total': total,
        'positif': distribusi.get('positif', 0),
        'negatif': distribusi.get('negatif', 0),
        'netral': distribusi.get('netral', 0),
        'persen_pos': round(distribusi.get('positif', 0) / total * 100, 2),
        'persen_neg': round(distribusi.get('negatif', 0) / total * 100, 2),
        'persen_net': round(distribusi.get('netral', 0) / total * 100, 2),
    }
    return render_template('dashboard.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)