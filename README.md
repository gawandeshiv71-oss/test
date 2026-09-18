# OMR Sheet Checker

A full-stack web application for instantly grading OMR (Optical Mark Recognition) answer sheets using OpenCV computer vision.

---

## 🚀 Quick Start

### Step 1 — Install Python
Make sure **Python 3.8+** is installed: https://www.python.org/downloads/

### Step 2 — Start the backend
Double-click **`start.bat`** (Windows) or run in terminal:
```bash
pip install -r requirements.txt
python backend/app.py
```
Server starts at **http://localhost:5000**

### Step 3 — Open the frontend
Open **`frontend/index.html`** in your browser (Chrome/Edge recommended).

> ⚠️ The frontend must be opened **after** the backend is running. The server status indicator (top right) shows a green dot when connected.

---

## 📁 Folder Structure

```
timepass/
├── frontend/
│   ├── index.html        ← Dashboard
│   ├── upload.html       ← Upload OMR + Answer Key
│   ├── results.html      ← Grading Results
│   └── history.html      ← All Past Results
│
├── backend/
│   ├── app.py            ← Flask REST API
│   ├── omr_processor.py  ← OpenCV detection engine
│   ├── models.py         ← SQLite database
│   └── utils.py          ← PDF + parsers
│
├── uploads/              ← Stored OMR images (auto-created)
├── results/              ← SQLite DB + result JSONs (auto-created)
├── requirements.txt      ← Python dependencies
└── start.bat             ← One-click launcher (Windows)
```

---

## 📝 How to Use

### 1. Enter Answer Key
On the Upload page, enter the answer key in any of these formats:

**Text format:**
```
1=A, 2=B, 3=C, 4=D, 5=A
```

**JSON format:**
```json
{"1":"A","2":"B","3":"C","4":"D"}
```

**CSV format:**
```
1,A
2,B
3,C
```

### 2. Configure the Sheet
- **Total Questions** — number of questions on the sheet
- **Options per Q** — 3, 4, or 5 bubble options
- **Negative Marking** — optional, e.g. 0.25 per wrong answer

### 3. Upload the Image
- Drag & drop or click to browse
- Supported: JPG, PNG, BMP, TIFF, WEBP
- Tip: Use a flat, well-lit photo with the sheet filling most of the frame

### 4. View Results
- Donut chart breakdown
- Per-question answer table (filter by correct/wrong/skipped)
- Detected bubbles overlay on the processed image
- Download as PDF

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/health` | Server health check |
| `POST` | `/api/process` | Process single OMR sheet |
| `POST` | `/api/bulk-upload` | Process multiple sheets |
| `GET`  | `/api/results` | List all results |
| `GET`  | `/api/results/<id>` | Get single result |
| `DELETE` | `/api/results/<id>` | Delete result |
| `GET`  | `/api/download-pdf/<id>` | Download PDF report |

---

## 🧠 How the OMR Detection Works

1. **Load & Grayscale** — convert image to grayscale
2. **Threshold** — Otsu's adaptive binarization to separate dark bubbles from paper
3. **Contour Detection** — find the largest 4-point contour (sheet boundary)
4. **Perspective Warp** — flatten the sheet to a perfect rectangle
5. **Grid Division** — split into Q×N ROIs (rows = questions, cols = options)
6. **Fill Detection** — count white pixels per ROI; highest = selected bubble
7. **Grade** — compare against answer key → calculate score + overlay

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.3 | Web API server |
| flask-cors | 4.0.1 | Cross-origin requests |
| opencv-python | 4.9.0 | OMR image processing |
| numpy | 1.26.4 | Array operations |
| reportlab | 4.2.0 | PDF generation |
| Pillow | 10.3.0 | Image utilities |

---

## 💡 Tips for Best Accuracy

- Use a **flat, well-lit** scan or photo
- Ensure the **entire sheet** is visible with a small border around it
- Avoid shadows or glare on the bubbles
- Fill bubbles **completely and darkly**
- A scanned image (300+ DPI) works better than a phone photo

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Server Offline" in browser | Make sure `start.bat` / `python backend/app.py` is running |
| Import errors on start | Run `pip install -r requirements.txt` manually |
| Poor detection accuracy | Ensure the sheet has a clear rectangular border; try better lighting |
| PDF download fails | Check that ReportLab is installed: `pip install reportlab` |
