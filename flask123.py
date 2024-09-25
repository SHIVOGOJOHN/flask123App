from flask import Flask, request, jsonify
import logging
import os

app = Flask(__name__)

# --- Configure Logging ---
logging.basicConfig(filename="mpesa_transactions.log", level=logging.INFO)

# --- Endpoint for STK Push Callback (Deposits) ---
@app.route('/stk_callback', methods=['POST'])
def stk_callback():
    data = request.json
    logging.info(f"STK Push Callback Received: {data}")
    
    # Extract and process the callback data
    result_code = data['Body']['stkCallback']['ResultCode']
    result_desc = data['Body']['stkCallback']['ResultDesc']
    merchant_request_id = data['Body']['stkCallback']['MerchantRequestID']
    checkout_request_id = data['Body']['stkCallback']['CheckoutRequestID']
    
    if result_code == 0:
        # Transaction was successful
        amount = data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        phone_number = data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']
        transaction_id = data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        logging.info(f"STK Push Successful: {amount} deposited by {phone_number}, Transaction ID: {transaction_id}")
        
        # You can update the user's balance here in your database
        # Example: update_user_balance(phone_number, amount)
    else:
        # Transaction failed
        logging.error(f"STK Push Failed: {result_desc}, MerchantRequestID: {merchant_request_id}")

    # Return success response to Safaricom
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

# --- Endpoint for B2C Callback (Withdrawals) ---
@app.route('/b2c_callback', methods=['POST'])
def b2c_callback():
    data = request.json
    logging.info(f"B2C Callback Received: {data}")
    
    # Extract and process the callback data
    result_code = data['Result']['ResultCode']
    result_desc = data['Result']['ResultDesc']
    conversation_id = data['Result']['ConversationID']
    originator_conversation_id = data['Result']['OriginatorConversationID']

    if result_code == 0:
        # Transaction was successful
        amount = data['Result']['ResultParameters']['ResultParameter'][1]['Value']
        phone_number = data['Result']['ResultParameters']['ResultParameter'][4]['Value']
        transaction_id = data['Result']['ResultParameters']['ResultParameter'][0]['Value']
        logging.info(f"B2C Successful: {amount} sent to {phone_number}, Transaction ID: {transaction_id}")
        
        # Update the user's withdrawal status in the database
        # Example: mark_withdrawal_successful(phone_number, amount)
    else:
        # Transaction failed
        logging.error(f"B2C Failed: {result_desc}, ConversationID: {conversation_id}")

    # Return success response to Safaricom
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

# --- Timeout Handlers ---
@app.route('/timeout', methods=['POST'])
def timeout():
    data = request.json
    logging.error(f"Timeout Error: {data}")
    
    # Process the timeout here
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200

if __name__ == "__main__":
    # Set host to '0.0.0.0' and port to environment variable or 5000 for local testing
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

