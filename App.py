from flask import Flask, request, render_template_string, redirect, url_for, flash, send_from_directory
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

# ==================== HTML + CSS embutidos ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MESSGAM - Sistema de Pautas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body { background-color: #f4f6f9; }
        .navbar-brand { font-weight: 700; letter-spacing: 1px; }
        .card-shadow { box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 16px; border: none; }
        .upload-zone { border: 2px dashed #dee2e6; border-radius: 12px; padding: 30px; text-align: center; transition: 0.3s; }
        .upload-zone:hover { border-color: #0d6efd; background-color: #f8f9ff; }
        .table th { background-color: #e9ecef; font-weight: 600; }
        .btn-actions { gap: 6px; }
        .listagem-card { min-height: 300px; }
        .footer { margin-top: 40px; text-align: center; color: #6c757d; font-size: 0.9rem; }
        .toast-container { position: fixed; top: 20px; right: 20px; z-index: 1050; }
    </style>
</head>
<body>

    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid px-4">
            <span class="navbar-brand mb-0 h1">
                <i class="bi bi-file-earmark-text"></i> MESSGAM · Pautas
            </span>
            <span class="navbar-text text-white-50">
                <i class="bi bi-clock"></i> Upload a qualquer hora
            </span>
        </div>
    </nav>

    <div class="container mt-4">

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="toast-container">
                    {% for category, message in messages %}
                        <div class="toast align-items-center text-white bg-{{ 'success' if category == 'success' else 'danger' }} border-0 show" role="alert">
                            <div class="d-flex">
                                <div class="toast-body">
                                    <i class="bi bi-{{ 'check-circle' if category == 'success' else 'exclamation-triangle' }} me-2"></i>
                                    {{ message }}
                                </div>
                                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <div class="row g-4">
            <div class="col-lg-4">
                <div class="card card-shadow p-4">
                    <h5 class="card-title mb-3">
                        <i class="bi bi-cloud-arrow-up text-primary"></i> Enviar nova pauta
                    </h5>
                    <form method="post" enctype="multipart/form-data" action="{{ url_for('upload') }}">
                        <div class="upload-zone">
                            <i class="bi bi-file-earmark-arrow-up" style="font-size: 2.5rem; color: #0d6efd;"></i>
                            <p class="mt-2 mb-1 text-secondary">Clique para selecionar ou arraste</p>
                            <input type="file" name="arquivo" class="form-control" id="fileInput" required style="display: none;">
                            <button type="button" class="btn btn-outline-primary btn-sm mt-2" onclick="document.getElementById('fileInput').click();">
                                <i class="bi bi-folder-open"></i> Escolher arquivo
                            </button>
                            <div id="fileSelected" class="mt-2 small text-muted"></div>
                        </div>
                        <div class="d-grid mt-3">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-send"></i> Enviar para MESSGAM
                            </button>
                        </div>
                    </form>
                    <div class="mt-2 small text-muted">
                        <i class="bi bi-info-circle"></i> Formatos: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG, ZIP. Máx. 16 MB.
                    </div>
                </div>

                <div class="card card-shadow p-3 mt-3">
                    <div class="d-flex justify-content-between">
                        <span><i class="bi bi-files"></i> Total de pautas:</span>
                        <span class="badge bg-primary rounded-pill">{{ files|length }}</span>
                    </div>
                    <div class="d-flex justify-content-between mt-1">
                        <span><i class="bi bi-hdd"></i> Espaço usado:</span>
                        <span class="badge bg-secondary rounded-pill">{{ total_size }}</span>
                    </div>
                </div>
            </div>

            <div class="col-lg-8">
                <div class="card card-shadow p-3 listagem-card">
                    <h5 class="card-title mb-3">
                        <i class="bi bi-list-ul text-primary"></i> Pautas arquivadas
                        <span class="badge bg-secondary ms-2">{{ files|length }}</span>
                    </h5>

                    {% if files %}
                        <div class="table-responsive">
                            <table class="table table-hover align-middle">
                                <thead>
                                    <tr>
                                        <th>Arquivo</th>
                                        <th>Data de envio</th>
                                        <th>Tamanho</th>
                                        <th class="text-center">Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for file in files %}
                                    <tr>
                                        <td>
                                            <i class="bi bi-file-{{ 'pdf' if file.extensao == 'PDF' else 'word' if file.extensao in ['DOC', 'DOCX'] else 'excel' if file.extensao in ['XLS', 'XLSX'] else 'image' if file.extensao in ['PNG', 'JPG', 'JPEG'] else 'archive' if file.extensao == 'ZIP' else 'text' }} me-2"></i>
                                            {{ file.nome }}
                                        </td>
                                        <td>{{ file.data }}</td>
                                        <td>{{ file.tamanho }}</td>
                                        <td class="text-center">
                                            <div class="d-flex justify-content-center btn-actions">
                                                <a href="{{ url_for('download', filename=file.nome) }}" class="btn btn-outline-success btn-sm" title="Baixar">
                                                    <i class="bi bi-download"></i>
                                                </a>
                                                <a href="{{ url_for('delete', filename=file.nome) }}" class="btn btn-outline-danger btn-sm" title="Excluir" onclick="return confirm('Tem certeza que deseja excluir {{ file.nome }}?')">
                                                    <i class="bi bi-trash3"></i>
                                                </a>
                                            </div>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    {% else %}
                        <div class="text-center py-5 text-secondary">
                            <i class="bi bi-inbox" style="font-size: 3rem;"></i>
                            <p class="mt-3">Nenhuma pauta MESSGAM enviada ainda.</p>
                            <p class="small">Use o formulário ao lado para fazer o primeiro upload.</p>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>

        <div class="footer">
            <i class="bi bi-shield-check"></i> Sistema exclusivo para pautas MESSGAM · Todos os arquivos são renomeados com timestamp.
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'Nenhum arquivo selecionado';
            document.getElementById('fileSelected').innerHTML = '<i class="bi bi-check-circle text-success"></i> ' + fileName;
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    files = get_uploaded_files()
    total_bytes = sum(os.path.getsize(os.path.join(UPLOAD_FOLDER, f['nome'])) for f in files)
    total_size = format_file_size(total_bytes)
    return render_template_string(HTML_TEMPLATE, files=files, total_size=total_size)

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
