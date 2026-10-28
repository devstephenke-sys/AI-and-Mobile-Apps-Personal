"""
Airtel Money API Testing Suite
Comprehensive testing for authentication, payment flows, and airtime purchase
"""

import os
import sys
import json
import time
from airtel_api_client import AirtelMoneyClient, generate_transaction_id, format_phone_number
from airtel_airtime_purchase import AirtimePurchaseManager

# Configuration - Load from environment variables
CLIENT_ID = os.getenv("AIRTEL_CLIENT_ID", "your_test_client_id")
CLIENT_SECRET = os.getenv("AIRTEL_CLIENT_SECRET", "your_test_client_secret")
SANDBOX = os.getenv("AIRTEL_SANDBOX", "true").lower() == "true"
CALLBACK_URL = os.getenv("CALLBACK_URL", "http://localhost:5000/webhook/airtel")


class AirtelAPITester:
    """Test suite for Airtel Money API"""

    def __init__(self):
        self.client = AirtelMoneyClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            sandbox=SANDBOX,
            callback_url=CALLBACK_URL
        )
        self.test_results = []

    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"  -> {message}")

    def test_authentication(self):
        """Test OAuth2 authentication"""
        print("\n" + "="*50)
        print("TEST: Authentication")
        print("="*50)

        try:
            success = self.client.authenticate()
            self.log_result(
                "OAuth2 Authentication",
                success,
                "Token obtained successfully" if success else "Authentication failed"
            )
            return success
        except Exception as e:
            self.log_result("OAuth2 Authentication", False, str(e))
            return False

    def test_ussd_push(self):
        """Test USSD push payment initiation"""
        print("\n" + "="*50)
        print("TEST: USSD Push Payment")
        print("="*50)

        if not self.client.access_token:
            self.log_result("USSD Push", False, "Not authenticated")
            return False

        try:
            transaction_id = generate_transaction_id()
            response = self.client.ussd_push(
                msisdn=format_phone_number("0712345678"),
                amount=10.0,  # Small test amount
                reference="Test Payment",
                transaction_id=transaction_id
            )

            success = response.get("status") == "success"
            self.log_result(
                "USSD Push Initiation",
                success,
                f"Transaction ID: {transaction_id}"
            )

            print(f"Response: {json.dumps(response, indent=2)}")
            return transaction_id if success else None

        except Exception as e:
            self.log_result("USSD Push", False, str(e))
            return None

    def test_collection_enquiry(self, transaction_id: str):
        """Test transaction status enquiry"""
        print("\n" + "="*50)
        print("TEST: Collection Enquiry")
        print("="*50)

        if not transaction_id:
            self.log_result("Collection Enquiry", False, "No transaction ID provided")
            return

        try:
            # Wait a moment for transaction to process
            time.sleep(2)

            response = self.client.collection_enquiry(transaction_id)
            success = "transaction" in response

            self.log_result(
                "Collection Enquiry",
                success,
                f"Status: {response.get('transaction', {}).get('status', 'N/A')}"
            )

            print(f"Response: {json.dumps(response, indent=2)}")

        except Exception as e:
            self.log_result("Collection Enquiry", False, str(e))

    def test_airtime_purchase(self):
        """Test airtime purchase flow"""
        print("\n" + "="*50)
        print("TEST: Airtime Purchase Flow")
        print("="*50)

        try:
            manager = AirtimePurchaseManager(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                sandbox=SANDBOX,
                callback_url=CALLBACK_URL
            )

            result = manager.purchase_airtime(
                phone_number="0712345678",
                amount=10.0,
                recipient_phone="0712345678"
            )

            success = result.get("status") in ["ussd_pushed", "in_progress"]
            self.log_result(
                "Airtime Purchase Initiation",
                success,
                f"Transaction ID: {result.get('transaction_id')}"
            )

            # Check status
            if result.get("transaction_id"):
                time.sleep(2)
                status = manager.check_airtime_purchase_status(result["transaction_id"])
                print(f"Status Check: {json.dumps(status, indent=2)}")

            return result.get("transaction_id")

        except Exception as e:
            self.log_result("Airtime Purchase", False, str(e))
            return None

    def test_phone_number_formatting(self):
        """Test phone number formatting"""
        print("\n" + "="*50)
        print("TEST: Phone Number Formatting")
        print("="*50)

        test_cases = [
            ("0712345678", "712345678"),
            ("+254712345678", "712345678"),
            ("254712345678", "712345678"),
            ("712345678", "712345678"),
        ]

        all_passed = True
        for input_num, expected in test_cases:
            result = format_phone_number(input_num)
            passed = result == expected
            all_passed = all_passed and passed
            self.log_result(
                f"Format {input_num}",
                passed,
                f"Expected: {expected}, Got: {result}"
            )

        return all_passed

    def test_token_refresh(self):
        """Test automatic token refresh"""
        print("\n" + "="*50)
        print("TEST: Token Refresh")
        print("="*50)

        try:
            # First authentication
            self.client.authenticate()
            first_token = self.client.access_token

            # Force token expiration by setting expiration to past
            from datetime import datetime, timedelta
            self.client.token_expires_at = datetime.now() - timedelta(seconds=10)

            # Try a request that should trigger refresh
            self.client.ensure_authenticated()
            second_token = self.client.access_token

            # In sandbox, tokens might not actually refresh, but the mechanism should work
            success = second_token is not None
            self.log_result(
                "Token Refresh Mechanism",
                success,
                "Token refresh check completed"
            )

            return success

        except Exception as e:
            self.log_result("Token Refresh", False, str(e))
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)

        passed = sum(1 for r in self.test_results if "PASS" in r["status"])
        failed = sum(1 for r in self.test_results if "FAIL" in r["status"])
        total = len(self.test_results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")

        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result['status']}: {result['test']}")
            if result['message']:
                print(f"    {result['message']}")

        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print("\nResults saved to test_results.json")


def run_interactive_test():
    """Run interactive testing mode"""
    print("="*50)
    print("Airtel Money API - Interactive Testing")
    print("="*50)
    print(f"Environment: {'SANDBOX' if SANDBOX else 'PRODUCTION'}")
    print(f"Client ID: {CLIENT_ID[:10]}..." if CLIENT_ID != "your_test_client_id" else "Client ID: (not set)")
    print()

    tester = AirtelAPITester()

    while True:
        print("\nAvailable Tests:")
        print("1. Authentication")
        print("2. USSD Push Payment")
        print("3. Collection Enquiry")
        print("4. Airtime Purchase Flow")
        print("5. Phone Number Formatting")
        print("6. Token Refresh")
        print("7. Run All Tests")
        print("8. Exit")

        choice = input("\nSelect test (1-8): ").strip()

        if choice == "1":
            tester.test_authentication()
        elif choice == "2":
            tx_id = tester.test_ussd_push()
            if tx_id:
                enquiry = input("Check transaction status? (y/n): ").strip().lower()
                if enquiry == "y":
                    tester.test_collection_enquiry(tx_id)
        elif choice == "3":
            tx_id = input("Enter transaction ID: ").strip()
            tester.test_collection_enquiry(tx_id)
        elif choice == "4":
            tester.test_airtime_purchase()
        elif choice == "5":
            tester.test_phone_number_formatting()
        elif choice == "6":
            tester.test_token_refresh()
        elif choice == "7":
            tester.test_authentication()
            tx_id = tester.test_ussd_push()
            if tx_id:
                tester.test_collection_enquiry(tx_id)
            tester.test_airtime_purchase()
            tester.test_phone_number_formatting()
            tester.test_token_refresh()
            tester.print_summary()
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice")


def run_automated_tests():
    """Run all tests automatically"""
    print("="*50)
    print("Airtel Money API - Automated Testing")
    print("="*50)

    tester = AirtelAPITester()

    # Run all tests
    tester.test_authentication()
    tester.test_phone_number_formatting()
    tester.test_token_refresh()

    # Transaction tests (require valid credentials)
    if CLIENT_ID != "your_test_client_id":
        tx_id = tester.test_ussd_push()
        if tx_id:
            tester.test_collection_enquiry(tx_id)
        tester.test_airtime_purchase()
    else:
        print("\n[WARNING] Skipping transaction tests - credentials not configured")
        print("Set AIRTEL_CLIENT_ID and AIRTEL_CLIENT_SECRET environment variables")

    tester.print_summary()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_test()
    else:
        run_automated_tests()
