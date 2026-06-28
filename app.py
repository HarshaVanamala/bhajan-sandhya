"""
app.py — Bhajan Sandhya Event Management
Routes:
  /                → Visitor page (enter code → get QR)
  /volunteer       → Volunteer login + scan portal
  /admin           → Admin dashboard
  /api/verify-pass → API: check pass code, return QR
  /api/checkin     → API: mark entry at gate
  /api/admin/stats → API: live stats for admin
"""

import os
import io
import base64
import qrcode
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from services.sheets_service import GoogleSheetsService

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bhajan-sandhya-secret-2026")

SPREADSHEET_NAME = os.environ.get("SPREADSHEET_NAME", "Music Event TEST")
VOLUNTEER_PASSWORD = os.environ.get("VOLUNTEER_PASSWORD", "Volunteer@BShk")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin#BShk")

def get_sheets():
    return GoogleSheetsService()


def generate_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a0a00", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ─── VISITOR ────────────────────────────────────────────────────────────────

@app.route("/")
def visitor():
    return render_template("visitor.html")


@app.route("/api/verify-pass", methods=["POST"])
def verify_pass():
    code = request.json.get("code", "").strip().upper()
    if not code:
        return jsonify({"success": False, "message": "Please enter your pass code."})

    try:
        passes_sheet = get_sheets().open_spreadsheet(SPREADSHEET_NAME).worksheet("Passes")
        records = passes_sheet.get_all_records()
    except Exception as e:
        return jsonify({"success": False, "message": "Could not reach database. Try again."})

    for i, row in enumerate(records):
        if str(row.get("Pass Code", "")).strip().upper() == code:
            status = str(row.get("Status", "")).strip()
            name = row.get("Name", "")
            pass_index = row.get("Pass Index", "")
            total = row.get("Total Passes", "")

            if status == "Used":
                checkin_time = row.get("Check-in Time", "")
                return jsonify({
                    "success": False,
                    "already_used": True,
                    "message": f"This pass was already used at entry ({checkin_time}).",
                    "name": name,
                })

            qr_data = f"BHAJAN-SANDHYA|{code}|{name}"
            qr_b64 = generate_qr_base64(qr_data)

            # Mark QR as generated
            row_number = i + 2  # header is row 1
            col_index = list(row.keys()).index("QR Generated") + 1
            passes_sheet.update_cell(row_number, col_index, "Yes")

            return jsonify({
                "success": True,
                "name": name,
                "code": code,
                "pass_index": pass_index,
                "total_passes": total,
                "status": status,
                "qr": qr_b64,
            })

    return jsonify({"success": False, "message": "Pass code not found. Check and try again."})


# ─── VOLUNTEER ───────────────────────────────────────────────────────────────

@app.route("/volunteer", methods=["GET", "POST"])
def volunteer():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == VOLUNTEER_PASSWORD:
            session["volunteer"] = True
            return redirect(url_for("volunteer_portal"))
        return render_template("volunteer_login.html", error="Wrong password. Try again.")
    return render_template("volunteer_login.html", error=None)


@app.route("/volunteer/portal")
def volunteer_portal():
    if not session.get("volunteer"):
        return redirect(url_for("volunteer"))
    return render_template("volunteer_portal.html")


@app.route("/api/checkin", methods=["POST"])
def checkin():
    if not session.get("volunteer") and not session.get("admin"):
        return jsonify({"success": False, "message": "Not authorized."})

    code = request.json.get("code", "").strip().upper()
    volunteer_name = request.json.get("volunteer", "Volunteer")

    try:
        passes_sheet = get_sheets().open_spreadsheet(SPREADSHEET_NAME).worksheet("Passes")
        records = passes_sheet.get_all_records()
    except Exception:
        return jsonify({"success": False, "message": "Database error."})

    for i, row in enumerate(records):
        if str(row.get("Pass Code", "")).strip().upper() == code:
            status = str(row.get("Status", "")).strip()
            name = row.get("Name", "")
            pass_index = row.get("Pass Index", "")
            total = row.get("Total Passes", "")

            if status == "Used":
                checkin_time = row.get("Check-in Time", "")
                return jsonify({
                    "success": False,
                    "already_used": True,
                    "name": name,
                    "message": f"Already checked in at {checkin_time}",
                })

            row_number = i + 2
            keys = list(row.keys())
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            passes_sheet.update_cell(row_number, keys.index("Status") + 1, "Used")
            passes_sheet.update_cell(row_number, keys.index("Check-in Time") + 1, now)
            passes_sheet.update_cell(row_number, keys.index("Volunteer") + 1, volunteer_name)

            return jsonify({
                "success": True,
                "name": name,
                "code": code,
                "pass_index": pass_index,
                "total_passes": total,
                "message": f"✓ Entry granted for {name}",
            })

    return jsonify({"success": False, "message": "Pass code not found in system."})


# ─── ADMIN ───────────────────────────────────────────────────────────────────

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            session["volunteer"] = True  # admin can also do volunteer actions
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Wrong password.")
    return render_template("admin_login.html", error=None)


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    return render_template("admin_dashboard.html")


@app.route("/api/admin/stats")
def admin_stats():
    if not session.get("admin"):
        return jsonify({"error": "Not authorized"}), 403

    try:
        passes_sheet = get_sheets().open_spreadsheet(SPREADSHEET_NAME).worksheet("Passes")
        records = passes_sheet.get_all_records()
    except Exception:
        return jsonify({"error": "Database error"}), 500

    total = len(records)
    used = sum(1 for r in records if str(r.get("Status", "")).strip() == "Used")
    pending = total - used

    # Unique registrations = unique timestamps
    unique_regs = len(set(str(r.get("Timestamp", "")) for r in records))

    recent = [
        {
            "name": r.get("Name"),
            "code": r.get("Pass Code"),
            "checkin": r.get("Check-in Time"),
            "volunteer": r.get("Volunteer"),
        }
        for r in records if str(r.get("Status", "")).strip() == "Used"
    ][-10:][::-1]  # last 10, newest first

    all_passes = [
        {
            "name": r.get("Name"),
            "code": r.get("Pass Code"),
            "email": r.get("Email"),
            "phone": r.get("Phone"),
            "status": r.get("Status"),
            "pass_index": r.get("Pass Index"),
            "total": r.get("Total Passes"),
            "checkin": r.get("Check-in Time", ""),
            "msg_sent": r.get("Message Sent", "No"),
        }
        for r in records
    ]

    return jsonify({
        "total_passes": total,
        "used": used,
        "pending": pending,
        "unique_registrations": unique_regs,
        "recent_checkins": recent,
        "all_passes": all_passes,
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("visitor"))


if __name__ == "__main__":
    app.run(debug=True)

@app.route("/debug")
def debug():
    import os, json
    creds_env = os.environ.get("GOOGLE_CREDENTIALS", "")
    result = {
        "GOOGLE_CREDENTIALS_present": bool(creds_env),
        "GOOGLE_CREDENTIALS_length": len(creds_env),
        "SPREADSHEET_NAME": os.environ.get("SPREADSHEET_NAME", "NOT SET"),
    }
    if creds_env:
        try:
            parsed = json.loads(creds_env)
            result["json_valid"] = True
            result["client_email"] = parsed.get("client_email", "missing")
        except Exception as e:
            result["json_valid"] = False
            result["json_error"] = str(e)
    return jsonify(result)