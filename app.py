from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
from hashlib import md5
import hashlib
from routes import main 
import os
from werkzeug.utils import secure_filename
import urllib.request
import re
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample user data (username: [password, role])
users = {
    "admin@gmail.com": [hashlib.md5('admin123'.encode()).hexdigest(), "admin", 0, "", "", "", ""], 
    "user@gmail.com": [hashlib.md5('user123'.encode()).hexdigest(), "user", 0, "", "", "", ""],
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not re.match(r"[^@]+@gmail\.com", username):
            flash('Username harus Tipe @gmail.com', 'error')
            return render_template('login.html', username=username)
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        if username in users:
            if users[username][0] == hashed_password:
                session['logged_in'] = True
                session['username'] = username
                session['password'] = hashed_password 
                session['role'] = users[username][1]
                if session['role'] == "admin":
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Password salah', 'error')
                return render_template('login.html', username=username)
        else:
            flash('Username dan Password Salah', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validasi tipe email
        if not re.match(r"[^@]+@gmail\.com", username):
            flash('Username harus tipe @gmail.com', 'error')
            return render_template('reg.html')
        if len(password) < 5:
            flash('Password harus terdiri dari minimal 5 karakter', 'error')
            return render_template('reg.html', username=username)
        if not re.search(r"[a-zA-Z]", password) or not re.search(r"\d", password):
            flash('Password harus mengandung huruf dan angka', 'error')
            return render_template('reg.html', username=username)
        if username in users:
            flash('Username sudah digunakan, silakan pilih username lain', 'error')
            return render_template('reg.html')
        
        # Tetapkan nilai default untuk elemen yang kosong
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        role = 'user'
        empty_values = [0, "", "", "", ""]
        users[username] = [hashed_password, role] + empty_values
        
        flash('Pendaftaran berhasil, silakan login', 'success')
        return redirect(url_for('login'))

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
            if not re.match(r"[^@]+@gmail\.com", new_username):
                flash('Username harus Tipe @gmail.com', 'error')
                return render_template('admin/settings.html')
            if new_password:
                if len(new_password) < 5:
                    flash('Password harus terdiri dari minimal 5 karakter', 'error')
                    return render_template('admin/settings.html')
                if not re.search(r"[a-zA-Z]", new_password) or not re.search(r"\d", new_password):
                    flash('Password harus mengandung huruf dan angka', 'error')
                    return render_template('admin/settings.html')
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
    # Dapatkan username pengguna yang sedang masuk
    current_username = session.get('username')

    # Periksa apakah username pengguna ada di users
    if current_username in users:
        # Periksa apakah entri pengguna memiliki cukup banyak elemen
        if len(users[current_username]) >= 10:
            # Dapatkan data janji pengguna
            input_nama = users[current_username][7]
            input_janji = users[current_username][8]
            input_tanggal = users[current_username][9]
            input_dokter = users[current_username][10]
            
            return render_template('admin/riwajat_janji.html', input_nama=input_nama, input_janji=input_janji, input_tanggal=input_tanggal, input_dokter=input_dokter)
        else:
            flash('Belum ada janji', 'error')
            return redirect(url_for('konsultasi'))
    else:
        flash('Pengguna tidak ditemukan', 'error')
        return redirect(url_for('admin_dashboard'))


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
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if request.method == 'POST':
        input_dokter = request.form['input_dokter']
        input_nama = request.form['input_nama']
        input_janji = request.form['input_janji']
        input_tanggal = request.form['input_tanggal']
        
        # Dapatkan username pengguna yang sedang masuk
        current_username = session.get('username')
        
        # Periksa apakah username pengguna ada di users
        if current_username in users:
            # Periksa apakah entri pengguna memiliki cukup banyak elemen
            if len(users[current_username]) < 12:
                # Tambahkan elemen baru untuk data janji pada entri pengguna
                users[current_username].extend([""] * (12 - len(users[current_username])))
            
            # Perbarui data janji pada entri pengguna
            users[current_username][7] = input_nama
            users[current_username][8] = input_janji
            users[current_username][9] = input_tanggal
            users[current_username][10] = input_dokter
            
            # Atur session untuk input janji dan input tanggal
            session['input_nama'] = input_nama
            session['input_janji'] = input_janji
            session['input_tanggal'] = input_tanggal
            session['input_dokter'] = input_dokter

        return redirect(url_for('berhasil', id=id, dokterrr=input_dokter, nameee=input_nama, message=input_janji, tanggal=input_tanggal))
    else:
        if dokter_terpilih:
            return render_template('admin/konsultasi/janji.html', dokter=dokter_terpilih)
        else:
            return 'Tidak ditemukan'

@app.route('/berhasil/<int:id>')
@admin_required
def berhasil(id):
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if dokter_terpilih:
        dokterrr = request.args.get('dokterrr')
        nameee = request.args.get('nameee')
        message = request.args.get('message')
        tanggal = request.args.get('tanggal')
        return render_template('admin/konsultasi/berhasil.html', dokter=dokter_terpilih, dokterrr=dokterrr, nameee=nameee, message=message, tanggal=tanggal)
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
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], gambarrr.filename)
                gambarrr.save(file_path)
        artikel1.append({"id": len(artikel1) + 1, "nama1": nama1, "kategori": kategori, "keterangan": keterangan, "gambarrr": f"img/img/{gambarrr.filename}"})
        flash('berhasil Upload Artikel', 'success')
        return redirect(url_for('artikel'))
    return render_template('admin/admin_dashboard.html')


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



# @app.route('/admin/chatbot')
# @admin_required
# def chatbot():
#     return render_template('admin/chatbot/chatbot.html')




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
            if not re.match(r"[^@]+@gmail\.com", new_username):
                flash('Username harus Tipe @gmail.com', 'error')
                return render_template('user/settings.html')
            if new_password:
                if len(new_password) < 5:
                    flash('Password harus terdiri dari minimal 5 karakter', 'error')
                    return render_template('user/settings.html')
                if not re.search(r"[a-zA-Z]", new_password) or not re.search(r"\d", new_password):
                    flash('Password harus mengandung huruf dan angka', 'error')
                    return render_template('user/settings.html')
            if old_username in users and users[old_username][0] == old_password:
                update_password = False
                if new_password: 
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
    # Dapatkan username pengguna yang sedang masuk
    current_username = session.get('username')

    # Periksa apakah username pengguna ada di users
    if current_username in users:
        # Periksa apakah entri pengguna memiliki cukup banyak elemen
        if len(users[current_username]) >= 10:
            # Dapatkan data janji pengguna
            input_nama = users[current_username][7]
            input_janji = users[current_username][8]
            input_tanggal = users[current_username][9]
            input_dokter = users[current_username][10]
            
            return render_template('user/riwajat_janji.html', input_nama=input_nama, input_janji=input_janji, input_tanggal=input_tanggal, input_dokter=input_dokter)
        else:
            flash('Belum ada janji', 'error')
            return redirect(url_for('konsultasiu'))
    else:
        flash('Pengguna tidak ditemukan', 'error')
        return redirect(url_for('user_dashboard'))

@app.route('/detail_dokteru/<int:id>')
@user_required
def detail_dokteru(id):
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
        
        # Dapatkan username pengguna yang sedang masuk
        current_username = session.get('username')
        
        # Periksa apakah username pengguna ada di users
        if current_username in users:
            # Periksa apakah entri pengguna memiliki cukup banyak elemen
            if len(users[current_username]) < 12:
                # Tambahkan elemen baru untuk data janji pada entri pengguna
                users[current_username].extend([""] * (12 - len(users[current_username])))
            
            # Perbarui data janji pada entri pengguna
            users[current_username][7] = input_nama
            users[current_username][8] = input_janji
            users[current_username][9] = input_tanggal
            users[current_username][10] = input_dokter
            
            # Atur session untuk input janji dan input tanggal
            session['input_nama'] = input_nama
            session['input_janji'] = input_janji
            session['input_tanggal'] = input_tanggal
            session['input_dokter'] = input_dokter

        return redirect(url_for('berhasilu', id=id, dokterrr=input_dokter, nameee=input_nama, message=input_janji, tanggal=input_tanggal))
    else:
        if dokter_terpilih:
            return render_template('user/konsultasi/janji.html', dokter=dokter_terpilih)
        else:
            return 'Tidak ditemukan'

@app.route('/berhasilu/<int:id>')
@user_required
def berhasilu(id):
    dokter_terpilih = next((d for d in dokter if d['id'] == id), None)
    if dokter_terpilih:
        dokterrr = request.args.get('dokterrr')
        nameee = request.args.get('nameee')
        message = request.args.get('message')
        tanggal = request.args.get('tanggal')
        return render_template('user/konsultasi/berhasil.html', dokter=dokter_terpilih, dokterrr=dokterrr, nameee=nameee, message=message, tanggal=tanggal)
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

@app.route('/user/Feedback1', methods=['GET', 'POST'])
@user_required
def Feedback1():
    if 'logged_in' in session:
        username = session['username']
        role = session['role']
        current_user = users.get(username)

        if not current_user:
            flash('Pengguna tidak ditemukan', 'error')
            return redirect(url_for('user_dashboard'))

        current_rating = current_user[2] if len(current_user) > 2 else None

        if request.method == 'POST':
            new_rating = request.form.get('new_rating')
            layanan = request.form.get('layanan')
            layanan1 = request.form.get('layanan1')
            layanan2 = request.form.get('layanan2')
            ulasan = request.form.get('ulasan')

            if not all([new_rating, layanan, layanan1, layanan2, ulasan]):
                flash('Mohon isi semua layanan dan ulasan', 'error')
                return redirect(url_for('Feedback'))

            while len(current_user) < 7:
                current_user.append("")

            current_user[3] = layanan
            current_user[4] = layanan1
            current_user[5] = layanan2
            current_user[6] = ulasan
            current_user[2] = new_rating
                
            flash('Feedback berhasil disimpan', 'success')
            return redirect(url_for('Feedback'))
                
        return render_template('user/Feedback/index.html', current_rating=current_rating)
    else:
        return redirect(url_for('login'))

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

@app.route('/user/Feedback')
@user_required
def Feedback():
    return render_template('user/Feedback.html')


#================main=====================


if __name__ == '__main__':
    app.run(debug=True)
