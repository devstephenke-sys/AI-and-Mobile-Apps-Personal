"""
Airtel Money Webhook Server
Handles transaction status callbacks from Airtel API
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
from typing import Dict, List
import threading
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage for transactions (use database in production)
transactions: Dict[str, Dict] = {}


class WebhookHandler:
    """Handle Airtel Money webhook callbacks"""

    @staticmethod
    def validate_signature(payload: str, signature: str) -> bool:
        """
        Validate webhook signature
        In production, implement signature verification using shared secret
        """
        # TODO: Implement HMAC signature verification
        return True

    @staticmethod
    def process_payment_callback(data: Dict) -> Dict:
        """
        Process payment status callback

        Status codes:
        - TS: Success
        - TF: Failed
        - TIP: In Progress
        """
        transaction_id = data.get("transaction", {}).get("id")
        status = data.get("transaction", {}).get("status")
        message = data.get("transaction", {}).get("message")

        logger.info(f"Payment callback received - Transaction: {transaction_id}, Status: {status}")

        # Store transaction status
        transactions[transaction_id] = {
            "status": status,
            "message": message,
            "callback_data": data,
            "timestamp": datetime.now().isoformat()
        }

        # Process based on status
        if status == "TS":
            logger.info(f"✓ Transaction {transaction_id} completed successfully")
            # Trigger success actions (update database, send confirmation, etc.)
        elif status == "TF":
            logger.error(f"✗ Transaction {transaction_id} failed: {message}")
            # Trigger failure actions (notify user, retry logic, etc.)
        elif status == "TIP":
            logger.info(f"⟳ Transaction {transaction_id} in progress")
            # Wait for next callback or poll for status

        return {"status": "success", "message": "Callback processed"}

    @staticmethod
    def process_disbursement_callback(data: Dict) -> Dict:
        """Process disbursement callback"""
        transaction_id = data.get("transaction", {}).get("id")
        status = data.get("transaction", {}).get("status")

        logger.info(f"Disbursement callback received - Transaction: {transaction_id}, Status: {status}")

        transactions[transaction_id] = {
            "type": "disbursement",
            "status": status,
            "callback_data": data,
            "timestamp": datetime.now().isoformat()
        }

        return {"status": "success", "message": "Disbursement callback processed"}


@app.route('/webhook/airtel', methods=['POST'])
def airtel_webhook():
    """
    Main webhook endpoint for Airtel Money callbacks
    """
    try:
        # Get raw payload for signature verification
        payload = request.get_data(as_text=True)
        signature = request.headers.get('X-Airtel-Signature', '')

        # Validate signature (in production)
        if not WebhookHandler.validate_signature(payload, signature):
            logger.warning("Invalid webhook signature")
            return jsonify({"status": "error", "message": "Invalid signature"}), 401

        # Parse JSON data
        data = request.get_json()

        if not data:
            logger.error("Empty webhook payload")
            return jsonify({"status": "error", "message": "Empty payload"}), 400

        # Determine callback type and process
        if "transaction" in data:
            response = WebhookHandler.process_payment_callback(data)
        else:
            response = WebhookHandler.process_disbursement_callback(data)

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/webhook/airtel/health', methods=['GET'])
def webhook_health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "transactions_stored": len(transactions)
    })


@app.route('/webhook/airtel/transactions', methods=['GET'])
def get_transactions():
    """Get all stored transactions (for monitoring/testing)"""
    return jsonify({
        "count": len(transactions),
        "transactions": transactions
    })


@app.route('/webhook/airtel/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id: str):
    """Get specific transaction status"""
    if transaction_id in transactions:
        return jsonify(transactions[transaction_id])
    else:
        return jsonify({"status": "error", "message": "Transaction not found"}), 404


def run_webhook_server(host: str = "0.0.0.0", port: int = 5000):
    """
    Run the webhook server

    Args:
        host: Host to bind to
        port: Port to listen on
    """
    logger.info(f"Starting webhook server on {host}:{port}")
    logger.info(f"Webhook URL: http://{host}:{port}/webhook/airtel")

    # Run Flask app
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    # Environment variables for configuration
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5000"))

    run_webhook_server(host=WEBHOOK_HOST, port=WEBHOOK_PORT)
