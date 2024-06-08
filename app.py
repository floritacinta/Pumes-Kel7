from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
from hashlib import md5
import hashlib
from routes import main 
import os
from werkzeug.utils import secure_filename
import urllib.request

import nltk
nltk.download('popular')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('model/models.h5')
import json
import random
intents = json.loads(open('model/data.json').read())
words = pickle.load(open('model/texts.pkl','rb'))
classes = pickle.load(open('model/labels.pkl','rb'))

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample user data (username: [password, role])
users = {
    "1": ["c4ca4238a0b923820dcc509a6f75849b", "admin"], #pw=1
    "2": ["c81e728d9d4c2f636f067f89cc14862c", "user"], #pw=2
}

dokter = [
    {"id": 1, "nama": "Dr. A", "spesialisasi": "Ahli Bedah Ginekologi", "latar": "Lulus dari Fakultas Kedokteran Universitas D di Yogyakarta. Dia menyelesaikan pelatihan spesialisasi dalam Endokrinologi Reproduksi di Rumah Sakit GHI", "keahlian": " memiliki pengetahuan mendalam tentang gangguan hormonal yang mempengaruhi reproduksi perempuan, seperti PCOS, sindrom ovarium polikistik, dan gangguan menstruasi. Dia juga terampil dalam menangani kasus infertilitas dan menawarkan solusi yang sesuai.", "gambarr": "img/dokter/1.png"},
    {"id": 2, "nama": "Dr. B", "spesialisasi": "Dokter Kandungan", "latar": "dari Fakultas Kedokteran Universitas B di Surabaya. Setelah itu, dia menyelesaikan residensi dalam bidang Kandungan di Rumah Sakit ABC.", "keahlian": " seorang ahli dalam merawat perempuan yang sedang hamil atau berencana untuk hamil. Dia juga memiliki pengalaman dalam menangani masalah kesehatan reproduksi seperti endometriosis, PCOS, dan masalah kehamilan.", "gambarr": "img/dokter/2.png"},
    {"id": 3, "nama": "Dr. C", "spesialisasi": "Endokrinologi Reproduksi", "latar": " lulus dari Fakultas Kedokteran Universitas D di Yogyakarta. Dia menyelesaikan pelatihan spesialisasi dalam Endokrinologi Reproduksi di Rumah Sakit GHI.", "keahlian": " memiliki pengetahuan mendalam tentang gangguan hormonal yang mempengaruhi reproduksi perempuan, seperti PCOS, sindrom ovarium polikistik, dan gangguan menstruasi. Dia juga terampil dalam menangani kasus infertilitas dan menawarkan solusi yang sesuai.", "gambarr": "img/dokter/3.png"},
    {"id": 4, "nama": "Dr. D", "spesialisasi": "Obstetri dan Ginekologi", "latar": " memperoleh gelar doktornya dari Universitas C di Bandung. Dia menyelesaikan pelatihan residensi dalam bidang Bedah Ginekologi di Rumah Sakit DEF.", "keahlian": " seorang ahli bedah yang terampil dalam melakukan berbagai prosedur ginekologi, termasuk histerektomi, pengangkatan kista ovarium, dan penanganan endometriosis.", "gambarr": "img/dokter/4.png"},
]

artikel1 = [
    {"id": 1, "nama1": "Pentingnya Menjaga Kebersihan Alat Reproduksi", "kategori": "Reproduksi", "keterangan": "Kesehatan reproduksi remaja merupakan kondisi kesehatan yang menyangkut masalah kesehatan organ reproduksi, yang kesiapannya dimulai sejak usia remaja ditandai oleh haid pertama kali pada remaja perempuan atau mimpi basah bagi remaja laki-laki. Kesehatan reproduksi remaja meliputi fungsi, proses, dan sistem reproduksi remaja. Sehat yang dimaksudkan tidak hanya semata-mata bebas dari penyakit atau dari cacat saja, tetapi juga sehat baik fisik, mental maupun sosial. Pengetahuan Dasar Kesehatan Reproduksi Pada Remaja Usia remaja adalah masa transisi yang ditandai dengan berbagai perubahan emosi, psikis, dan fisik dengan ciri khas yang unik. Penting bagi remaja untuk mendapatkan informasi yang tepat tentang kesehatan reproduksi dan berbagai faktor yang berpengaruh terhadap kesehatan reproduksi. Sebagai pengenalan terhadap kesehatan reproduksi dasar, remaja harus mengetahui beberapa hal di bawah ini: Pengenalan tentang proses, fungsi, dan sistem alat reproduksi Mengetahui penyakit HIV/AIDS dan penyakit menular seksual lainnya, serta dampaknya pada kondisi kesehatan organ reproduksi Mengetahui dan menghindari kekerasan seksual Mengetahui pengaruh media dan sosial terhadap aktivitas seksual Mengembangkan kemampuan dalam berkomunikasi, terutama membentuk kepercayaan diri dengan tujuan untuk menghindari perilaku berisiko. Cara menjaga organ reproduksi, diantaranya: Pakai handuk yang lembut, kering, bersih, dan tidak berbau atau lembab. Memakai celana dalam dengan bahan yang mudah menyerap keringat Pakaian dalam diganti minimal 2 kali dalam sehari Bagi perempuan, sesudah buang air kecil, membersihkan alat kelamin sebaiknya dilakukan dari arah depan menuju belakang agar kuman yang terdapat pada anus tidakmasuk ke dalam organ reproduksi. Bagi laki-laki, dianjurkan untuk dikhitan atau disunat agarmencegah terjadinya penularan penyakit menular seksual serta menurunkan risiko kanker penis.", "gambarrr": "img/img/1.jpg"},
    {"id": 2, "nama1": "Cara Menjaga Kesehatan Mental Ibu Hamil untuk Cegah Depresi", "kategori": "Kehamilan", "keterangan": " Menjaga kesehatan mental ibu hamil sama pentingnya dengan menjaga kesehatan fisik. Selama kehamilan, tubuh Ibu mengalami perubahan hormon yang signifikan. Perubahan hormon ini dapat membuat ibu hamil menjadi lebih rentan terhadap stres. Stres yang dialami oleh ibu hamil dapat memiliki dampak negatif pada kesehatan mental ibu dan perkembangan bayi dalam kandungan. Oleh karena itu, kesehatan mental pada ibu hamil perlu dijaga. Lalu, apa pemicu masalah kesehatan mental ibu hamil? Bagaimana cara menjaga kesehatan mental saat sedang hamil? Lihat selengkapnya di sini, Bu. Pemicu Masalah Kesehatan Mental pada Ibu Hamil Kehamilan dan menjadi orang tua adalah perubahan besar dalam hidup. Baik calon ibu maupun calon ayah, keduanya perlu mempersiapkan diri secara mental untuk menghadapi peran baru ini. Bagi ibu, kehamilan memiliki posisi yang lebih spesial karena janin tumbuh dan berkembang dalam rahimnya. Namun, tidak dapat dipungkiri bahwa kehamilan seringkali membawa perasaan campur aduk dan tidak selalu semuanya positif. Ada rasa khawatir, cemas, dan ketakutan tentang kesehatan bayi dan diri sendiri. Hal-hal ini adalah perasaan yang wajar dirasakan oleh setiap ibu hamil, terutama pada kehamilan pertama atau kehamilan yang tidak direncanakan. Selain itu, ibu hamil seringkali menghadapi kesulitan dalam menghadapi perubahan dan ketidakpastian terkait kehamilan sehingga rentan terhadap dampak negatif yang ditimbulkan. Berikut beberapa hal yang berpotensi untuk memicu masalah kesehatan mental pada ibu hamil.", "gambarrr": "img/img/2.jpg"},

]

def get_md5_hash(password):
    return md5(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silahkan Login Kembali', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'admin':
            flash('Silahkan Login Kembali', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') != 'user':
            flash('Silahkan Login Kembali', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/hapus/<int:id>')
def hapus(id):
    for i, artikel in enumerate(artikel1):
        if artikel['id'] == id:
            artikel1.pop(i)
            break
    flash('berhasil Hapus Artikel', 'success')
    return redirect(url_for('artikel'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = md5(password.encode()).hexdigest() 
        if username in users and users[username][0] == hashed_password:  
            session['logged_in'] = True
            session['username'] = username
            session['password'] = hashed_password 
            session['role'] = users[username][1]
            if session['role'] == "admin":
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Username dan Password Salah', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username sudah digunakan, silakan pilih username lain', 'error')
            return render_template('reg.html')
        hashed_password = md5(password.encode()).hexdigest()
        role = 'user'
        users[username] = [hashed_password, role]
        flash('Pendaftaran berhasil, silakan login', 'success')
        return redirect(url_for('register1'))
    return render_template('reg.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_artikel(id):
    artikel_found = None
    for i, artikel in enumerate(artikel1):
        if artikel['id'] == id:
            artikel_found = artikel
            break
    if artikel_found:
        if request.method == 'POST':
            # Tangkap data dari form dan lakukan penyuntingan artikel
            artikel_found['nama1'] = request.form['nama1']
            artikel_found['kategori'] = request.form['kategori']
            artikel_found['keterangan'] = request.form['keterangan']
            flash('berhasil diedit', 'success')
            return redirect(url_for('edit_artikel', id=id))
        return render_template('admin/artikel/edit.html', artikel=artikel_found)
    return 'Artikel tidak ditemukan'


@app.route('/edit1/<int:id>', methods=['GET', 'POST'])
def edit_konsultasi(id):
    konsultasi_found = None
    for i, konsultasi in enumerate(dokter):
        if konsultasi['id'] == id:
            konsultasi_found = konsultasi
            break
    if konsultasi_found:
        if request.method == 'POST':
            konsultasi_found['spesialisasi'] = request.form['spesialisasi']
            konsultasi_found['latar'] = request.form['latar']
            konsultasi_found['keahlian'] = request.form['keahlian']
            flash('berhasil diedit', 'success')
            return redirect(url_for('edit_konsultasi', id=id))
        return render_template('admin/konsultasi/edit.html', artikel=konsultasi_found)
    return 'konsultasi tidak ditemukan'


def generate_calendar(start_date, end_date):
    calendar = []
    current_date = start_date
    while current_date <= end_date:
        calendar.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return calendar

app.register_blueprint(main)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout Berhasil', 'success')
    return redirect(url_for('login'))


#==============admin================


@app.route('/admin/list_daftar', methods=['GET', 'POST'])
@admin_required
def show_users():
    if request.method == 'POST':
        for user_id in users:
            new_role = request.form.get(user_id)
            if new_role:
                users[user_id][1] = new_role

    return render_template('admin/users.html', users=users)



@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def edit555():
    if 'logged_in' in session:
        username = session['username']
        role = session['role']
        if request.method == 'POST':
            old_username = session['username']
            old_password = session['password']
            new_username = request.form.get('new_username')
            new_password = request.form.get('new_password')
            
            if old_username in users and users[old_username][0] == old_password:
                update_password = False
                if new_password:  # Periksa jika kata sandi baru diberikan
                    new_password_hash = hashlib.md5(new_password.encode()).hexdigest()
                    update_password = True
                else:
                    new_password_hash = old_password

                if new_username and new_username != old_username:
                    if new_username not in users:
                        users[new_username] = [new_password_hash, role]
                        del users[old_username]
                        session['username'] = new_username
                        session['password'] = new_password_hash if update_password else old_password
                        flash('Username dan Password berhasil diubah' if update_password else 'Username berhasil diubah', 'success')
                    else:
                        flash('Username sudah digunakan', 'error')
                elif update_password:
                    users[old_username][0] = new_password_hash
                    session['password'] = new_password_hash
                    flash('Password berhasil diubah', 'success')
                else:
                    flash('Tidak ada perubahan yang dilakukan', 'info')
                
                return redirect(url_for('edit555'))
            else:
                flash('Silakan login kembali', 'error')
                
        return render_template('admin/settings.html', username=username)
    else:
        return redirect(url_for('edit555'))

@app.route('/riwajat_janji')
@admin_required
def riwajat_janji():
    input_dokter = session.get('input_dokter')
    input_nama = session.get('input_nama')
    input_janji = session.get('input_janji')
    input_tanggal = session.get('input_tanggal')
    if input_janji and input_tanggal and input_nama and input_dokter:
        return render_template('admin/riwajat_janji.html', input_janji=input_janji, input_tanggal=input_tanggal, input_nama=input_nama, input_dokter=input_dokter)
    else:
        flash('Belum Ada janji', 'error')
        return redirect(url_for('konsultasi'))


@app.route('/detail_dokter/<int:id>')
@admin_required
def detail_dokter(id):
    # Temukan produk dengan ID yang sesuai
    dokter_terpilih = next((p for p in dokter if p['id'] == id), None)
    if dokter_terpilih:
        return render_template('admin/konsultasi/detail_dokter.html', dokter=dokter_terpilih)
    else:
        return 'Tidak ditemukan'


@app.route('/janji_dokter/<int:id>', methods=['GET', 'POST'])
@admin_required
def janji(id):
    # Temukan dokter dengan ID yang sesuai
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if request.method == 'POST':
        input_dokter = request.form['input_dokter']
        input_nama = request.form['input_nama']
        input_janji = request.form['input_janji']
        input_tanggal = request.form['input_tanggal']
        session['input_dokter'] = input_dokter
        session['input_nama'] = input_nama
        session['input_janji'] = input_janji
        session['input_tanggal'] = input_tanggal
        # Proses input janji dan simpan ke database jika diperlukan
        return redirect(url_for('berhasil', id=id, message=input_janji, tanggal=input_tanggal, nameee=input_nama, dokterrr=input_dokter))
    else:
        if dokter_terpilih:
            return render_template('admin/konsultasi/janji.html', dokter=dokter_terpilih)
        else:
            return 'Tidak ditemukan'

@app.route('/berhasil/<int:id>/<message>/<tanggal>/<nameee>/<dokterrr>')
@admin_required
def berhasil(id, message, tanggal, nameee, dokterrr):
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if dokter_terpilih:
        return render_template('admin/konsultasi/berhasil.html', dokter=dokter_terpilih, message=message, tanggal=tanggal, nameee=nameee, dokterrr=dokterrr)
    else:
        return 'Tidak ditemukan'


@app.route('/hapus_session')
@admin_required
def hapus_session():
    session.pop('input_dokter', None)
    session.pop('input_nama', None)
    session.pop('input_janji', None)
    session.pop('input_tanggal', None)
    flash('Janji sudah dihapus', 'success')
    return redirect(url_for('konsultasi'))


@app.route('/post/<int:id>')
@admin_required
def post(id):
    artikel_terpilih = next((p for p in artikel1 if p['id'] == id), None)
    if artikel_terpilih:
        return render_template('admin/artikel/post.html', artikel1=artikel_terpilih)
    else:
        return 'Tidak ditemukan'



@app.route('/kalkulator', methods=['POST'])
@admin_required
def kalkulator():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

        if end_date >= start_date:
            duration = (end_date - start_date).days + 1
            kalender = generate_calendar(start_date, end_date)
            return render_template('admin/kalender/kalkulator.html', durasi_haid=duration, kalender=kalender)
        else:
            error_message = 'Tanggal akhir harus lebih besar atau sama dengan tanggal awal.'
            return render_template('admin/kalender/kalkulator.html', error_message=error_message)

# UPLOAD_FOLDER = '/home/adit5454/mysite/static/img/img/'
UPLOAD_FOLDER = 'static/img/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload1', methods=['GET', 'POST'])
@admin_required
def upload1():
    if request.method == 'POST':
        nama1 = request.form['nama1']
        kategori = request.form['kategori']
        keterangan = request.form['keterangan']
        if 'gambarrr' in request.files:
            gambarrr = request.files['gambarrr']
            if gambarrr.filename != '':
                # Simpan file gambar di direktori uploads
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], gambarrr.filename)
                gambarrr.save(file_path)
        artikel1.append({"id": len(artikel1) + 1, "nama1": nama1, "kategori": kategori, "keterangan": keterangan, "gambarrr": f"img/img/{gambarrr.filename}"})
        flash('berhasil Upload Artikel', 'success')
        return redirect(url_for('artikel'))
    return render_template('admin/admin_dashboard.html')

#Chatbot
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    return res

#Route konektor

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')

@app.route('/admin/konsultasi')
@admin_required
def konsultasi():
    return render_template('admin/konsultasi/index.html', dokter=dokter)

@app.route('/admin/artikel')
@admin_required
def artikel():
    return render_template('admin/artikel/index.html', artikel1=artikel1)

@app.route('/admin/kalender')
@admin_required
def kalender():
    return render_template('admin/kalender/index.html')

@app.route('/admin/upload')
@admin_required
def upload():
    return render_template('admin/artikel/upload.html')

@app.route('/admin/chatbot')
@admin_required
def chatbot():
    return render_template('admin/chatbot/chatbot.html')

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

#===================user======================

@app.route('/user/list_daftar', methods=['GET', 'POST'])
@user_required
def show_usersu():
    if request.method == 'POST':
        for user_id in users:
            new_role = request.form.get(user_id)
            if new_role:
                users[user_id][1] = new_role
    return render_template('user/users.html', users=users)

@app.route('/user/settings', methods=['GET', 'POST'])
@user_required
def edit555u():
    if 'logged_in' in session:
        username = session['username']
        role = session['role']
        if request.method == 'POST':
            old_username = session['username']
            old_password = session['password']
            new_username = request.form.get('new_username')
            new_password = request.form.get('new_password')
            
            if old_username in users and users[old_username][0] == old_password:
                update_password = False
                if new_password:  # Periksa jika kata sandi baru diberikan
                    new_password_hash = hashlib.md5(new_password.encode()).hexdigest()
                    update_password = True
                else:
                    new_password_hash = old_password

                if new_username and new_username != old_username:
                    if new_username not in users:
                        users[new_username] = [new_password_hash, role]
                        del users[old_username]
                        session['username'] = new_username
                        session['password'] = new_password_hash if update_password else old_password
                        flash('Username dan Password berhasil diubah' if update_password else 'Username berhasil diubah', 'success')
                    else:
                        flash('Username sudah digunakan', 'error')
                elif update_password:
                    users[old_username][0] = new_password_hash
                    session['password'] = new_password_hash
                    flash('Password berhasil diubah', 'success')
                else:
                    flash('Tidak ada perubahan yang dilakukan', 'info')
                
                return redirect(url_for('edit555u'))
            else:
                flash('Silakan login kembali', 'error')
                
        return render_template('user/settings.html', username=username)
    else:
        return redirect(url_for('edit555u'))

@app.route('/riwajat_janjiu')
@user_required
def riwajat_janjiu():
    input_dokter = session.get('input_dokter')
    input_nama = session.get('input_nama')
    input_janji = session.get('input_janji')
    input_tanggal = session.get('input_tanggal')
    if input_janji and input_tanggal and input_nama and input_dokter:
        return render_template('user/riwajat_janji.html', input_janji=input_janji, input_tanggal=input_tanggal, input_nama=input_nama, input_dokter=input_dokter)
    else:
        flash('Belum Ada janji', 'error')
        return redirect(url_for('konsultasiu'))

@app.route('/detail_dokteru/<int:id>')
@user_required
def detail_dokteru(id):
    # Temukan produk dengan ID yang sesuai
    dokter_terpilih = next((p for p in dokter if p['id'] == id), None)
    if dokter_terpilih:
        return render_template('user/konsultasi/detail_dokter.html', dokter=dokter_terpilih)
    else:
        return 'Tidak ditemukan'

@app.route('/janji_dokteru/<int:id>', methods=['GET', 'POST'])
@user_required
def janjiu(id):
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if request.method == 'POST':
        input_dokter = request.form['input_dokter']
        input_nama = request.form['input_nama']
        input_janji = request.form['input_janji']
        input_tanggal = request.form['input_tanggal']
        session['input_dokter'] = input_dokter
        session['input_nama'] = input_nama
        session['input_janji'] = input_janji
        session['input_tanggal'] = input_tanggal
        return redirect(url_for('berhasilu', id=id, message=input_janji, tanggal=input_tanggal, nameee=input_nama, dokterrr=input_dokter))
    else:
        if dokter_terpilih:
            return render_template('user/konsultasi/janji.html', dokter=dokter_terpilih)
        else:
            return 'Tidak ditemukan'

@app.route('/berhasilu/<int:id>/<message>/<tanggal>/<nameee>/<dokterrr>')
@user_required
def berhasilu(id, message, tanggal, nameee, dokterrr):
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if dokter_terpilih:
        return render_template('user/konsultasi/berhasil.html', dokter=dokter_terpilih, message=message, tanggal=tanggal, nameee=nameee, dokterrr=dokterrr)
    else:
        return 'Tidak ditemukan'

@app.route('/hapus_sessionu')
@user_required
def hapus_sessionu():
    session.pop('input_dokter', None)
    session.pop('input_nama', None)
    session.pop('input_janji', None)
    session.pop('input_tanggal', None)
    flash('Janji sudah dihapus', 'success')
    return redirect(url_for('konsultasiu'))

@app.route('/postu/<int:id>')
@user_required
def postu(id):
    artikel_terpilih = next((p for p in artikel1 if p['id'] == id), None)
    if artikel_terpilih:
        return render_template('user/artikel/post.html', artikel1=artikel_terpilih)
    else:
        return 'Tidak ditemukan'

@app.route('/kalkulatoru', methods=['POST'])
@user_required
def kalkulatoru():
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

        if end_date >= start_date:
            duration = (end_date - start_date).days + 1
            kalender = generate_calendar(start_date, end_date)
            return render_template('user/kalender/kalkulator.html', durasi_haid=duration, kalender=kalender)
        else:
            error_message = 'Tanggal akhir harus lebih besar atau sama dengan tanggal awal.'
            return render_template('user/kalender/kalkulator.html', error_message=error_message)

UPLOAD_FOLDER = 'static/img/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload1u', methods=['GET', 'POST'])
@user_required
def upload1u():
    if request.method == 'POST':
        # Tangkap data dari form
        nama1 = request.form['nama1']
        kategori = request.form['kategori']
        keterangan = request.form['keterangan']
        if 'gambarrr' in request.files:
            gambarrr = request.files['gambarrr']
            if gambarrr.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], gambarrr.filename)
                gambarrr.save(file_path)
        artikel1.append({"id": len(artikel1) + 1, "nama1": nama1, "kategori": kategori, "keterangan": keterangan, "gambarrr": f"img/img/{gambarrr.filename}"})
        flash('berhasil Upload Artikel', 'success')
        return redirect(url_for('artikelu'))
    return render_template('user/user_dashboard.html')

@app.route('/user')
@user_required
def user_dashboard():
    return render_template('user/user_dashboard.html')

@app.route('/user/settings')
@user_required
def user_settings():
    return render_template('user/settings.html')

@app.route('/user/konsultasi')
@user_required
def konsultasiu():
    return render_template('user/konsultasi/index.html', dokter=dokter)

@app.route('/user/artikel')
@user_required
def artikelu():
    return render_template('user/artikel/index.html', artikel1=artikel1)

@app.route('/user/kalender')
@user_required
def kalenderu():
    return render_template('user/kalender/index.html')

@app.route('/user/upload')
@user_required
def uploadu():
    return render_template('user/artikel/upload.html')

#================main=====================



if __name__ == '__main__':
    app.run(debug=True)
