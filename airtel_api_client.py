"""
Airtel Money API Client
Official Airtel Kenya Developer Portal Integration
https://developers.airtel.africa/docs
"""

import requests
import json
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


class AirtelMoneyClient:
    """
    Airtel Money API Client for payment collection and disbursement
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        country: str = "KE",
        currency: str = "KES",
        sandbox: bool = True,
        callback_url: Optional[str] = None
    ):
        """
        Initialize Airtel Money Client

        Args:
            client_id: Your API client ID from developer portal
            client_secret: Your API client secret from developer portal
            country: Country code (default: KE for Kenya)
            currency: Currency code (default: KES)
            sandbox: Use sandbox environment (True) or production (False)
            callback_url: Webhook URL for transaction status callbacks
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.country = country
        self.currency = currency
        self.sandbox = sandbox
        self.callback_url = callback_url

        # Base URLs
        if sandbox:
            self.base_url = "https://openapiuat.airtelkenya.com"
        else:
            self.base_url = "https://openapi.airtelkenya.com"

        # Token storage
        self.access_token = None
        self.token_expires_at = None

    def get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "X-Country": self.country,
            "X-Currency": self.currency,
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def authenticate(self) -> bool:
        """
        Authenticate using OAuth2 client_credentials grant
        Tokens expire every 180 seconds (3 minutes)
        """
        auth_url = f"{self.base_url}/auth/oauth2/token"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }

        try:
            response = requests.post(auth_url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            self.access_token = result.get("access_token")
            expires_in = result.get("expires_in", 180)

            # Set token expiration time (subtract 10 seconds buffer)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 10)

            print(f"[SUCCESS] Authentication successful. Token expires in {expires_in} seconds")
            return True

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False

    def ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return True
        return self.authenticate()

    def ussd_push(
        self,
        msisdn: str,
        amount: float,
        reference: str,
        transaction_id: str
    ) -> Dict:
        """
        Request payment from subscriber's Airtel Money wallet via USSD push

        Args:
            msisdn: Subscriber phone number (format: 7XXXXXXXX)
            amount: Amount to collect
            reference: Payment reference (e.g., "Invoice payment")
            transaction_id: Unique transaction ID

        Returns:
            API response dictionary
        """
        if not self.ensure_authenticated():
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.base_url}/merchant/v1/payments/"

        payload = {
            "reference": reference,
            "subscriber": {
                "country": self.country,
                "currency": self.currency,
                "msisdn": msisdn
            },
            "transaction": {
                "amount": amount,
                "country": self.country,
                "currency": self.currency,
                "id": transaction_id
            }
        }

        if self.callback_url:
            payload["callback_url"] = self.callback_url

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    def collection_enquiry(self, transaction_id: str) -> Dict:
        """
        Check the status of a collection transaction

        Args:
            transaction_id: The transaction ID from the original payment request

        Returns:
            Transaction status response
        """
        if not self.ensure_authenticated():
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.base_url}/standard/v1/payments/{transaction_id}"

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    def refund(self, airtel_money_id: str) -> Dict:
        """
        Refund a completed collection transaction

        Args:
            airtel_money_id: The Airtel Money transaction ID to refund

        Returns:
            Refund response
        """
        if not self.ensure_authenticated():
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.base_url}/standard/v1/payments/refund"

        payload = {
            "airtel_money_id": airtel_money_id
        }

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}

    def disburse(
        self,
        msisdn: str,
        amount: float,
        reference: str,
        transaction_id: str,
        pin: str  # Encrypted PIN for disbursement
    ) -> Dict:
        """
        Send money to an Airtel Money subscriber (B2C)

        Args:
            msisdn: Recipient phone number
            amount: Amount to send
            reference: Transaction reference
            transaction_id: Unique transaction ID
            pin: Encrypted merchant PIN

        Returns:
            Disbursement response
        """
        if not self.ensure_authenticated():
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.base_url}/standard/v1/disbursements/"

        payload = {
            "payee": {
                "country": self.country,
                "currency": self.currency,
                "msisdn": msisdn
            },
            "transaction": {
                "amount": amount,
                "country": self.country,
                "currency": self.currency,
                "id": transaction_id,
                "ref": reference
            },
            "pin": pin
        }

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}


# Helper functions for airtime purchase flow
def generate_transaction_id() -> str:
    """Generate a unique transaction ID"""
    return f"TXN_{int(time.time() * 1000)}"


def format_phone_number(phone: str) -> str:
    """
    Format phone number to Airtel format (7XXXXXXXX)
    Accepts formats: 07XXXXXXXX, +2547XXXXXXXX, 2547XXXXXXXX
    """
    phone = phone.strip()
    phone = phone.replace("+", "").replace(" ", "")

    if phone.startswith("0"):
        return phone[1:]  # Remove leading 0
    elif phone.startswith("254"):
        return phone[3:]  # Remove country code
    else:
        return phone  # Assume already correct format


if __name__ == "__main__":
    # Example usage
    print("Airtel Money API Client")
    print("=" * 50)

    # Initialize client (use environment variables for credentials in production)
    client = AirtelMoneyClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        sandbox=True,
        callback_url="https://your-domain.com/webhook/airtel"
    )

    # Authenticate
    if client.authenticate():
        print("✓ Client authenticated successfully")

        # Example: USSD Push for airtime purchase
        print("\nExample: Initiating airtime purchase via USSD Push")
        transaction_id = generate_transaction_id()
        response = client.ussd_push(
            msisdn=format_phone_number("0712345678"),
            amount=100.0,
            reference="Airtime Purchase",
            transaction_id=transaction_id
        )
        print(f"Response: {json.dumps(response, indent=2)}")

        # Check transaction status
        print("\nChecking transaction status...")
        status = client.collection_enquiry(transaction_id)
        print(f"Status: {json.dumps(status, indent=2)}")
