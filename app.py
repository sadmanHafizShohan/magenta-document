import io
import os
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from pdf_to_magenta import image_to_magenta, pdf_to_magenta


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def convert_uploaded_file(upload, output_dir, threshold, outline_only, border_px, dpi):
    original_name = secure_filename(upload.filename or "")
    extension = Path(original_name).suffix.lower()
    if not original_name or extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {original_name or 'unknown file'}")

    input_path = Path(output_dir) / f"input{extension}"
    output_path = Path(output_dir) / f"converted{extension}"
    upload.save(input_path)

    if extension == ".pdf":
        pdf_to_magenta(
            str(input_path),
            str(output_path),
            dpi=dpi,
            threshold=threshold,
            outline_only=outline_only,
            border_px=border_px,
        )
    else:
        image_to_magenta(
            str(input_path),
            str(output_path),
            dpi=dpi,
            threshold=threshold,
            outline_only=outline_only,
            border_px=border_px,
        )

    return original_name, output_path


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert():
    uploads = [upload for upload in request.files.getlist("files") if upload.filename]
    if not uploads:
        return render_template("index.html", error="Please choose at least one PDF or image file.")

    try:
        threshold = max(0, min(255, int(request.form.get("threshold", 200))))
        border_px = max(0, min(50, int(request.form.get("border", 3))))
        dpi = max(72, min(600, int(request.form.get("dpi", 300))))
    except ValueError:
        return render_template("index.html", error="Threshold, border, and DPI must be valid numbers.")

    outline_only = request.form.get("outline") == "on"

    with tempfile.TemporaryDirectory() as temp_dir:
        converted = []
        try:
            for upload in uploads:
                original_name, output_path = convert_uploaded_file(
                    upload, temp_dir, threshold, outline_only, border_px, dpi
                )
                output_name = f"{Path(original_name).stem}_magenta{Path(original_name).suffix.lower()}"
                converted.append((output_name, output_path.read_bytes()))
        except (OSError, ValueError) as error:
            return render_template("index.html", error=str(error))

        if len(converted) == 1:
            output_name, content = converted[0]
            media_type = "application/pdf" if output_name.endswith(".pdf") else "image/*"
            return send_file(
                io.BytesIO(content),
                as_attachment=True,
                download_name=output_name,
                mimetype=media_type,
            )

        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for output_name, content in converted:
                bundle.writestr(output_name, content)
        archive.seek(0)
        return send_file(
            archive,
            as_attachment=True,
            download_name="magenta-converted-files.zip",
            mimetype="application/zip",
        )


@app.errorhandler(413)
def too_large(_error):
    return render_template("index.html", error="The upload is too large. Please keep the total size under 200 MB."), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
