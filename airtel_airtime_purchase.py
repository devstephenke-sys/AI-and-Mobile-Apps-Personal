"""
Airtel Airtime Purchase Module
Specific implementation for airtime top-up using Airtel Money API
"""

from airtel_api_client import AirtelMoneyClient, generate_transaction_id, format_phone_number
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AirtimePurchaseManager:
    """
    Manage airtime purchase transactions using Airtel Money
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        sandbox: bool = True,
        callback_url: Optional[str] = None
    ):
        """
        Initialize Airtime Purchase Manager

        Args:
            client_id: Airtel API client ID
            client_secret: Airtel API client secret
            sandbox: Use sandbox environment
            callback_url: Webhook URL for transaction callbacks
        """
        self.client = AirtelMoneyClient(
            client_id=client_id,
            client_secret=client_secret,
            country="KE",
            currency="KES",
            sandbox=sandbox,
            callback_url=callback_url
        )

        # Store pending transactions
        self.pending_transactions: Dict[str, Dict] = {}

    def purchase_airtime(
        self,
        phone_number: str,
        amount: float,
        recipient_phone: Optional[str] = None
    ) -> Dict:
        """
        Purchase airtime for a phone number

        Args:
            phone_number: Payer's Airtel Money phone number
            amount: Airtime amount in KES
            recipient_phone: Optional recipient phone number (if different from payer)
                             If None, airtime is purchased for the payer's number

        Returns:
            Transaction response
        """
        # Authenticate
        if not self.client.ensure_authenticated():
            return {
                "status": "error",
                "message": "Authentication failed"
            }

        # Format phone numbers
        payer_msisdn = format_phone_number(phone_number)
        recipient_msisdn = format_phone_number(recipient_phone) if recipient_phone else payer_msisdn

        # Generate transaction ID
        transaction_id = generate_transaction_id()

        # Create reference
        reference = f"Airtime for {recipient_msisdn}"

        logger.info(f"Initiating airtime purchase: {amount} KES for {recipient_msisdn}")
        logger.info(f"Transaction ID: {transaction_id}")

        # Store transaction details
        self.pending_transactions[transaction_id] = {
            "payer_msisdn": payer_msisdn,
            "recipient_msisdn": recipient_msisdn,
            "amount": amount,
            "status": "initiated",
            "timestamp": self._get_timestamp()
        }

        # Initiate USSD push payment
        response = self.client.ussd_push(
            msisdn=payer_msisdn,
            amount=amount,
            reference=reference,
            transaction_id=transaction_id
        )

        # Update transaction status
        if response.get("status") == "success":
            self.pending_transactions[transaction_id]["status"] = "ussd_pushed"
            self.pending_transactions[transaction_id]["response"] = response
        else:
            self.pending_transactions[transaction_id]["status"] = "failed"
            self.pending_transactions[transaction_id]["error"] = response.get("message")

        return {
            "transaction_id": transaction_id,
            "status": self.pending_transactions[transaction_id]["status"],
            "response": response
        }

    def check_airtime_purchase_status(self, transaction_id: str) -> Dict:
        """
        Check the status of an airtime purchase transaction

        Args:
            transaction_id: Transaction ID to check

        Returns:
            Transaction status
        """
        if not self.client.ensure_authenticated():
            return {
                "status": "error",
                "message": "Authentication failed"
            }

        logger.info(f"Checking status for transaction: {transaction_id}")

        # Query transaction status
        response = self.client.collection_enquiry(transaction_id)

        # Update local transaction record
        if transaction_id in self.pending_transactions:
            transaction_status = response.get("transaction", {}).get("status")

            if transaction_status == "TS":
                self.pending_transactions[transaction_id]["status"] = "completed"
            elif transaction_status == "TF":
                self.pending_transactions[transaction_id]["status"] = "failed"
            elif transaction_status == "TIP":
                self.pending_transactions[transaction_id]["status"] = "in_progress"

            self.pending_transactions[transaction_id]["latest_status"] = response

        return response

    def get_transaction_details(self, transaction_id: str) -> Optional[Dict]:
        """
        Get stored transaction details

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction details or None if not found
        """
        return self.pending_transactions.get(transaction_id)

    def get_all_transactions(self) -> Dict:
        """Get all stored transactions"""
        return self.pending_transactions

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Airtime Purchase API (Flask wrapper)
from flask import Flask, request, jsonify

app = Flask(__name__)

# Global purchase manager instance
purchase_manager: Optional[AirtimePurchaseManager] = None


def init_purchase_manager(client_id: str, client_secret: str, sandbox: bool = True):
    """Initialize the purchase manager"""
    global purchase_manager
    purchase_manager = AirtimePurchaseManager(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=sandbox
    )


@app.route('/api/airtime/purchase', methods=['POST'])
def api_purchase_airtime():
    """
    API endpoint to purchase airtime

    Request body:
    {
        "phone_number": "0712345678",
        "amount": 100.0,
        "recipient_phone": "0787654321"  // optional
    }
    """
    if not purchase_manager:
        return jsonify({
            "status": "error",
            "message": "Purchase manager not initialized"
        }), 500

    data = request.get_json()

    phone_number = data.get("phone_number")
    amount = data.get("amount")
    recipient_phone = data.get("recipient_phone")

    if not phone_number or not amount:
        return jsonify({
            "status": "error",
            "message": "phone_number and amount are required"
        }), 400

    try:
        result = purchase_manager.purchase_airtime(
            phone_number=phone_number,
            amount=amount,
            recipient_phone=recipient_phone
        )
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Airtime purchase error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/airtime/status/<transaction_id>', methods=['GET'])
def api_check_status(transaction_id: str):
    """API endpoint to check transaction status"""
    if not purchase_manager:
        return jsonify({
            "status": "error",
            "message": "Purchase manager not initialized"
        }), 500

    try:
        result = purchase_manager.check_airtime_purchase_status(transaction_id)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/airtime/transactions', methods=['GET'])
def api_get_transactions():
    """API endpoint to get all transactions"""
    if not purchase_manager:
        return jsonify({
            "status": "error",
            "message": "Purchase manager not initialized"
        }), 500

    return jsonify(purchase_manager.get_all_transactions())


if __name__ == "__main__":
    import os

    # Configuration from environment variables
    CLIENT_ID = os.getenv("AIRTEL_CLIENT_ID", "your_client_id")
    CLIENT_SECRET = os.getenv("AIRTEL_CLIENT_SECRET", "your_client_secret")
    SANDBOX = os.getenv("AIRTEL_SANDBOX", "true").lower() == "true"

    # Initialize purchase manager
    init_purchase_manager(CLIENT_ID, CLIENT_SECRET, SANDBOX)

    # Run API server
    PORT = int(os.getenv("API_PORT", "5001"))
    print(f"Starting Airtime Purchase API on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
