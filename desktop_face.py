"""CPU face verification with normalized profiles and a bounded camera session."""
from pathlib import Path
import time, base64

def verify(emit):
    emit('status', text='Step 1/5: importing camera and face libraries…')
    import cv2
    import numpy as np
    import joblib
    from insightface.app import FaceAnalysis
    profile = Path(__file__).resolve().parent / 'database' / 'face_profile.pkl'
    if not profile.exists():
        raise FileNotFoundError('Copy your own database/face_profile.pkl into this project. See START_HERE.txt.')
    emit('status', text='Step 2/5: reading your saved face profile…')
    known = np.asarray(joblib.load(profile), dtype=np.float32)
    if known.ndim == 1: known = known[None, :]
    if known.ndim != 2 or known.shape[1] != 512 or len(known) == 0 or not np.isfinite(known).all():
        raise ValueError('Invalid face profile. Rebuild it from your own face photos.')
    lengths = np.linalg.norm(known, axis=1, keepdims=True)
    if (lengths <= 0).any(): raise ValueError('Face profile contains an empty embedding.')
    known = known / lengths
    emit('status', text='Step 3/5: loading InsightFace models (first run may download files)…')
    model = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    emit('status', text='Step 4/5: preparing face models on CPU…')
    model.prepare(ctx_id=-1, det_size=(640, 640))
    emit('status', text='Step 5/5: opening camera…')
    camera = cv2.VideoCapture(0)
    try:
        if not camera.isOpened(): raise RuntimeError('Camera unavailable. Close other camera apps and check Windows camera permissions.')
        emit('status', text='Look at the camera • verifying your face')
        deadline = time.monotonic() + 30
        streak = 0
        while time.monotonic() < deadline:
            ok, frame = camera.read()
            if not ok: raise RuntimeError('Could not read camera frame.')
            faces = model.get(frame)
            matched = False
            if len(faces) == 1:
                vector = faces[0].embedding
                vector = vector / max(np.linalg.norm(vector), 1e-12)
                matched = float(np.max(known @ vector)) > 0.6
                x1,y1,x2,y2 = faces[0].bbox.astype(int)
                cv2.rectangle(frame,(x1,y1),(x2,y2),(100,230,80) if matched else (240,180,60),2)
            streak = streak + 1 if matched else 0
            small = cv2.resize(frame, (400, 300))
            ok, jpg = cv2.imencode('.jpg', small)
            if ok: emit('frame', data=base64.b64encode(jpg).decode())
            if streak >= 3: return True
        return False
    finally:
        camera.release()
