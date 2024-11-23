import os
from twilio.rest import Client
import os
from dotenv import load_dotenv
import json

with open("contacts.json", "r") as file:
    contacts = json.load(file)



load_dotenv()
acc_sid = os.getenv("ACC_SID")
authen_token = os.getenv("AUTHEN_TOKEN")
acc_number = os.getenv("ACC_NUMBER")



def send_sms(number, sentence):
    try:
        if number and len(number) >= 12:
            account_sid = acc_sid
            auth_token = authen_token
            client = Client(account_sid, auth_token)
            # Send an SMS
            message = client.messages.create(
                body=str(sentence),
                from_=acc_number,  # Your twilio number
                to=str(number)  # The recipient's phone number
            )
            return f"Message sent: {message.sid}"
    except Exception as error:
        print(error)


def unique_text(message, value):
    if '{}' in str(message):
        return message.format(str(value))
    else:
        pass


if __name__ == "__main__":
    for name, number in contacts.items():
        messages = unique_text("{} Good morning, i hope you're doing well", name)
        send_sms(number, messages)
