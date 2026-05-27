from flask import Flask, render_template, request, send_file, jsonify
import os
import io
from werkzeug.utils import secure_filename

# ------------------ DATABASE ------------------
from db import init_db, insert_report, fetch_reports

# ------------------ SUMMARIZER ------------------
from utils.summarizer import (
    summarize_text,
    extract_keywords,
    extract_entities_from_text,
    calculate_quality_score,
    calculate_severity_score,
    doctor_recommendation,
    suggest_doctors,
    force_load_model
)

# ------------------ NEW MODULES ------------------
from utils.analytics import severity_stats
from utils.chatbot import ask_chatbot

# ------------------ SYSTEM PATHS ------------------
# os.environ["PATH"] += os.pathsep + r"C:\poppler\poppler-25.11.0\Library\bin"

# ------------------ OCR ------------------
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import pdfplumber
# from pdf2image import convert_from_path

# ------------------ APP CONFIG ------------------
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "txt"}

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# ------------------ INIT ------------------
force_load_model()
init_db()

# ------------------ GLOBAL STORAGE ------------------
latest_summary = ""

# ------------------ HELPERS ------------------
def extract_text_from_pdf(pdf_path: str) -> str:

    text = ""

    try:

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                t = page.extract_text()

                if t:
                    text += t + "\n"

    except Exception as e:

        print("PDF extraction error:", e)

    return text.strip()

    # OCR fallback
    if not text.strip():

        try:
            images = convert_from_path(pdf_path)

            for img in images:
                text += pytesseract.image_to_string(img)

        except Exception as e:
            print("OCR error:", e)

    return text.strip()

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ------------------ HISTORY ------------------

@app.route("/history")
def history():

    reports = fetch_reports()

    return render_template(
        "history.html",
        reports=reports
    )

# ------------------ DASHBOARD ------------------

@app.route("/dashboard")
def dashboard():

    stats = severity_stats()

    return render_template(
        "dashboard.html",
        stats=stats
    )

# ------------------ CHATBOT PAGE ------------------

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# ------------------ CHAT API ------------------

@app.route("/chat", methods=["POST"])
def chat():

    global latest_summary

    question = request.json.get("question", "")

    if not latest_summary:

        return jsonify({
            "response": "Please upload and summarize a medical report first."
        })

    try:

        response = ask_chatbot(
            latest_summary,
            question
        )

        return jsonify({
            "response": response
        })

    except Exception as e:

        return jsonify({
            "response": f"Chatbot error: {str(e)}"
        })

# ------------------ SUMMARIZE API ------------------

@app.route("/summarize", methods=["POST"])
def summarize():

    global latest_summary

    text = ""

    # ---------------- FILE UPLOAD ----------------

    if "file" in request.files and request.files["file"].filename != "":

        file = request.files["file"]

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        ext = filename.rsplit(".", 1)[1].lower()

        # PDF
        if ext == "pdf":

            text = extract_text_from_pdf(filepath)

        # TXT
        else:

            with open(
                filepath,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                text = f.read()

        # Delete uploaded file
        try:
            os.remove(filepath)

        except:
            pass

    # ---------------- TEXT INPUT ----------------

    elif request.form.get("text", "").strip():

        text = request.form["text"].strip()

    # ---------------- VALIDATION ----------------

    if not text or len(text) < 10:

        return jsonify({
            "error": "No valid text found."
        }), 400

    # ---------------- AI PROCESSING ----------------

    summary = summarize_text(text)

    # SAVE latest summary for chatbot
    latest_summary = summary

    keywords = extract_keywords(text)

    entities = extract_entities_from_text(text)

    quality = calculate_quality_score()

    severity = calculate_severity_score(text)

    recommendation = doctor_recommendation(
        severity["level"]
    )

    doctor_info = suggest_doctors(
        severity["level"]
    )

    summary_html = summary.replace(
        "\n",
        "<br>"
    )

    # ---------------- SAVE TO DATABASE ----------------

    insert_report(
        text,
        summary,
        severity["level"],
        severity["score"],
        recommendation,
        ", ".join(doctor_info["doctors"])
    )

    # ---------------- RESPONSE ----------------

    return jsonify({

        "summary": summary_html,

        "original_word_count": len(text.split()),

        "summary_word_count": len(summary.split()),

        "keywords": keywords,

        "entities": entities,

        "quality_score": quality,

        "severity": severity,

        "recommendation": recommendation,

        "doctor_specialty": doctor_info["specialty"],

        "suggested_doctors": doctor_info["doctors"]
    })

# ------------------ DOWNLOAD ------------------

@app.route("/download", methods=["POST"])
def download():

    summary = request.form.get("summary", "")

    buffer = io.BytesIO()

    buffer.write(summary.encode("utf-8"))

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="summary.txt",
        mimetype="text/plain"
    )

# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)