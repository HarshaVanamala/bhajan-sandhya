"""
generate_passes.py

Run this script to:
  1. Read new registrations from Google Form sheet
  2. Skip registrations that already have passes generated
  3. Generate unique pass codes for each new registration
  4. Write all new passes into the Passes sheet

Usage:
    python generate_passes.py
"""

from datetime import datetime

from services.sheets_service import GoogleSheetsService
from services.pass_service import PassService
from models.registration import Registration

SPREADSHEET_NAME = "Music Event TEST"


def build_pass_rows(registrations, existing_timestamps):
    """
    For each new registration, generate passes and return
    a list of rows ready to be written to the Passes sheet.
    """
    pass_service = PassService()
    rows = []

    new_registrations = [
        reg for reg in registrations
        if str(reg.get("Timestamp", "")).strip() not in existing_timestamps
    ]

    print(f"  Total registrations     : {len(registrations)}")
    print(f"  Already processed       : {len(registrations) - len(new_registrations)}")
    print(f"  New registrations found : {len(new_registrations)}")

    if not new_registrations:
        return rows

    # PassService expects raw dicts (it creates Registration objects internally)
    passes = pass_service.generate_passes(new_registrations)

    # We need pass_index per registration, so we track it manually
    # Group passes by registration timestamp to assign pass_index
    pass_index_tracker = {}

    for raw_row in new_registrations:
        registration = Registration(raw_row)
        timestamp_key = str(registration.timestamp).strip()
        pass_index_tracker[timestamp_key] = 0

    for event_pass in passes:
        # Find the source registration to get full details
        # PassService copies name/email/phone into Pass, but not timestamp
        # We match by name+phone since Pass doesn't store timestamp
        matching_reg = next(
            (
                Registration(r)
                for r in new_registrations
                if Registration(r).name == event_pass.name
                and str(Registration(r).phone) == str(event_pass.phone)
            ),
            None,
        )

        if matching_reg is None:
            print(f"  [WARNING] Could not match pass for {event_pass.name} - skipping")
            continue

        ts_key = str(matching_reg.timestamp).strip()
        pass_index_tracker[ts_key] += 1
        pass_index = pass_index_tracker[ts_key]

        row = [
            matching_reg.timestamp,                    # Timestamp
            f"REG-{ts_key[-6:].replace(' ', '')}",    # Registration ID (short)
            event_pass.code,                           # Pass Code
            event_pass.name,                           # Name
            event_pass.email,                          # Email
            event_pass.phone,                          # Phone
            matching_reg.pass_count,                   # Total Passes
            pass_index,                                # Pass Index (1, 2, 3...)
            matching_reg.amount_paid,                  # Amount Paid
            event_pass.status,                         # Status → "Pending"
            "No",                                      # QR Generated
            "No",                                      # Message Sent
            "",                                        # Check-in Time
            "",                                        # Volunteer
        ]

        rows.append(row)

    return rows


def main():
    print("=" * 60)
    print("  EVENT PASS GENERATOR")
    print(f"  Spreadsheet : {SPREADSHEET_NAME}")
    print(f"  Run at      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    sheets = GoogleSheetsService()

    print("\n[1/4] Reading registrations...")
    registrations = sheets.get_registration_data(SPREADSHEET_NAME)

    print("\n[2/4] Checking existing passes...")
    existing_timestamps = sheets.get_existing_timestamps(SPREADSHEET_NAME)

    print("\n[3/4] Generating passes...")
    rows = build_pass_rows(registrations, existing_timestamps)

    if not rows:
        print("\n  ✅ Nothing to do — all registrations already have passes.")
        print("=" * 60)
        return

    print(f"\n[4/4] Writing {len(rows)} pass(es) to Passes sheet...")
    sheets.append_passes(SPREADSHEET_NAME, rows)

    print("\n" + "=" * 60)
    print(f"  ✅ Done! {len(rows)} passes written.")
    print("=" * 60)
    print("\nPasses written:")
    print(f"  {'Code':<12} {'Name':<20} {'Pass'}")
    print(f"  {'-'*12} {'-'*20} {'-'*6}")
    for row in rows:
        print(f"  {row[2]:<12} {row[3]:<20} {row[7]} of {row[6]}")


if __name__ == "__main__":
    main()