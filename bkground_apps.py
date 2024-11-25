from sms import send_sms, unique_text
from app import get_all_db_client, total_number_clients, get_all_schedule_event
from datetime import datetime, timedelta, date, time
import pytz


# iterate through an array of dobs in db if dob == today action
def wish_happy_birthday():
    # Getting today's date in Quebec Montreal timezone
    montreal_tz = pytz.timezone("America/Montreal")
    today = datetime.now(montreal_tz).date()  # Getting date only
    client_list = get_all_db_client("invst_client_test")
    for client in client_list:
        client_name = f"{client[1]} {client[2]}"
        email_message = (f"Happy Birthday, {client_name}! 🎉 Wishing you a wonderful birthday and a fantastic year "
                         f"ahead. Thank you for trusting iA Financial Group to be part of your journey. \nMr. Jean, "
                         f"iA Financial Group")
        dob = client[-1]
        if isinstance(dob, date) and dob.month == today.month and dob.day == today.day:
            send_sms(client[3], email_message)
            # print(f"Happy Birthday, {client[1]} {client[2]}!")  # Using first and last name


# Scheduler Event executor
def event_executor():
    montreal_tyzone = pytz.timezone("America/Montreal")
    today = datetime.now(montreal_tyzone).date()
    list_of_schedules = get_all_schedule_event()
    for event in list_of_schedules:
        event_date = datetime.strptime(event[1], '%Y-%m-%d').date()
        if event_date == today:
            if event[2] in ("insurance_client", "investment_client", "insuran_client_test"):
                recipients = get_all_db_client(event[2])
            else:
                recipients = total_number_clients()
            for recipient in recipients:
                message = unique_text(event(3), f"{recipient[1]} {recipient[2]}".strip())
                if '-' in recipient[3]:
                    send_sms(f"+1{recipient[3].replace('-', "")}", message)
                else:
                    send_sms(f"{recipient[3]}", message)







