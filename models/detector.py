from ultralytics import YOLO
import cv2

# Загрузка предобученной модели
model = YOLO('models/yolov8x-seg.pt')

def detect_and_annotate(img_path: str):
    """
    Принимает путь к изображению,
    возвращает (count, jpeg_bytes).
    """
    img = cv2.imread(img_path)
    results = model.predict(source=img)
    res = results[0]
    annotated = res.plot()             # numpy array с аннотацией
    _, buffer = cv2.imencode('.jpg', annotated)
    return len(res.boxes), buffer.tobytes()
