import requests
import base64
import datetime
from requests.auth  import HTTPBasicAuth
def mpesa_payment(amount, phone):
        # GENERATING THE ACCESS TOKEN
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"
 
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
 
        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']
 
        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')
 
        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }
 
        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }
 
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL
 
        response = requests.post(url, json=payload, headers=headers)
        print(response.text)







