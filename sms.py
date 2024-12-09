from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from twilio.rest import Client
import detectlanguage
import os


load_dotenv()
acc_sid = os.getenv("ACC_SID")
authen_token = os.getenv("AUTHEN_TOKEN")
acc_number = os.getenv("ACC_NUMBER")


# Text body translator
def message_translator(message, tar_lang):
    detectlanguage.configuration.api_key = os.getenv('LANG_DETECT')
    detct_lang = detectlanguage.simple_detect(message)
    if detct_lang == tar_lang:
        return message
    else:
        translated_txt = GoogleTranslator(source='auto', target=tar_lang).translate(message)
        return translated_txt


def send_sms(recipient_number, sms_txt, targ_lang):
    recipient_number = str(recipient_number)
    try:
        if recipient_number and len(recipient_number) >= 12:
            account_sid = acc_sid
            auth_token = authen_token
            client = Client(account_sid, auth_token)
            trnslated_txt = message_translator(sms_txt, targ_lang)
            # Send an SMS
            if '-' in recipient_number:
                recipient_number = f"+1{recipient_number.replace('-', "")}"
            message = client.messages.create(
                body=str(trnslated_txt),
                from_=acc_number,  # twilio number
                to=recipient_number  # The recipient's phone number
            )
            return f"Message sent: {message.sid}"
    except Exception as error:
        print(error)


def unique_text(message, value):
    if '{}' in str(message):
        return message.format(str(value))
    else:
        return message

# if __name__ == "__main__":
#     for name, number in contacts.items():
#         messages = unique_text("{} Good morning,  hope you're doing well", name)
#         send_sms(number, messages)
