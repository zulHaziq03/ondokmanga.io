from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
from models import db, Manga, Chapter, ChapterImage
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manga.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    mangas = Manga.query.all()
    return render_template('index.html', mangas=mangas)

@app.route('/read/<int:chapter_id>')
def read_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('read_chapter.html', chapter=chapter)

@app.route('/admin')
def admin_panel():
    mangas = Manga.query.all()
    return render_template('admin.html', mangas=mangas)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/mangas', methods=['GET'])
def get_mangas():
    mangas = Manga.query.all()
    return jsonify([{'id': m.id, 'title': m.title} for m in mangas])

@app.route('/api/add_manga', methods=['POST'])  # Changed endpoint
def api_add_manga():
    title = request.form.get('title')
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    new_manga = Manga(title=title)
    db.session.add(new_manga)
    db.session.commit()
    return jsonify({'message': 'Manga added'}), 201

@app.route('/add_manga', methods=['POST'])
def add_manga():
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.files.get('cover_image')

    if not title or not file:
        return redirect(url_for('admin_panel'))

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        new_manga = Manga(title=title, cover_image=filename)
        db.session.add(new_manga)
        db.session.commit()

    return redirect(url_for('admin_panel'))


@app.route('/api/chapters', methods=['POST'])
def upload_chapter():
    title = request.form.get('title')
    manga_id = request.form.get('manga_id')
    files = request.files.getlist('images')

    if not title or not manga_id or not files:
        return jsonify({'error': 'Missing required fields'}), 400

    chapter = Chapter(title=title, manga_id=manga_id)
    db.session.add(chapter)
    db.session.commit()

    for index, file in enumerate(files, start=1):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            image = ChapterImage(
                filename=filename,
                image_path=filepath,  # full relative path
                chapter_id=chapter.id,
                page_number=index
            )
            db.session.add(image)

    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    chapters = Chapter.query.all()
    result = []
    for ch in chapters:
        result.append({
            'id': ch.id,
            'title': ch.title,
            'manga': ch.manga.title,
            'images': [img.image_path for img in ch.images]
        })
    return jsonify(result)

@app.route('/api/chapters/<int:manga_id>', methods=['GET'])
def get_chapters_by_manga(manga_id):
    chapters = Chapter.query.filter_by(manga_id=manga_id).all()
    result = []
    for ch in chapters:
        result.append({
            'id': ch.id,
            'title': ch.title,
            'images': [img.image_path for img in ch.images]
        })
    return jsonify(result)

@app.route('/manga/<int:manga_id>')
def view_manga(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    return render_template('manga_detail.html', manga=manga)


@app.route('/manga/<int:manga_id>')
def manga_detail(manga_id):
    manga = Manga.query.get_or_404(manga_id)
    return render_template('manga_detail.html', manga=manga)


if __name__ == '__main__':
    app.run(debug=True)
