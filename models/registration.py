class Registration:
    def __init__(self, row):
        # Clean all column names by removing extra spaces
        cleaned = {k.strip(): v for k, v in row.items()}

        self.timestamp = cleaned.get("Timestamp")
        self.email = cleaned.get("Email Address")
        self.name = cleaned.get("Name")
        self.phone = str(cleaned.get("Whatsapp Number / Mobile Number"))

        self.gender = cleaned.get("Gender")
        self.age = cleaned.get("Age")

        self.pass_count = int(
            cleaned.get(
                "Select Number of Passes required \n(Entry Contribution: ₹250 per pass)",
                1,
            )
        )

        self.amount_paid = cleaned.get("Amount Paid (₹)")