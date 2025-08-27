import io, os, zipfile
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from tools import pdf_utils

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 150 * 1024 * 1024  # 150 MB per request; change if needed
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.get("/")
def index():
    return render_template("index.html")

def _send_pdf_bytes(b: bytes, filename: str):
    return send_file(io.BytesIO(b), mimetype="application/pdf", as_attachment=True, download_name=filename)

# Merge
@app.post("/api/merge")
def api_merge():
    files = request.files.getlist("files")
    if not files:
        return jsonify(error="No files uploaded"), 400
    out = pdf_utils.merge(files)
    return _send_pdf_bytes(out, "merged.pdf")

# Split (ranges or every N)
@app.post("/api/split")
def api_split():
    file = request.files.get("file")
    ranges = request.form.get("ranges")
    every = request.form.get("every")
    if not file:
        return jsonify(error="No file uploaded"), 400
    if ranges:
        parts = pdf_utils.split_pdf_by_ranges(file, ranges)
    elif every:
        try:
            n = int(every)
        except:
            return jsonify(error="Invalid 'every'"), 400
        parts = pdf_utils.split_pdf_every_n(file, n)
    else:
        return jsonify(error="Provide ranges or every"), 400
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, part in enumerate(parts, start=1):
            zf.writestr(f"part_{i}.pdf", part)
    mem.seek(0)
    return send_file(mem, mimetype="application/zip", as_attachment=True, download_name="split_parts.zip")

# Rotate
@app.post("/api/rotate")
def api_rotate():
    file = request.files.get("file")
    angle = int(request.form.get("angle", "90"))
    pages = request.form.get("pages", "*")
    if not file:
        return jsonify(error="No file uploaded"), 400
    out = pdf_utils.rotate_pdf_pages(file, angle, pages)
    return _send_pdf_bytes(out, "rotated.pdf")

# Reorder
@app.post("/api/reorder")
def api_reorder():
    file = request.files.get("file")
    order = request.form.get("order", "")
    if not file or not order:
        return jsonify(error="Provide file + order"), 400
    try:
        indices = [int(x) for x in order.split(",") if x.strip()]
    except:
        return jsonify(error="Bad order"), 400
    out = pdf_utils.reorder_pdf_pages(file, indices)
    return _send_pdf_bytes(out, "reordered.pdf")

# Protect
@app.post("/api/protect")
def api_protect():
    file = request.files.get("file")
    password = request.form.get("password", "")
    if not file or not password:
        return jsonify(error="Provide file + password"), 400
    out = pdf_utils.protect_pdf(file, password)
    return _send_pdf_bytes(out, "protected.pdf")

# Unprotect
@app.post("/api/unprotect")
def api_unprotect():
    file = request.files.get("file")
    password = request.form.get("password", "")
    if not file or not password:
        return jsonify(error="Provide file + password"), 400
    try:
        out = pdf_utils.unprotect_pdf(file, password)
    except Exception as e:
        return jsonify(error=str(e)), 400
    return _send_pdf_bytes(out, "unprotected.pdf")

# Extract pages
@app.post("/api/extract-pages")
def api_extract_pages():
    file = request.files.get("file")
    ranges = request.form.get("ranges", "")
    if not file or not ranges:
        return jsonify(error="Provide file + ranges"), 400
    out = pdf_utils.extract_pages(file, ranges)
    return _send_pdf_bytes(out, "extracted_pages.pdf")

# Watermark text
@app.post("/api/watermark-text")
def api_watermark_text():
    file = request.files.get("file")
    text = request.form.get("text", "").strip()
    opacity = float(request.form.get("opacity", "0.15"))
    fontsize = int(request.form.get("fontsize", "48"))
    rotation = int(request.form.get("rotation", "45"))
    if not file or not text:
        return jsonify(error="Provide file + text"), 400
    out = pdf_utils.add_watermark_text(file, text, opacity, fontsize, rotation)
    return _send_pdf_bytes(out, "watermarked.pdf")

# Page numbers
@app.post("/api/page-numbers")
def api_page_numbers():
    file = request.files.get("file")
    start = int(request.form.get("start", "1"))
    position = request.form.get("position", "bottom-right")
    if not file:
        return jsonify(error="Provide file"), 400
    out = pdf_utils.add_page_numbers(file, start=start, position=position)
    return _send_pdf_bytes(out, "page_numbers.pdf")

# Extract images
@app.post("/api/extract-images")
def api_extract_images():
    file = request.files.get("file")
    if not file:
        return jsonify(error="Provide file"), 400
    zip_bytes = pdf_utils.extract_images_zip(file)
    return send_file(io.BytesIO(zip_bytes), mimetype="application/zip", as_attachment=True, download_name="images.zip")

# Compress (basic: downscale images inside pdf via PyMuPDF)
@app.post("/api/compress")
def api_compress():
    file = request.files.get("file")
    quality = int(request.form.get("quality", "75"))  # 10..100
    if not file:
        return jsonify(error="Provide file"), 400
    out = pdf_utils.compress_pdf_basic(file, quality=quality)
    return _send_pdf_bytes(out, "compressed.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
