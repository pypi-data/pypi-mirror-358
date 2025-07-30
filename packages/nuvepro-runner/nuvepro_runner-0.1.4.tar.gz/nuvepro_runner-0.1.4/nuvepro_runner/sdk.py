from .sandbox import Sandbox
from dotenv import load_dotenv
import os

class Nuvepro:
    def create(self):
        # Load the .env file (from project root)
        load_dotenv()

        config = {
            "baseurl":os.getenv("CLOUDLABS_BASE_URL"),
            "planId": os.getenv("APP_PLAN_ID"),
            "userName": os.getenv("APP_USERNAME"),
            "password": os.getenv("APP_PASSWORD"),
            "companyId": os.getenv("APP_COMPANY_ID"),
            "teamId": os.getenv("APP_TEAM_ID")
        }
        return Sandbox(config=config)
