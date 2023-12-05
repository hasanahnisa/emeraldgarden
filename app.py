from flask import Flask, render_template, redirect, url_for, jsonify, request
app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/admin/fasilitas')
def adminFasilitas():
   return render_template('adm-fasilitas.html')

@app.route('/admin/produk')
def adminProduk():
   return render_template('adm-produk.html')

@app.route('/about')
def about():
   return render_template('about.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/produk')
def produk():
   return render_template('produk.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)