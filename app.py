from flask import Flask, render_template, redirect, url_for, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import os
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime, timedelta
import hashlib
import jwt
from werkzeug.utils import secure_filename

app = Flask(__name__)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

SECRET_KEY = 'skripsi'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client[DB_NAME]
TOKEN_KEY = 'my_token'

def insert_admin(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    doc = {
        "username": username,
        "password": hashed_password,
    }

    find_admin = db.admin.find_one({'username': username})
    
    if find_admin:
        return "Admin sudah ada"
    else:
        db.admin.insert_one(doc)
        return "Admin berhasil ditambahkan"
    
@app.route('/login')
def login():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)
   if msg:
      return render_template('login.html',msg=msg)
   else:
      if token_receive:
         try:
               payload = jwt.decode(
                  token_receive,
                  SECRET_KEY,
                  algorithms=['HS256']
               )
               user_info = db.admin.find_one({'username':payload.get('id')})
            
               
               if user_info:
                  return render_template('adm-fasilitas.html',user_info=user_info)
               else:
                  return render_template('login.html')
                  
         except jwt.ExpiredSignatureError:
               msg='Your token has expired'
               return redirect(url_for('login', msg=msg))
         except jwt.exceptions.DecodeError:
               msg='There was a problem logging you in'
               return redirect(url_for('login', msg=msg))
      else:
         return render_template('login.html',msg=msg)
      
@app.route('/sign_in', methods=['POST'])
def sign_in():
   username_receive = request.form["username_give"]
   password_receive = request.form["password_give"]
   print(username_receive)
   pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
   result = db.admin.find_one(
      {
         "username": username_receive,
         "password": pw_hash,
      }
   )
   
   if result:
      payload = {
         "id": username_receive,
         "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
      }
      token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

      return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
   else:
      return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )
   
@app.route('/register_save', methods=['POST'])
def register_save():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

    doc = {
        "username" : username_receive,
        "password" : password_hash,
        "registration_time": datetime.now()
    }
    db.admin.insert_one(doc)
    db.admin.create_index([("registration_time", -1)]) 
    return jsonify({'result':'success'})

@app.route('/sign_up/check_dup', methods=['POST']) 
def check_dup():
     username_receive = request.form.get('username_give')
     user = db.admin.find_one({'username' : username_receive})
     exists = bool(user)
     return jsonify({'result':'success', 'exists' : exists})

@app.route('/register',methods=['GET'])
def register():
    return render_template("register.html")

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/admin/fasilitas')
def adminFasilitas():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)

   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
            fasilitas = db.fasilitas.find()
            data_fasilitas = list(fasilitas)

            
            if user_info:
               return render_template('adm-fasilitas.html',user_info=user_info, data_fasilitas=data_fasilitas)
            else:
               return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")

@app.route('/tambah/fasilitas',  methods=['POST'])
def tambahFasilitas():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)
   date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
         
            
            if user_info:
               if request.method == 'POST':
                  # Ambil data dari form
                  nama = request.form['nama_fasilitas']
                  jenis = request.form['jenis_fasilitas']
                  deskripsi = request.form['deskripsi_fasilitas']
                  
                  doc = {
                     "nama": nama,
                     "jenis": jenis,
                     "deskripsi": deskripsi,
                  }
                  
                  if "gambar_fasilitas" in request.files and request.files["gambar_fasilitas"].filename:
                     file = request.files["gambar_fasilitas"]
                     filename = secure_filename(file.filename)
                     extension = filename.split(".")[-1]
                     file_path = f"gambar_fasilitas/{nama}_{date}.{extension}"
                     file.save(os.path.join(os.getcwd(), 'static', file_path))
                     doc["gambar"] = file_path
                  else:
                     doc["gambar"] = ''

                  # Tambahkan data baru ke MongoDB
                  db.fasilitas.insert_one(doc)

                  return redirect(url_for('adminFasilitas'))
               
            else:
               return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")

@app.route('/perbarui/fasilitas', methods=['POST'])
def perbaruiFasilitas():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)
   date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
         
            
            if user_info:
               if request.method == 'POST':
                  id = request.form['id']
                  nama = request.form['nama_fasilitas']
                  jenis = request.form['jenis_fasilitas']
                  deskripsi = request.form['deskripsi_fasilitas']

                  # Ambil ID fasilitas dari parameter URL
                  id_fasilitas = ObjectId(id)

                  # Ambil dokumen fasilitas yang akan diperbarui
                  fasilitas = db.fasilitas.find_one({'_id': id_fasilitas})
                  
                  if fasilitas:
                        # Perbarui data pada dokumen fasilitas
                        fasilitas["nama"] = nama
                        fasilitas["jenis"] = jenis
                        fasilitas["deskripsi"] = deskripsi
                        gambar_lama = fasilitas.get('gambar', '')
                        # Perbarui gambar jika ada file yang diunggah
                        if "gambar_fasilitas" in request.files and request.files["gambar_fasilitas"].filename:
                           file = request.files["gambar_fasilitas"]
                           filename = secure_filename(file.filename)
                           extension = filename.split(".")[-1]
                           file_path = f"gambar_fasilitas/{nama}_{date}.{extension}"
                           file.save(os.path.join(os.getcwd(), 'static', file_path))
                           fasilitas["gambar"] = file_path
                           if gambar_lama:
                              gambar_path = os.path.join(os.getcwd(), 'static', gambar_lama)
                              try:
                                    if os.path.exists(gambar_path):
                                       os.remove(gambar_path)
                              except Exception as e:
                                    print(f"Error deleting old file: {e}")
                              
                        # Simpan perubahan ke MongoDB
                        db.fasilitas.update_one({'_id': id_fasilitas}, {'$set': fasilitas})
                        
                        return redirect(url_for('adminFasilitas'))
            else:
               return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")   
   
@app.route('/hapus/fasilitas/<id_fasilitas>')
def hapusFasilitas(id_fasilitas):
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)

   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
            fasilitas = db.fasilitas.find_one({'_id':ObjectId(id_fasilitas)})
            
            if fasilitas:
               if user_info:
                  if 'gambar' in fasilitas:
                     gambar_path = os.path.join(os.getcwd(), 'static', fasilitas['gambar'])
                     if os.path.exists(gambar_path):
                        os.remove(gambar_path)
                     db.fasilitas.delete_one({'_id':ObjectId(id_fasilitas)})
                     return redirect(url_for('adminFasilitas'))
               else:
                  return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")   

@app.route('/get_fasilitas', methods=['GET'])
def get_fasilitas():
   fasilitas = list(db.fasilitas.find({}))
   print(fasilitas)
   
   list_fasilitas = []
   for data in fasilitas :
      doc = {
         '_id': str(data['_id']),
         'nama': data['nama'],
         'jenis': data['jenis'],
         'deskripsi': data['deskripsi'],
         'gambar': data['gambar'] if 'gambar' in data else None
      }
      
      list_fasilitas.append(doc)
   
   if fasilitas:
      return jsonify({
         'fasilitas': list_fasilitas
      })
   else:
      return jsonify({'error': 'Produk not found'}), 404

@app.route('/admin/produk')
def adminProduk():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)

   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
            produk = db.produk.find()
            data_produk = list(produk)
         
            
            if user_info:
               return render_template('adm-produk.html',user_info=user_info, data_produk=data_produk)
            else:
               return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")

@app.route('/tambah/produk',  methods=['POST'])
def tambahProduk():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)
   date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
         
            
            if user_info:
               if request.method == 'POST':
                  # Ambil data dari form
                  tipe = request.form['tipe']
                  deskripsi = request.form['deskripsi']
                  
                  doc = {
                     "tipe": tipe,
                     "deskripsi": deskripsi,
                  }
                  
                  if "gambar_produk" in request.files and request.files["gambar_produk"].filename:
                     file = request.files["gambar_produk"]
                     filename = secure_filename(file.filename)
                     extension = filename.split(".")[-1]
                     file_path = f"gambar_produk/{tipe}_{date}.{extension}"
                     file.save(os.path.join(os.getcwd(), 'static', file_path))
                     doc["gambar"] = file_path
                  else:
                     doc["gambar"] = ''

                  # Tambahkan data baru ke MongoDB
                  db.produk.insert_one(doc)

                  return redirect(url_for('adminProduk'))
               
            else:
               return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")

@app.route('/perbarui/produk', methods=['POST'])
def perbaruiProduk():
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)
   date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
         
            
            if user_info:
               if request.method == 'POST':
                  id = request.form['id']
                  tipe = request.form['tipe']
                  deskripsi = request.form['deskripsi']

                  # Ambil ID produk dari parameter URL
                  id_produk = ObjectId(id)

                  # Ambil dokumen produk yang akan diperbarui
                  produk = db.produk.find_one({'_id': id_produk})
                  
                  if produk:
                        # Perbarui data pada dokumen produk
                        produk["tipe"] = tipe
                        produk["deskripsi"] = deskripsi
                        gambar_lama = produk.get('gambar', '')
                        # Perbarui gambar jika ada file yang diunggah
                        if "gambar_produk" in request.files and request.files["gambar_produk"].filename:
                           file = request.files["gambar_produk"]
                           filename = secure_filename(file.filename)
                           extension = filename.split(".")[-1]
                           file_path = f"gambar_produk/{tipe}_{date}.{extension}"
                           file.save(os.path.join(os.getcwd(), 'static', file_path))
                           produk["gambar"] = file_path
                           if gambar_lama:
                              gambar_path = os.path.join(os.getcwd(), 'static', gambar_lama)
                              try:
                                    if os.path.exists(gambar_path):
                                       os.remove(gambar_path)
                              except Exception as e:
                                    print(f"Error deleting old file: {e}")
                              
                        # Simpan perubahan ke MongoDB
                        db.produk.update_one({'_id': id_produk}, {'$set': produk})
                        
                        return redirect(url_for('adminProduk'))
            else:
               return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")   
   
@app.route('/hapus/produk/<id_produk>')
def hapusProduk(id_produk):
   msg = request.args.get('msg')
   token_receive = request.cookies.get(TOKEN_KEY)

   if token_receive:
      try:
            payload = jwt.decode(
               token_receive,
               SECRET_KEY,
               algorithms=['HS256']
            )
            user_info = db.admin.find_one({'username':payload['id']})
            produk = db.produk.find_one({'_id':ObjectId(id_produk)})
            
            if produk:
               if user_info:
                  if 'gambar' in produk:
                     gambar_path = os.path.join(os.getcwd(), 'static', produk['gambar'])
                     if os.path.exists(gambar_path):
                        os.remove(gambar_path)
                     db.produk.delete_one({'_id':ObjectId(id_produk)})
                     return redirect(url_for('adminFasilitas'))
               else:
                  return render_template('login.html')
               
      except jwt.ExpiredSignatureError:
            msg='Your token has expired'
            return redirect(url_for('login', msg=msg))
      except jwt.exceptions.DecodeError:
            msg='There was a problem logging you in'
            return redirect(url_for('login', msg=msg))
   else:
      return render_template('login.html',msg="token tidak ada")   

@app.route('/get_produk', methods=['GET'])
def get_produk():
   produks = list(db.produk.find({}))
   print(produks)
   
   list_produk = []
   for produk in produks :
      doc = {
          '_id': str(produk['_id']),
         'tipe': produk['tipe'],
         'deskripsi': produk['deskripsi'],
         'gambar': produk['gambar'] if 'gambar' in produk else None
      }
      
      list_produk.append(doc)
   
   if produk:
      return jsonify({
         'produk': list_produk
      })
   else:
      return jsonify({'error': 'Produk not found'}), 404

@app.route('/about')
def about():
   return render_template('about.html')
      
@app.route('/produk30')
def produk30():
   return render_template('produk30.html')

@app.route('/produk36')
def produk36():
   return render_template('produk36.html')

@app.route('/produk60')
def produk60():
   return render_template('produk60.html')

@app.route('/produkkavling')
def produkkavling():
   return render_template('produkkavling.html')

@app.route('/fasilitas')
def fasilitas():
   return render_template('fasilitas.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)