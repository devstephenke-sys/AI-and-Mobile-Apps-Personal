# Airtel Money API Integration

Complete implementation for Airtel Money API integration including authentication, payment flows, webhooks, and airtime purchase functionality.

## Overview

This integration provides:
- ✅ OAuth2 authentication with automatic token refresh
- ✅ USSD push payment collection
- ✅ Payment disbursement (B2C)
- ✅ Transaction status enquiries
- ✅ Refund processing
- ✅ Webhook server for transaction callbacks
- ✅ Airtime purchase specific implementation
- ✅ Comprehensive testing suite

## Documentation

Official Airtel Developer Portal: https://developers.airtel.africa/docs

## Prerequisites

1. **Airtel Developer Account**
   - Register at https://developers.airtel.africa/developer
   - Create an application
   - Get your `client_id` and `client_secret`

2. **Python 3.8+**
   ```bash
   python --version
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```env
   AIRTEL_CLIENT_ID=your_actual_client_id
   AIRTEL_CLIENT_SECRET=your_actual_client_secret
   AIRTEL_SANDBOX=true
   CALLBACK_URL=https://your-domain.com/webhook/airtel
   ```

## Components

### 1. API Client (`airtel_api_client.py`)

Core client for interacting with Airtel Money API.

#### Usage Example

```python
from airtel_api_client import AirtelMoneyClient

# Initialize client
client = AirtelMoneyClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    sandbox=True,
    callback_url="https://your-domain.com/webhook/airtel"
)

# Authenticate
client.authenticate()

# USSD Push for payment collection
response = client.ussd_push(
    msisdn="712345678",
    amount=100.0,
    reference="Invoice payment",
    transaction_id="TXN_1234567890"
)

# Check transaction status
status = client.collection_enquiry("TXN_1234567890")

# Refund transaction
refund = client.refund("airtel_money_id")
```

### 2. Webhook Server (`airtel_webhook_server.py`)

Flask server to handle transaction status callbacks.

#### Running the Webhook Server

```bash
python airtel_webhook_server.py
```

The server will listen on:
- **Webhook endpoint**: `http://localhost:5000/webhook/airtel`
- **Health check**: `http://localhost:5000/webhook/airtel/health`
- **Transaction history**: `http://localhost:5000/webhook/airtel/transactions`

#### Webhook Response Handling

The webhook processes callbacks with status codes:
- `TS` = Transaction Success
- `TF` = Transaction Failed
- `TIP` = Transaction In Progress

### 3. Airtime Purchase Module (`airtel_airtime_purchase.py`)

Specialized module for airtime top-up transactions.

#### Standalone Usage

```python
from airtel_airtime_purchase import AirtimePurchaseManager

manager = AirtimePurchaseManager(
    client_id="your_client_id",
    client_secret="your_client_secret",
    sandbox=True
)

# Purchase airtime
result = manager.purchase_airtime(
    phone_number="0712345678",
    amount=100.0,
    recipient_phone="0787654321"  # Optional
)

# Check status
status = manager.check_airtime_purchase_status(result["transaction_id"])
```

#### API Server Mode

```bash
python airtel_airtime_purchase.py
```

API Endpoints:
- `POST /api/airtime/purchase` - Purchase airtime
- `GET /api/airtime/status/<transaction_id>` - Check transaction status
- `GET /api/airtime/transactions` - Get all transactions

#### API Example

```bash
# Purchase airtime
curl -X POST http://localhost:5001/api/airtime/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "0712345678",
    "amount": 100.0,
    "recipient_phone": "0787654321"
  }'

# Check status
curl http://localhost:5001/api/airtime/status/TXN_1234567890
```

### 4. Testing Suite (`test_airtel_api.py`)

Comprehensive testing for all components.

#### Run Automated Tests

```bash
python test_airtel_api.py
```

#### Run Interactive Tests

```bash
python test_airtel_api.py --interactive
```

## Airtime Purchase Flow

### Complete Transaction Flow

```
1. User initiates airtime purchase
   ↓
2. System generates transaction ID
   ↓
3. OAuth2 authentication (token obtained)
   ↓
4. USSD Push sent to payer's phone
   ↓
5. User confirms USSD prompt on phone
   ↓
6. Airtel processes transaction
   ↓
7. Webhook callback sent to your server
   ↓
8. Transaction status updated
   ↓
9. Airtime credited to recipient
```

### Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `initiated` | Transaction created | Waiting for USSD push |
| `ussd_pushed` | USSD sent to user | Waiting for user confirmation |
| `in_progress` / `TIP` | Processing | Wait for final status |
| `completed` / `TS` | Success | Airtime credited |
| `failed` / `TF` | Failed | Notify user, possibly retry |

## Security Best Practices

1. **Credential Management**
   - Never commit `.env` file to version control
   - Use environment variables in production
   - Rotate credentials regularly

2. **Webhook Security**
   - Implement signature verification (HMAC)
   - Use HTTPS for webhook URLs
   - Validate all incoming requests

3. **API Security**
   - Use separate sandbox and production credentials
   - Implement rate limiting
   - Log all API calls for audit

4. **Transaction Security**
   - Never store PINs in plain text
   - Use encryption for sensitive data
   - Implement idempotency for transaction retries

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AIRTEL_CLIENT_ID` | API client ID | Yes | - |
| `AIRTEL_CLIENT_SECRET` | API client secret | Yes | - |
| `AIRTEL_SANDBOX` | Use sandbox environment | No | `true` |
| `AIRTEL_COUNTRY` | Country code | No | `KE` |
| `AIRTEL_CURRENCY` | Currency code | No | `KES` |
| `CALLBACK_URL` | Webhook URL | No | - |
| `WEBHOOK_HOST` | Webhook server host | No | `0.0.0.0` |
| `WEBHOOK_PORT` | Webhook server port | No | `5000` |
| `API_PORT` | API server port | No | `5001` |

## API Endpoints Reference

### Authentication
- **POST** `/auth/oauth2/token` - Get access token

### Payments
- **POST** `/merchant/v1/payments/` - USSD push payment
- **GET** `/standard/v1/payments/{id}` - Check transaction status
- **POST** `/standard/v1/payments/refund` - Refund transaction

### Disbursements
- **POST** `/standard/v1/disbursements/` - Send money (B2C)

## Troubleshooting

### Authentication Failed
- Verify client_id and client_secret are correct
- Check if using sandbox vs production credentials
- Ensure token hasn't expired (tokens expire in 180 seconds)

### USSD Push Not Received
- Verify phone number format (7XXXXXXXX for Kenya)
- Check if user has sufficient balance
- Ensure phone number is registered with Airtel Money

### Webhook Not Receiving Callbacks
- Verify CALLBACK_URL is publicly accessible
- Check firewall settings
- Ensure webhook server is running
- Test with webhook testing tools (e.g., webhook.site)

### Transaction Stuck in Progress
- Wait longer (transactions can take up to 2 minutes)
- Use collection enquiry to check status
- Check Airtel system status
- Contact Airtel support if persistent

## Development Workflow

1. **Setup Development Environment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Configure environment
   cp .env.example .env
   # Edit .env with sandbox credentials
   ```

2. **Run Tests**
   ```bash
   # Automated tests
   python test_airtel_api.py

   # Interactive testing
   python test_airtel_api.py --interactive
   ```

3. **Start Webhook Server**
   ```bash
   python airtel_webhook_server.py
   ```

4. **Start API Server** (optional)
   ```bash
   python airtel_airtime_purchase.py
   ```

5. **Test Integration**
   - Use the testing suite
   - Monitor webhook server logs
   - Check transaction status via API

## Production Deployment

1. **Use Production Credentials**
   ```env
   AIRTEL_SANDBOX=false
   AIRTEL_CLIENT_ID=production_client_id
   AIRTEL_CLIENT_SECRET=production_client_secret
   ```

2. **Use HTTPS**
   - Configure SSL/TLS certificates
   - Use HTTPS for all endpoints

3. **Implement Rate Limiting**
   - Add rate limiting middleware
   - Monitor API usage

4. **Database Integration**
   - Replace in-memory transaction storage with database
   - Implement proper transaction logging

5. **Monitoring**
   - Set up application monitoring
   - Configure alerting for failed transactions
   - Monitor webhook delivery rates

## Support

- **Airtel Developer Portal**: https://developers.airtel.africa/docs
- **API Documentation**: https://developers.airtelkenya.com/documentation
- **Support Email**: developer-support@airtel.com

## License

This integration is provided as-is for legitimate development purposes. Ensure compliance with Airtel's terms of service and applicable regulations.

## Important Notes

- This is a legitimate API integration for authorized developers
- Requires valid credentials from Airtel Developer Portal
- All transactions are processed through Airtel's official servers
- No simulation or bypass of payment systems
- Use only for authorized business purposes
