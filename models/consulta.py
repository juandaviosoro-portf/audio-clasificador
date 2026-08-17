from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Consulta(db.Model):
    __tablename__ = 'consultas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo_entrada = db.Column(db.String(20), nullable=False)  # 'audio' o 'texto'
    archivo_audio = db.Column(db.String(255), nullable=True)
    transcripcion = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(50), nullable=False)
    confianza = db.Column(db.Integer, nullable=False, default=0)
    prioridad = db.Column(db.String(20), nullable=False, default='MEDIA')
    resumen = db.Column(db.Text, nullable=True)
    duracion_audio = db.Column(db.Float, nullable=True)
    modelo_whisper = db.Column(db.String(20), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None,
            'tipo_entrada': self.tipo_entrada,
            'archivo_audio': self.archivo_audio,
            'transcripcion': self.transcripcion,
            'categoria': self.categoria,
            'confianza': self.confianza,
            'prioridad': self.prioridad,
            'resumen': self.resumen,
            'duracion_audio': round(self.duracion_audio, 2) if self.duracion_audio else None,
            'modelo_whisper': self.modelo_whisper
        }
