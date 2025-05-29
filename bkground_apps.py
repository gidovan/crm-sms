from datetime import datetime, timedelta, date, time
from sqlalchemy import create_engine, text
from sms import send_sms, unique_text
from dotenv import load_dotenv
import threading
import time
import pytz
import os

load_dotenv()

# Define your database connection URI
DATABASE_URI = os.getenv("DATABASE_URI")

#Signatures
SIGN_NAME = os.getenv()
SIGN_EMAIL = os.getenv()
SIGN_PHONE = os.getenv()


# Initializing SQLAlchemy engine
def init_connection():
    return create_engine(DATABASE_URI)


# DATABASE CONNECTION OBJECT
engine = init_connection()


def total_number_clients():
    obia = set()
    okpoloei = ['insurance_client', 'investment_client']
    for okpolo in okpoloei:
        total = get_all_db_client(okpolo)
        for nipa in total:
            sliced_data = nipa[1:8]
            obia.add(tuple(sliced_data))
    return list(list(nipa_baku) for nipa_baku in obia)


def get_all_db_client(insurance_investment):
    query = text(
        f"SELECT id, fname, lname, prim_phone, busi_phone, cell_phone, dob, language FROM {insurance_investment}")
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            all_client = result.fetchall()
            # Convert nested tuples to lists
            all_client = [list(client_info) for client_info in all_client]
            all_client.sort(key=lambda clients: clients[1])  # Sorting using the first name of each client
            return all_client
    except Exception as errors:
        return errors


def get_all_schedule_event():
    query = text("SELECT id, date, group_client, message FROM scheduled_event")
    try:
        with engine.connect() as conn:
            results = conn.execute(query)
            all_schedules = results.fetchall()
            return [list(item) for item in all_schedules]
    except Exception as error:
        print(error)


# iterate through an array of dobs in db if dob == today action
def wish_happy_birthday():
    while True:
        # Getting today's date in Quebec Montreal timezone
        montreal_tz = pytz.timezone("America/Montreal")
        today = datetime.now(montreal_tz).date()  # Getting date only
        client_list = total_number_clients()
        for client in client_list:
            client_name = f"{client[0]} {client[1]}"
            sms_message = (
                f"Je te souhaite une bonne fête, {client_name} 🎉.\n\n"
                "Que cette journée spéciale soit remplie de joie, de succès, et de beaux moments à partager avec tes "
                "proches.\n\n"
                "Joyeux anniversaire !\n\n"
                f"{SIGN_NAME}\n"
                "Votre Conseiller Financier\n"
                "IA Groupe\n\n"
                f"📧 {SIGN_EMAIL}\n"
                f"📞 {SIGN_PHONE}"
            )

            dob = client[-2]
            if dob.strftime('%Y-%m-%d') == '1900-01-01':
                pass
            else:
                if dob.month == today.month and dob.day == today.day:
                    if client[2]:
                        if '_' in client[2]:
                            send_sms(f"+1{client[2].replace('-', "")}", sms_message, client[-1])
                        else:
                            send_sms(client[2], sms_message, client[-1])
                    else:
                        if '_' in client[4]:
                            send_sms(f"+1{client[4].replace('-', "")}", sms_message, client[-1])
                        else:
                            send_sms(client[4], sms_message, client[-1])
        time.sleep(86400)


# Scheduler Event executor
def event_executor():
    while True:
        montreal_tyzone = pytz.timezone("America/Montreal")
        today = datetime.now(montreal_tyzone).date()
        list_of_schedules = get_all_schedule_event()
        for event in list_of_schedules:
            event_date = datetime.strptime(event[1], '%Y-%m-%d').date()
            if event_date == today:
                if event[2] in ("insurance_client", "investment_client", "insuran_client_test", "invst_client_test"):
                    recipients = get_all_db_client(event[2])
                    for recipient in recipients:
                        message = unique_text(event[3], f"{recipient[1]} {recipient[2]}".strip())
                        if recipient[3]:
                            if '-' in recipient[3]:
                                send_sms(f"+1{recipient[3].replace('-', "")}", message, recipient[-1])
                            else:
                                send_sms(f"{recipient[3]}", message, recipient[-1])
                        else:
                            if '-' in recipient[5]:
                                send_sms(f"+1{recipient[5].replace('-', "")}", message, recipient[-1])
                            else:
                                send_sms(f"{recipient[5]}", message, recipient[-1])
                else:
                    recipients = total_number_clients()
                    for recipient in recipients:
                        message = unique_text(event[3], f"{recipient[0]} {recipient[1]}".strip())
                        if recipient[2]:
                            if '-' in recipient[2]:
                                send_sms(f"+1{recipient[2].replace('-', "")}", message, recipient[-1])
                            else:
                                send_sms(f"{recipient[2]}", message, recipient[-1])
                        else:
                            if '-' in recipient[4]:
                                send_sms(f"+1{recipient[4].replace('-', "")}", message, recipient[-1])
                            else:
                                send_sms(f"{recipient[4]}", message, recipient[-1])

        time.sleep(86400)


if __name__ == "__main__":
    bck_proces1 = threading.Thread(target=wish_happy_birthday)
    bck_proces2 = threading.Thread(target=event_executor)

    bck_proces1.start()
    bck_proces2.start()

    bck_proces1.join()
    bck_proces2.join()
