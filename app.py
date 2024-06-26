from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import os
from utils import encrypt_file, decrypt_file
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'xlsx', 'zip', 'bin'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'supersecretkey'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            password = request.form['password']
            if password:
                filename = secure_filename(file.filename)
                file_data = file.read()
                encrypted_data = encrypt_file(file_data, password)
                encrypted_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted_' + filename)
                with open(encrypted_filename, 'wb') as f:
                    f.write(encrypted_data)
                return send_file(encrypted_filename, as_attachment=True)
            else:
                flash('Password is required')
                return redirect(request.url)
        else:
            flash('File type not allowed')
            return redirect(request.url)
    return render_template('encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            password = request.form['password']
            if password:
                encrypted_data = file.read()
                try:
                    decrypted_data = decrypt_file(encrypted_data, password)
                    decrypted_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted_' + file.filename)
                    with open(decrypted_filename, 'wb') as f:
                        f.write(decrypted_data)
                    return send_file(decrypted_filename, as_attachment=True)
                except Exception as e:
                    flash('Decryption failed: ' + str(e))
                    return redirect(request.url)
            else:
                flash('Password is required')
                return redirect(request.url)
        else:
            flash('File type not allowed')
            return redirect(request.url)
    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(debug=True)
