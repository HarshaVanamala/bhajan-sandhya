from services.sheets_service import GoogleSheetsService
from services.pass_service import PassService

SPREADSHEET_NAME = "Music Event TEST"

sheet_service = GoogleSheetsService()

registrations = sheet_service.get_registration_data(SPREADSHEET_NAME)

pass_service = PassService()

passes = pass_service.generate_passes(registrations)

print("=" * 70)
print(f"  Registrations  : {len(registrations)}")
print(f"  Passes Generated : {len(passes)}")
print("=" * 70)

for event_pass in passes:
    print(
        event_pass.code,
        "|",
        event_pass.name,
        "|",
        event_pass.phone,
        "|",
        event_pass.status,
    )