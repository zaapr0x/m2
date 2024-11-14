import requests
import config
class DripRealmAPI:
    

    def __init__(self):
        """Initialize the API client with an API key."""
        
        self.BASE_URL = config.BASE_URL
        self.REALM_ID = config.REALM_ID
        self.REALM_POINT_ID = config.REALM_POINT_ID
        self.API_KEY = config.DRIP_API_KEY

        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json"
        }

    def view_user_balance(self,user_id):
        """Retrieve a user's balance within a specific realm."""
        url = f"{self.BASE_URL}/api/v4/realms/{self.REALM_ID}/members/{user_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        print(response.json())
        return response.json()

    def update_user_balance(self,user_id,amount):
        """Update a user's balance within a realm by a specified amount."""
        url = f"{self.BASE_URL}/api/v4/realms/{self.REALM_ID}/members/{user_id}/tokenBalance"
        payload = {"realmPointId": self.REALM_POINT_ID, "tokens": amount}
        response = requests.patch(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

