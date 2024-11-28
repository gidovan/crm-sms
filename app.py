import streamlit as st
from sqlalchemy import create_engine, text
import time
import datetime
from datetime import date
from sms import send_sms, unique_text
import os
from dotenv import load_dotenv
from bkground_apps import total_number_clients, get_all_schedule_event, get_all_db_client

load_dotenv()

# Define your database connection URI
DATABASE_URI = os.getenv("DATABASE_URI")


# Initializing SQLAlchemy engine
def init_connection():
    return create_engine(DATABASE_URI)


# DATABASE CONNECTION OBJECT
engine = init_connection()


# Retrieves total number of clients from db
# def total_number_clients():
#     obia = set()
#     okpoloei = ['insurance_client', 'investment_client']
#     for okpolo in okpoloei:
#         total = get_all_db_client(okpolo)
#         for nipa in total:
#             sliced_data = nipa[0:7]
#             obia.add(tuple(sliced_data))
#     return list(list(nipa_baku) for nipa_baku in obia)


# Get all clients from database
# def get_all_db_client(insurance_investment):
#     query = text(f"SELECT id, fname, lname, prim_phone, busi_phone, cell_phone, dob FROM {insurance_investment}")
#     try:
#         with engine.connect() as conn:
#             result = conn.execute(query)
#             all_client = result.fetchall()
#             # Convert nested tuples to lists
#             all_client = [list(client_info) for client_info in all_client]
#             all_client.sort(key=lambda clients: clients[1])  # Sorting using the first name of each client
#             return all_client
#     except Exception as errors:
#         return errors


# Function to retrieve all events from db
# def get_all_schedule_event():
#     query = text("SELECT id, date, group_client, message FROM scheduled_event")
#     try:
#         with engine.connect() as conn:
#             results = conn.execute(query)
#             all_schedules = results.fetchall()
#             return [list(item) for item in all_schedules]
#     except Exception as error:
#         print(error)


# Function to add new contact to db
def add_new_client_db(clients_db, fname, lname, prim_phone, busi_phone, cell_phone, dob):
    try:
        query = text(
            f"INSERT INTO {clients_db} (fname, lname, prim_phone, busi_phone, cell_phone, dob) VALUES (:fname, :lname,"
            ":prim_phone, :busi_phone, :cell_phone, :dob)")
        with engine.connect() as connection:
            connection.execute(query,
                               {'fname': fname, 'lname': lname, "prim_phone": prim_phone, 'busi_phone': busi_phone,
                                'cell_phone': cell_phone, 'dob': dob})
            connection.commit()
        print("contact inserted successfully!")
        return True
    except Exception as error:
        print("Error inserting user:", error)
        return False


# Delete Scheduled Event using the id
def delete_Schedule_event(idz):
    query = text('DELETE FROM scheduled_event WHERE id = :id')
    try:
        with engine.connect() as connection:
            connection.execute(query, {'id': str(idz)})
            connection.commit()
            return "Delete successful"
    except Exception as error:
        print(error)


# Function to add scheduled events to database
def add_schedule_event(date, group_client, message):
    try:
        query = text(
            f"INSERT INTO scheduled_event (date, group_client, message) VALUES (:date, :group_client, :message)")
        with engine.connect() as connection:
            connection.execute(query, {"date": date, "group_client": group_client, "message": message})
            connection.commit()
        print("contact inserted successfully!")
        return True
    except Exception as error:
        print("Error inserting user:", error)
        return False


# Function to delete data in db, using id
def delete_data_db(client_name, table, client_id):
    allowed_tables = {"insurance_client", "investment_client", "insuran_client_test", "invst_client_test"}
    if table not in allowed_tables:
        return "Contact developer."
    query = text(f"DELETE FROM {table} WHERE id = :id")
    try:
        with engine.connect() as connection:
            connection.execute(query, {"id": client_id})
            connection.commit()
            return f"{client_name} Successfully deleted"
    except Exception as error:
        return "Ooops an error occurred"


# Function to update already existed data in db
def update_clients_data(table, id, fname, lname, prim_phone, busi_phone, cell_phone, dob):
    query = text(f"""
    UPDATE {table}
    SET fname = :fname, lname = :lname, prim_phone = :prim_phone, busi_phone = :busi_phone, cell_phone = :cell_phone, dob = :dob
    WHERE id = :id
    """)
    try:
        with engine.connect() as connection:
            # Execute the update query
            result = connection.execute(query,
                                        {"fname": fname, "lname": lname, "prim_phone": prim_phone,
                                         "busi_phone": busi_phone, "cell_phone": cell_phone,
                                         "dob": dob, "id": id})
            # Commit the changes to the database
            connection.commit()
            # Check how many rows were affected
            if result.rowcount > 0:
                print(f"Updated {result.rowcount} row(s).")
            else:
                print(f"No rows updated. Verify the id or check for duplicate values.")

            return "Client contact successfully updated"
    except Exception as error:
        return f"An error occurred: {error}"


# Function to validate user login credentials
def validate_user(username, password):
    try:
        query = text("SELECT * FROM users WHERE username = :username")
        with engine.connect() as conn:
            result = conn.execute(query, {"username": username})
            user = result.fetchone()  # Fetch the first row of results
            if user:  # Check if user exists
                return user[2] == password
    except Exception as error:
        internet_conn("ooops! check your internet connection")
        print(error)
    return False


# internet connection status function
def internet_conn(status):
    net_status.error(status)


# Check if user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login page
if not st.session_state.logged_in:
    with st.container(border=True):
        net_status = st.empty()
        login_t1, login_t2, login_t3, = st.columns([6, 4, 6])
        login_t2.subheader("Sign In")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type='password')
        button1, button2, button3, button4 = st.columns([1, 1, 2, 1])
        if button3.button("Login"):
            if validate_user(username, password):
                st.success("Login Successful!")
                st.balloons()
                time.sleep(1)
                st.session_state.logged_in = True  # Set logged in state to True
                st.rerun()  # Rerun the app to update the UI
            else:
                st.error("Invalid username or password.")

else:
    # Display content for logged-in users
    logout1, logout2, logout3, logout4 = st.columns([6, 6, 6, 3])
    if logout4.button("Sign Off"):
        st.session_state.logged_in = False  # Set logged in state to False
        st.success("You have been logged out.")
        st.rerun()  # Rerun to show login page
    header1, header2, header3 = st.columns([2, 4, 2])
    header2.subheader(".....iA SMS BROADCAST......  ", divider='rainbow')  # Content to show after successful login
    with st.sidebar:  # sidebar panel
        placeholder = st.empty()
        if st.button("ADD CLIENT"):  # Add Contact button
            with placeholder:
                st.session_state["view_contact"] = False
                st.session_state["add_schedule"] = False
                st.session_state["view_schedule"] = False
                st.session_state["add_contact"] = True

        if st.button("VIEW CLIENTS"):  # View Contact button
            with placeholder:
                st.session_state["add_contact"] = False
                st.session_state["add_schedule"] = False
                st.session_state["view_schedule"] = False
                st.session_state["view_contact"] = True

        if st.button("ADD SCHEDULE"):  # Add new scheduled events button
            with placeholder:
                st.session_state["view_contact"] = False
                st.session_state["add_contact"] = False
                st.session_state["view_schedule"] = False
                st.session_state["add_schedule"] = True

        if st.button("VIEW SCHEDULES"):  # View scheduled events
            with placeholder:
                st.session_state["add_schedule"] = False
                st.session_state["view_contact"] = False
                st.session_state["add_contact"] = False
                st.session_state["view_schedule"] = True

    # Main interface for sms sending
    with st.container(border=True, key='login_container'):
        with st.form("txt_Form", border=True, clear_on_submit=True):
            selected_clients = st.selectbox(
                "Which group of clients would you like to communicate with",
                ('Insurance Client', 'Investment Client', 'Investment TESTING'),
                index=None,
                placeholder="Select group of clients..."
            )
            if selected_clients == 'Investment Clients':
                selected_clients = 'investment_clients'
            elif selected_clients == 'Insurance Client':
                selected_clients = "insurance_client"
            elif selected_clients == "Investment TESTING":
                selected_clients = "invst_client_test"
            else:
                selected_clients = None
            sender_text = st.text_area(label="Message here:",
                                       key="sender_txt",
                                       height=220
                                       )
            send_button1, send_button2, send_button3 = st.columns([8, 6, 6])
            if send_button2.form_submit_button("SEND"):
                st.session_state["add_schedule"] = False
                st.session_state["view_contact"] = False
                st.session_state["add_contact"] = False
                st.session_state["view_schedule"] = False
                if len(sender_text) < 10:
                    st.warning("characters should be 10 or more")
                # elif '{}' not in st.session_state['sender_txt']:
                #     st.warning("You forgot place holders")
                elif selected_clients is None:
                    st.warning("Choose insurance or investment client")
                else:
                    progress_bar = st.progress(0)
                    client_contacts = get_all_db_client(selected_clients)
                    total_contact = len(client_contacts)
                    for index, recipient_info in enumerate(client_contacts):
                        unique_message = unique_text(sender_text, f'{recipient_info[1]} {recipient_info[2]}')
                        if recipient_info[3]:
                            send_sms(recipient_info[3], unique_message)
                        else:
                            send_sms(recipient_info[5], unique_message)
                        progress = (index + 1) / total_contact
                        progress_bar.progress(progress, text=f"SMS SENDING IN PROGRESS: {recipient_info[1].upper()}")
                        time.sleep(2)
                    progress_bar.empty()
                    st.success("Messages sent successfully.")
                    st.rerun()

    st.write("")

    # Adding new contact info to database
    if 'add_contact' not in st.session_state:
        st.session_state["add_contact"] = None
    if "add_contact" and st.session_state["add_contact"]:
        with st.container(border=True, key='add_contact1'):
            st.info("ADD NEW CLIENTS TO DATABASE")
            saving_db = st.selectbox('Saving to insurance client or investment client',
                                     ("Investment Clients", 'Insurance Clients', 'Client Test', 'Client Test 2'),
                                     index=None,
                                     placeholder='Belongs to which set of clients?..'
                                     )
            fname, lname = st.columns(2)
            phone_no, c_dob = st.columns(2)
            first_name = fname.text_input("First name:")
            last_name = lname.text_input("Last name:")
            phone = phone_no.text_input("Mobile No#:", placeholder="+14321234567")
            dob = c_dob.date_input("Date Of Birth:", min_value=date(1900, 1, 1), max_value=date.today())
            save_butt1, save_butt2, save_butt3 = st.columns([4, 2, 4])
            if save_butt2.button("SAVE.."):
                if all([first_name, last_name, phone, dob, saving_db]):
                    if saving_db == "Investment Clients":
                        saving_db = "investment_client"
                    elif saving_db == "Insurance Clients":
                        saving_db = "insurance_client"
                    elif saving_db == "Client Test":
                        saving_db = "insuran_client_test"
                    elif saving_db == "Client Test 2":
                        saving_db = "invst_client_test"
                    else:
                        saving_db = None
                    add_new_client_db(saving_db, first_name, last_name, phone, phone, phone, dob)
                    print("it all a truthy")
                    st.success("Client saved successfully")
                    st.snow()
                    time.sleep(3)
                    st.session_state["add_contact"] = False
                    st.rerun()
                else:
                    st.error("Some fields might be empty, please cross check!")

    # View Contacts page
    if 'view_contact' not in st.session_state:
        st.session_state["view_contact"] = None
    if "view_contact" and st.session_state["view_contact"]:
        names = [['Jonathan kofi', '+12627261908'], ['Jonathan1 kofi', '+12627261908'],
                 ['Jonathan2 kofi', '+12627261908'], ['Jonathan3 kofi', '+12627261908']]
        with st.container(border=True, height=600):
            st.info(f"AVAILABLE CONTACTS")
            select_clients = st.selectbox(
                "",
                ('Investment Client', 'Insurance Client', "Client Testing", "Client Testing 2"),
                index=None,
                placeholder="Select group of clients..."
            )
            if select_clients == "Investment Client":
                select_clients = "investment_client"
            elif select_clients == "Insurance Client":
                select_clients = "insurance_client"
            elif select_clients == "Client Testing":
                select_clients = "insuran_client_test"
            elif select_clients == "Client Testing 2":
                select_clients = "invst_client_test"
            else:
                select_clients = None

            if not select_clients:
                st.warning("Please select a group of clients.")
            else:
                all_clients = get_all_db_client(select_clients)

                for index, c_name in enumerate(all_clients):
                    form_dob = str(c_name[6])
                    with st.expander(f"{c_name[1]} {c_name[2]} {c_name[6]}"):
                        edit_colum1, edit_colum2 = st.columns(2)
                        edit_fname = edit_colum1.text_input("First Name:", key=f"{index}-{c_name[1]}-{c_name[0]}",
                                                            value=c_name[1])
                        edit_lname = edit_colum2.text_input("Last Name:", key=f"{index}-{c_name[2]}-{c_name[0]}",
                                                            value=c_name[2])
                        edit_dob = edit_colum1.date_input("DOB", value=datetime.datetime.strptime(form_dob, "%Y-%m-%d"),
                                                          min_value=date(1900, 1, 1), max_value=date.today(), key=index)
                        edit_phone = edit_colum2.text_input("Phone:", key=f"{c_name[3]}-{c_name[0]}", value=c_name[3])
                        if edit_colum1.button("Save", key=f"{index}-{c_name[0]}"):
                            updated_status = update_clients_data(select_clients, c_name[0], edit_fname, edit_lname,
                                                                 edit_phone, "", edit_phone,
                                                                 edit_dob.strftime("%Y-%m-%d"))
                            st.success(updated_status)
                            time.sleep(2)
                            st.rerun()
                        if edit_colum2.button("Delete", key=f"{index}-{c_name[2]}"):
                            st.success(delete_data_db(f"{c_name[1]} {c_name[2]}", select_clients, c_name[0]))
                            time.sleep(1)
                            st.rerun()

    # Add Schedule Page
    if 'add_schedule' not in st.session_state:
        st.session_state["add_schedule"] = None
    if "add_schedule" and st.session_state["add_schedule"]:
        with st.container(border=True):
            with st.form("schedule_add", border=False, clear_on_submit=True):
                st.info("SCHEDULE MESSAGES")
                add_sche_date, add_sche_client = st.columns(2)
                sched_date = add_sche_date.date_input("Choose Date:", key="sched_date")
                sched_clients = add_sche_client.selectbox("Select Clients:",
                                                          ('Investment Clients', 'Insurance Clients', 'All Clients',
                                                           'Insurance TESTING', 'Investment TESTING'),
                                                          index=None,
                                                          placeholder="Select group of clients", key="sched_clients"
                                                          )
                sched_message = st.text_area("Messages here:", height=200, key='sched_message')
                if st.form_submit_button("SAVE ME"):
                    if sched_clients == "Investment Clients":
                        sched_clients = "investment_client"
                    elif sched_clients == 'Insurance Clients':
                        sched_clients = "insurance_client"
                    elif sched_clients == 'Insurance TESTING':
                        sched_clients = "insuran_client_test"
                    elif sched_clients == 'Investment TESTING':
                        sched_clients = "invst_client_test"
                    elif sched_clients == 'All Clients':
                        sched_clients = "all_clients"
                    else:
                        sched_clients = None
                    if all([sched_date, sched_clients, sched_message]):
                        add_schedule_event(sched_date, sched_clients, sched_message)
                        st.success("Event saved successfully")
                        time.sleep(3)
                        st.rerun()
                    else:
                        st.error("Empty fields")

    # View Schedules Page
    if 'view_schedule' not in st.session_state:
        st.session_state["view_schedule"] = None
    if "view_schedule" and st.session_state["view_schedule"]:
        with st.container(border=True, height=720):
            list_of_schedule = get_all_schedule_event()
            list_of_schedule = [[str(item) for item in event_schedule] for event_schedule in list_of_schedule]
            search_result = []
            st.info("AVAILABLE SCHEDULES")
            search_word = st.text_input("Search events:", placeholder="Looking for a specific event ?..")
            if search_word:
                for items in list_of_schedule:
                    for info_item in items:
                        if search_word.lower() in info_item.lower():
                            search_result.append(items)
                for itemsz_info in search_result:
                    with st.container(border=True):
                        if st.checkbox(f"{itemsz_info[1]} - {itemsz_info[3]} ({itemsz_info[2]})"):
                            delete_Schedule_event(itemsz_info[0])
                            st.rerun()
            else:
                for items_in in list_of_schedule:
                    with st.container(border=True):
                        delete_info = st.checkbox(f"{items_in[1]} - {items_in[3]} \n({items_in[2]})")
                        if delete_info:
                            delete_Schedule_event(items_in[0])
                            st.rerun()


