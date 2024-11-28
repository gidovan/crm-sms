from sms import send_sms, unique_text
# from app_ori import get_all_db_client, total_number_clients, get_all_schedule_event
from datetime import datetime, timedelta, date, time
import pytz
import time
import threading
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Define your database connection URI
DATABASE_URI = os.getenv("DATABASE_URI")


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
            sliced_data = nipa[0:7]
            obia.add(tuple(sliced_data))
    return list(list(nipa_baku) for nipa_baku in obia)


def get_all_db_client(insurance_investment):
    query = text(f"SELECT id, fname, lname, prim_phone, busi_phone, cell_phone, dob FROM {insurance_investment}")
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
            client_name = f"{client[1]} {client[2]}"
            email_message = (
                f"Je te souhaite une bonne fête, {client_name} 🎉.\n\n"
                "Que cette journée spéciale soit remplie de joie, de succès, et de beaux moments à partager avec tes proches.\n\n"
                "Joyeux anniversaire !\n\n"
                "Jean Kokou\n"
                "Votre Conseiller Financier\n"
                "IA Groupe\n\n"
                "Kokoujean.kpomegbe@agc.ia.ca\n"
                "514 793 3114"
            )

            dob = client[-1]
            if dob.strftime('%Y-%m-%d') == '1900-01-01':
                pass
            else:
                if dob.month == today.month and dob.day == today.day:
                    if client[3]:
                        if '_' in client[3]:
                            send_sms(f"+1{client[3].replace('-', "")}", email_message)
                        else:
                            send_sms(client[3], email_message)
                    else:
                        if '_' in client[5]:
                            send_sms(f"+1{client[5].replace('-', "")}", email_message)
                        else:
                            send_sms(client[5], email_message)
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
                else:
                    recipients = total_number_clients()
                for recipient in recipients:
                    message = unique_text(event[3], f"{recipient[1]} {recipient[2]}".strip())
                    if recipient[3]:
                        if '-' in recipient[3]:
                            send_sms(f"+1{recipient[3].replace('-', "")}", message)
                        else:
                            send_sms(f"{recipient[3]}", message)
                    else:
                        if '-' in recipient[5]:
                            send_sms(f"+1{recipient[5].replace('-', "")}", message)
                        else:
                            send_sms(f"{recipient[5]}", message)
        time.sleep(86400)


bck_proces1 = threading.Thread(target=wish_happy_birthday)
bck_proces2 = threading.Thread(target=event_executor)

bck_proces1.start()
bck_proces2.start()

bck_proces1.join()
bck_proces2.join()

#
# if __name__ == "__Main__":
#     bck_proces1 = threading.Thread(target=wish_happy_birthday)
#     bck_proces2 = threading.Thread(target=event_executor)
#
#     bck_proces1.start()
#     bck_proces2.start()
#
#     bck_proces1.join()
#     bck_proces2.join()
