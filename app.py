from flask import Flask, request, render_template, send_from_directory
import os
import cv2
import uuid
import moviepy as mp

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
SCREENSHOT_FOLDER = 'screenshots'
MAX_DURATION_SECONDS = 300  # 5 minutes max video length

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

def video_to_screenshots(video_path, output_folder, interval_sec=1):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25  # fallback fps
    frame_interval = int(fps * interval_sec)
    count = 0
    saved_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_interval == 0:
            filename = os.path.join(output_folder, f"screenshot_{saved_count}.jpg")
            cv2.imwrite(filename, frame)
            saved_count += 1
        count += 1
    cap.release()

@app.route('/', methods=['GET', 'POST'])
def index():
    screenshots = []
    error = None
    interval = 2  # default interval

    if request.method == 'POST':
        file = request.files.get('video')
        interval_str = request.form.get('interval', '2')

        try:
            interval = max(1, int(interval_str))
        except ValueError:
            interval = 2

        if file and file.filename != '':
            unique_id = str(uuid.uuid4())
            video_filename = unique_id + '_' + file.filename
            video_path = os.path.join(UPLOAD_FOLDER, video_filename)
            file.save(video_path)

            # Check video duration
            try:
                clip = mp.VideoFileClip(video_path)
                duration = clip.duration
                clip.close()
            except Exception:
                os.remove(video_path)
                error = "Failed to process video file."
                return render_template('index.html', error=error, screenshots=[], interval=interval)

            if duration > MAX_DURATION_SECONDS:
                os.remove(video_path)
                error = f"Video too long! Max allowed length is {MAX_DURATION_SECONDS // 60} minutes."
                return render_template('index.html', error=error, screenshots=[], interval=interval)

            output_folder = os.path.join(SCREENSHOT_FOLDER, unique_id)
            video_to_screenshots(video_path, output_folder, interval_sec=interval)

            screenshots = [f"/screenshots/{unique_id}/{f}" for f in os.listdir(output_folder)]

    return render_template('index.html', error=error, screenshots=screenshots, interval=interval)

@app.route('/screenshots/<folder>/<filename>')
def screenshots(folder, filename):
    return send_from_directory(os.path.join(SCREENSHOT_FOLDER, folder), filename)

if __name__ == '__main__':
    app.run(debug=True)
