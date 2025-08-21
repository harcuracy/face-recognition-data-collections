from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client
import base64
import uuid

app = Flask(__name__)

SUPABASE_URL = "https://phsbthgaxqowuutidjyx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBoc2J0aGdheHFvd3V1dGlkanl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2NDg1OTQsImV4cCI6MjA3MTIyNDU5NH0.DJEcVmQRGhN-1mcdmWoEzshkXyEVwJHY9ziY2jDTW9I"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "faces-dataset"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/save_image', methods=['POST'])
def save_image():
    data = request.get_json()
    img_data = data.get("image")
    matric_no = data.get("matric_no")

    if not img_data or not matric_no:
        return jsonify({"status": "error", "message": "Missing image or matric number"}), 400

    # Remove "data:image/png;base64," prefix
    img_data = img_data.split(",")[1]
    image_bytes = base64.b64decode(img_data)

    # Unique filename inside student's folder
    file_name = f"{matric_no}/{uuid.uuid4().hex}.png"

    try:
        res = supabase.storage.from_(BUCKET_NAME).upload(file_name, image_bytes)

        # If upload is successful, return public URL
        if res:
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
            return jsonify({"status": "success", "filename": file_name, "url": public_url})
        else:
            return jsonify({"status": "error", "message": "Upload failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
