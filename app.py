import os
import requests

# Путь, куда будет скачиваться модель
MODEL_URL = 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x-seg.pt'
MODEL_PATH = os.path.join('models', 'yolov8x-seg.pt')

# Убедимся, что папка для модели существует
os.makedirs('models', exist_ok=True)

# Проверим, существует ли файл модели. Если нет, скачиваем.
if not os.path.exists(MODEL_PATH):
    print("Модель не найдена, скачиваем...")
    try:
        # Скачивание модели
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()  # Пытаемся поймать возможные ошибки при скачивании

        with open(MODEL_PATH, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"Модель успешно скачана в {MODEL_PATH}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании модели: {e}")
else:
    print(f"Модель уже есть по пути: {MODEL_PATH}")


import os
from flask import (
    Flask, render_template, request,
    jsonify, send_file
)
from datetime import datetime
from sqlalchemy import (
    create_engine, Column,
    Integer, String, DateTime
)
from sqlalchemy.orm import (
    declarative_base, sessionmaker
)
import pandas as pd

from models.detector import detect_and_annotate

# Создаём папки
os.makedirs('logs', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Настройка SQLite через SQLAlchemy
engine = create_engine('sqlite:///logs/history.db', echo=False)
Base   = declarative_base()
Session= sessionmaker(bind=engine)

class Record(Base):
    __tablename__ = 'records'
    id        = Column(Integer, primary_key=True)
    filename  = Column(String)
    count     = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Инициализируем Flask
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

# Обработка загруженного изображения
@app.route('/process-image', methods=['POST'])
def process_image():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file'}), 400

    # Сохраняем оригинал
    save_path = os.path.join('logs', file.filename)
    file.save(save_path)

    # Запускаем детектор
    count, jpg_bytes = detect_and_annotate(save_path)

    # Сохраняем запись в БД
    session = Session()
    rec = Record(filename=file.filename, count=count)
    session.add(rec)
    session.commit()
    session.close()

    # Возвращаем JSON с изображением в base64
    import base64
    img_b64 = base64.b64encode(jpg_bytes).decode('utf-8')
    return jsonify({
        'count': count,
        'image': f'data:image/jpeg;base64,{img_b64}'
    })

@app.route('/history')
def history():
    session = Session()
    records = session.query(Record).order_by(Record.timestamp.desc()).all()
    session.close()
    return render_template('history.html', records=records)

# Отчёт Excel
@app.route('/report/excel')
def report_excel():
    df = pd.read_sql_table('records', engine)
    out = 'reports/report.xlsx'
    df.to_excel(out, index=False, engine='openpyxl')
    return send_file(out, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)