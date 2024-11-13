import requests as r
import json
import os
from dotenv import load_dotenv
load_dotenv()

class API:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = os.getenv("API_BASE_URL")
        self.realm = "6728c5f8eddb398453f0544e"
        self.headers = {"Authorization": f"Bearer {self.api_key}","Content-Type": "application/json"}

    def leaderboard(self):
        return r.get(f"{self.base_url}/api/v4/realms/{self.realm}/leaderboard", headers=self.headers).json()
        
    def get_user_balance(self, user_id):
        url = f"{self.base_url}/api/v4/realms/{self.realm}/members/{user_id}"
        req = r.get(url, headers=self.headers)
        if req.status_code == 200:
            data = {
                "status": req.status_code,
                "data": req.json()
            }
            return data
        else:
            data = {
                "status": req.status_code,

            }
            return data
        
    def update_balance(self, user_id, balance):
        url = f"{self.base_url}/api/v4/realms/{self.realm}/members/{user_id}/tokenBalance"
        data = {
            "realmPointId": '6728ca04eddb398453f0589f',
            "tokens": balance
        }
        req = r.patch(url, headers=self.headers, data=json.dumps(data))
        if req.status_code == 200:
            data = {
                "status": req.status_code,
                "data": req.json()
            }
            print("Balance updated successfully",data)
            return data
        else:
            data = {
                "status": req.status_code,

            }
            return data
