import os
import time
import shutil

UPLOAD_FOLDER = 'uploads'
SCREENSHOT_FOLDER = 'screenshots'
MAX_AGE_SECONDS = 3600  # 1 hour

def remove_old_files(folder, max_age_seconds):
    now = time.time()
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        try:
            # If it’s a directory (screenshots), remove folder if old
            if os.path.isdir(filepath):
                mod_time = os.path.getmtime(filepath)
                if now - mod_time > max_age_seconds:
                    shutil.rmtree(filepath)
                    print(f"Removed folder: {filepath}")
            else:
                # File - check modification time
                mod_time = os.path.getmtime(filepath)
                if now - mod_time > max_age_seconds:
                    os.remove(filepath)
                    print(f"Removed file: {filepath}")
        except Exception as e:
            print(f"Error removing {filepath}: {e}")

if __name__ == "__main__":
    remove_old_files(UPLOAD_FOLDER, MAX_AGE_SECONDS)
    remove_old_files(SCREENSHOT_FOLDER, MAX_AGE_SECONDS)
