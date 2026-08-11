from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'messgam_super_secret_key_2026'

UPLOAD_FOLDER = 'uploads_messgam'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg', 'zip'}
MAX_FILE_SIZE = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_file_size(size_bytes):
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unidade}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_uploaded_files():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith('MESSGAM_'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            stat = os.stat(filepath)
            try:
                name_part = filename.split('_')[1] + '_' + filename.split('_')[2].split('.')[0]
                upload_time = datetime.datetime.strptime(name_part, '%Y%m%d_%H%M%S')
                data_str = upload_time.strftime('%d/%m/%Y às %H:%M:%S')
            except:
                data_str = 'Data desconhecida'
            files.append({
                'nome': filename,
                'tamanho': format_file_size(stat.st_size),
                'data': data_str,
                'extensao': filename.rsplit('.', 1)[1].upper() if '.' in filename else 'SEM EXT'
            })
    files.sort(key=lambda x: x['nome'], reverse=True)
    return files

@app.route('/')
def index():
    files = get_uploaded_files()
    total_bytes = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER, f['nome'])) for f in files)
    total_size = format_file_size(total_bytes)
    return render_template('index.html', files=files, total_size=total_size)

@app.route('/upload', methods=['POST'])
def upload():
    if 'arquivo' not in request.files:
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('index'))
    file = request.files['arquivo']
    if file.filename == '':
        flash('Nome de arquivo vazio.', 'danger')
        return redirect(url_for('index'))
    if not allowed_file(file.filename):
        flash('Formato não permitido.', 'danger')
        return redirect(url_for('index'))
    original_name = secure_filename(file.filename)
    ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"MESSGAM_{timestamp}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    file.save(filepath)
    flash(f'Pauta "{new_filename}" enviada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    if not filename.startswith('MESSGAM_'):
        flash('Arquivo inválido.', 'danger')
        return redirect(url_for('index'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete(filename):
    if not filename.startswith('MESSGAM_'):
        flash('Arquivo inválido.', 'danger')
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'Pauta "{filename}" excluída.', 'success')
    else:
        flash('Arquivo não encontrado.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("="*50)
    print("🚀 SERVIDOR MESSGAM INICIADO")
    print(f"📁 Pasta de upload: {os.path.abspath(UPLOAD_FOLDER)}")
    print("🌐 Acesse: http://localhost:5000")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=True)
