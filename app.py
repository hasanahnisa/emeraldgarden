from flask import Flask, render_template, redirect, url_for, jsonify, request
from pymongo import MongoClient
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

def insert_admin():
   doc = {
            "username": "admin",                               
            "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",                                                                                   
            }
   find_admin = db.admin.find_one({'username':'admin'})
   if find_admin:
      return "sudah ada"
   else:
      db.admin.insert_one(doc)
      return "berhasil"

insert_admin()

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
      return render_template('login.html',msg="token tidak ada")


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
         
            
            if user_info:
               return render_template('adm-produk.html',user_info=user_info)
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

@app.route('/about')
def about():
   return render_template('about.html')

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
      
@app.route('/produk')
def produk():
   return render_template('produk.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)