from models.registration import Registration
from models.pass_model import Pass

from utils.code_generator import generate_pass_code


class PassService:

    def generate_passes(self, registrations):

        all_passes = []

        for row in registrations:

            registration = Registration(row)

            for _ in range(registration.pass_count):

                pass_code = generate_pass_code()

                event_pass = Pass(pass_code, registration)

                all_passes.append(event_pass)

        return all_passes