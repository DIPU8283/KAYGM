# PDF Tools — Local (Flask)

A minimal, beginner-friendly PDF tools web app that runs **locally on your laptop**.
Features included now:
- Merge PDFs (drag to reorder in UI)
- Split by ranges or every N pages
- Rotate pages
- Reorder pages (by order string)
- Protect / Unprotect (when you know the password)
- Extract specific pages
- Add text watermark (opacity, size, rotation)
- Add page numbers (position + start index)
- Extract embedded images (returns a ZIP)

> Note: Advanced features like **Compress**, **OCR**, and **PDF↔Word/PPT/Image** usually need extra system tools (Ghostscript / Tesseract / LibreOffice / Poppler). You can add them later.

---

## 1) Prerequisites (Windows)
- Install **Python 3.10+**
- Install **VS Code**

## 2) Setup (PowerShell commands)
Open **PowerShell** in this project folder and run:

```powershell
# 1) Create virtual environment
python -m venv .venv

# 2) Activate it
. .\.venv\Scripts\Activate.ps1

# 3) Install requirements
pip install -r requirements.txt

# 4) Run the server (host=0.0.0.0 lets other devices on same WiFi access it)
python app.py
```

Now open: **http://127.0.0.1:5000/**

To let others in your office (same WiFi/LAN) open it, get your local IP (e.g., `192.168.1.5`) and open:
**http://YOUR-IP:5000/**

> Keep your laptop ON while others are using it. When you close the terminal, the site will stop.

## 3) File size limit
Default limit is **50 MB per request**. Change it in `app.py`:
```python
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # bytes
```

## 4) Where is the code?
- `app.py` — Flask server + API routes
- `templates/index.html` — Simple front-end (Tailwind CDN)
- `static/script.js` — Client logic (drag-drop, form submits)
- `tools/pdf_utils.py` — All PDF operations (pypdf + PyMuPDF)

## 5) Next features (when you're ready)
- **Compression presets** (needs Ghostscript or image downsampling)
- **OCR to searchable PDF** (needs Tesseract + pdf2image + Poppler)
- **PDF ↔ Word/PPT/Image** (LibreOffice or other libs)
- User auth, rate limiting, logging, etc.

## 6) Stop the server
Press **Ctrl + C** in the terminal. To deactivate venv:
```powershell
deactivate
```
