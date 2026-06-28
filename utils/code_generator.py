import random

# Removed confusing characters:
# O, 0, I, 1, L

CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

generated_codes = set()


def generate_pass_code():
    while True:
        code = "".join(random.choice(CHARACTERS) for _ in range(8))

        if code not in generated_codes:
            generated_codes.add(code)
            return code