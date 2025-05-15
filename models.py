from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chapters = db.relationship('Chapter', backref='manga', lazy=True, cascade="all, delete")
    cover_image = db.Column(db.String(255))
    description = db.Column(db.Text)  # 👈 Add this



class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ChapterImage', backref='chapter', lazy=True, cascade="all, delete")

class ChapterImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)  # FULL path relative to /uploads
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
