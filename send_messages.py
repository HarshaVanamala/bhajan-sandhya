"""
send_messages.py — Phase 2: Email (Gmail) + WhatsApp (pywhatkit)

Usage:
    python send_messages.py
"""

import smtplib
import time
import pywhatkit
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from services.sheets_service import GoogleSheetsService

# ── CONFIG ────────────────────────────────────────────────────────────────────

SPREADSHEET_NAME = "Music Event TEST"
WEBSITE_URL      = "https://bhajan-sandhya.onrender.com"

GMAIL_ADDRESS  = "harshavanamala1111@gmail.com"
GMAIL_APP_PASS = "tzfu lqgv buqy mvpf"
SENDER_NAME    = "Bhajan Sandhya by Kirtan Rasiks"

WHATSAPP_GAP   = 25  # seconds between messages

# ── EMAIL TEMPLATE ────────────────────────────────────────────────────────────

def email_html(name, code, pass_index, total_passes):
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body {{ margin:0; padding:0; background:#0E0604; font-family:'Georgia',serif; }}
    .wrap {{ max-width:520px; margin:0 auto; background:#0E0604; }}
    .header {{ background:linear-gradient(135deg,#7A1C10,#E8650A); padding:2.5rem 2rem 2rem; text-align:center; }}
    .header h1 {{ color:#F0C060; font-size:2rem; margin:0 0 0.25rem; letter-spacing:0.04em; }}
    .header p {{ color:rgba(255,255,255,0.7); font-size:0.85rem; margin:0; letter-spacing:0.08em; }}
    .body {{ padding:2rem; color:#FAF3E8; }}
    .greeting {{ font-size:1.1rem; color:#F0C060; margin-bottom:1rem; }}
    .para {{ font-size:0.9rem; color:rgba(250,243,232,0.75); line-height:1.7; margin-bottom:1.2rem; }}
    .code-box {{ background:rgba(201,146,42,0.1); border:1px solid rgba(201,146,42,0.35); border-radius:12px; padding:1.5rem; text-align:center; margin:1.5rem 0; }}
    .code-label {{ font-size:0.65rem; letter-spacing:0.18em; text-transform:uppercase; color:#C9922A; margin-bottom:0.5rem; }}
    .code {{ font-family:monospace; font-size:2rem; letter-spacing:0.25em; color:#F0C060; font-weight:bold; }}
    .pass-num {{ font-size:0.72rem; color:rgba(250,243,232,0.35); margin-top:0.4rem; }}
    .event-strip {{ background:rgba(255,255,255,0.03); border:1px solid rgba(201,146,42,0.15); border-radius:10px; padding:1rem 1.2rem; margin:1.2rem 0; }}
    .event-row {{ display:flex; justify-content:space-between; font-size:0.82rem; padding:0.35rem 0; border-bottom:1px solid rgba(201,146,42,0.08); color:rgba(250,243,232,0.65); }}
    .event-row:last-child {{ border-bottom:none; }}
    .event-row span:first-child {{ color:#C9922A; }}
    .cta {{ display:block; background:linear-gradient(135deg,#E8650A,#7A1C10); color:#fff !important; text-decoration:none; text-align:center; padding:0.9rem 1.5rem; border-radius:10px; font-size:0.88rem; letter-spacing:0.05em; margin:1.5rem 0 0.75rem; }}
    .cta-note {{ font-size:0.72rem; color:rgba(250,243,232,0.35); text-align:center; line-height:1.6; }}
    .spam-note {{ font-size:0.72rem; color:rgba(250,243,232,0.3); text-align:center; margin-top:0.75rem; font-style:italic; }}
    .footer {{ text-align:center; padding:1.5rem 2rem; border-top:1px solid rgba(201,146,42,0.1); font-size:0.72rem; color:rgba(250,243,232,0.25); line-height:1.7; }}
  </style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>Bhajan Sandhya</h1>
    <p>by Kirtan Rasiks &nbsp;·&nbsp; ॥ हरे कृष्ण ॥</p>
  </div>
  <div class="body">
    <p class="greeting">Hare Krishna, {name} 🙏</p>
    <p class="para">Your registration for <strong style="color:#F0C060">Bhajan Sandhya</strong> is confirmed. An evening of devotion, melody, and kirtan awaits you — presented by the young troupe of Kirtan Rasiks.</p>
    <div class="code-box">
      <div class="code-label">Your Pass Code</div>
      <div class="code">{code}</div>
      <div class="pass-num">Pass {pass_index} of {total_passes}</div>
    </div>
    <div class="event-strip">
      <div class="event-row"><span>📅 Date</span><span>July 4, 2026 · Saturday</span></div>
      <div class="event-row"><span>🕔 Time</span><span>5:30 PM – 8:30 PM</span></div>
      <div class="event-row"><span>📍 Venue</span><span>Marri Krishna Hall, Tarnaka</span></div>
    </div>
    <a href="{WEBSITE_URL}" class="cta">Get Your Entry QR →</a>
    <p class="cta-note">
      Copy your pass code <strong style="color:#C9922A">{code}</strong> and paste it in the QR generator on the website to get your entry QR.<br/>
      Show that QR to the volunteer at the gate.
    </p>
    <p class="spam-note">📧 If this email landed in spam, please mark it as Not Spam so you don't miss updates.</p>
  </div>
  <div class="footer">
    Each pass is valid for one person only.<br/>
    Do not share this code. See you on July 4! 🪈<br/><br/>
    Kirtan Rasiks · Bhajan Sandhya 2026
  </div>
</div>
</body>
</html>"""


# ── WHATSAPP TEMPLATE ─────────────────────────────────────────────────────────

def whatsapp_text(name, code, pass_index, total_passes):
    return (
        f"🙏 *Hare Krishna, {name}!*\n\n"
        f"Your pass for *Bhajan Sandhya* is confirmed.\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎵 *Bhajan Sandhya* by Kirtan Rasiks\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📅 July 4, 2026 · Saturday\n"
        f"🕔 5:30 PM – 8:30 PM\n"
        f"📍 Marri Krishna Hall, Tarnaka\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🎟 *Your Pass Code:* `{code}`\n"
        f"_(Pass {pass_index} of {total_passes})_\n\n"
        f"To get your entry QR, visit:\n"
        f"🔗 {WEBSITE_URL}\n\n"
        f"Copy your pass code *{code}* and paste it in the QR generator on the website. "
        f"Show that QR to the volunteer at the gate.\n\n"
        f"📧 Also check your spam folder for the confirmation email and mark it as Not Spam.\n\n"
        f"Come, immerse in devotion and melody 🪈\n"
        f"_Each pass is valid for one person only._"
    )


# ── SEND FUNCTIONS ────────────────────────────────────────────────────────────

def send_email(to_email, name, code, pass_index, total_passes):
    msg = MIMEMultipart("alternative")
    msg["Subject"]  = f"🎵 Your Bhajan Sandhya Pass — {code}"
    msg["From"]     = f"{SENDER_NAME} <{GMAIL_ADDRESS}>"
    msg["To"]       = to_email
    msg["Reply-To"] = GMAIL_ADDRESS
    # Plain text fallback (helps avoid spam filters)
    plain = (
        f"Hare Krishna, {name}!\n\n"
        f"Your Bhajan Sandhya pass is confirmed.\n"
        f"Pass Code: {code} (Pass {pass_index} of {total_passes})\n\n"
        f"Date: July 4, 2026 | 5:30 PM onwards\n"
        f"Venue: Marri Krishna Hall, Tarnaka\n\n"
        f"Get your entry QR at: {WEBSITE_URL}\n"
        f"Copy your pass code and paste it in the QR generator on the website.\n\n"
        f"See you on July 4! Hare Krishna 🙏"
    )
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(email_html(name, code, pass_index, total_passes), "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())


def send_whatsapp(phone, name, code, pass_index, total_passes):
    number = str(phone).strip()
    if not number.startswith("+"):
        number = "+91" + number.lstrip("0")
    send_time = datetime.now() + timedelta(minutes=2)
    pywhatkit.sendwhatmsg(
        phone_no   = number,
        message    = whatsapp_text(name, code, pass_index, total_passes),
        time_hour  = send_time.hour,
        time_min   = send_time.minute,
        wait_time  = 20,
        tab_close  = True,
        close_time = 5,
    )


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  BHAJAN SANDHYA — MESSAGE SENDER")
    print("  Email: Gmail  |  WhatsApp: pywhatkit")
    print("=" * 60)

    sheets  = GoogleSheetsService()
    sheet   = sheets.open_spreadsheet(SPREADSHEET_NAME).worksheet("Passes")
    records = sheet.get_all_records()
    keys    = list(records[0].keys()) if records else []

    pending = [r for r in records if str(r.get("Message Sent", "")).strip().lower() != "yes"]

    print(f"\n  Total passes  : {len(records)}")
    print(f"  Already sent  : {len(records) - len(pending)}")
    print(f"  To send now   : {len(pending)}")

    if not pending:
        print("\n  ✅ All messages already sent. Nothing to do.")
        print("=" * 60)
        return

    print("\n  ⚠  Make sure WhatsApp Web is open in Chrome before continuing.")
    input("  Press Enter when ready...\n")

    sent_count   = 0
    failed_count = 0

    for i, row in enumerate(records):
        if str(row.get("Message Sent", "")).strip().lower() == "yes":
            continue

        name       = row.get("Name", "").strip()
        email      = row.get("Email", "").strip()
        phone      = str(row.get("Phone", "")).strip()
        code       = row.get("Pass Code", "").strip()
        pass_index = row.get("Pass Index", 1)
        total      = row.get("Total Passes", 1)
        row_number = i + 2
        msg_col    = keys.index("Message Sent") + 1

        print(f"\n  [{sent_count + 1}] {name}")
        print(f"       Code : {code}  (Pass {pass_index}/{total})")

        email_ok    = False
        whatsapp_ok = False

        # Email
        try:
            send_email(email, name, code, pass_index, total)
            print(f"       ✉  Email sent → {email}")
            email_ok = True
        except Exception as e:
            print(f"       ✗  Email failed: {e}")

        # WhatsApp
        try:
            send_whatsapp(phone, name, code, pass_index, total)
            print(f"       💬 WhatsApp scheduled → {phone}")
            whatsapp_ok = True
        except Exception as e:
            print(f"       ✗  WhatsApp failed: {e}")

        # Mark sent
        if email_ok or whatsapp_ok:
            sheet.update_cell(row_number, msg_col, "Yes")
            sent_count += 1
        else:
            failed_count += 1

        if sent_count < len(pending):
            print(f"       ⏳ Waiting {WHATSAPP_GAP}s before next...")
            time.sleep(WHATSAPP_GAP)

    print("\n" + "=" * 60)
    print(f"  ✅ Messages sent : {sent_count}")
    if failed_count:
        print(f"  ✗  Failed       : {failed_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()