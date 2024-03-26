import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Standard library imports
import base64
import json
import logging
import sqlite3
import uuid
from datetime import datetime
import xml.etree.ElementTree as ET
# import time  # Uncomment if used elsewhere in your application

# Third-party imports
import requests
from cryptography.hazmat.primitives import serialization, asymmetric
from jose import jwk
import pyperclip
import ttkbootstrap as ttk
from tkinter import PhotoImage, messagebox, filedialog
import tkinter as tk
from ttkbootstrap import Style


from cryptography.fernet import Fernet  # Uncomment if used elsewhere
from cryptography.hazmat.backends import default_backend  # Uncomment if used elsewhere

# Application-specific imports
from samarbeidsportalen import get_access_token



# Logging configuration
logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_settings_table():
    conn = sqlite3.connect('vegvesen_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 password TEXT)''')
    conn.commit()
    conn.close()


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def main_app():
    
    def on_closing():
        root.destroy()

    # Functionality to read XML and fetch data from Vegvesen
    def fetch_vegvesen_data(file_path, iviref_uid):
        print(f"Debug: The file_path is {file_path}")
        
        access_token = get_access_token()
        if access_token:
            print("Access token retrieved successfully.")
        else:
            result_text.set(access_token)
        
        conn = None  # Initialize to None
        iviReferanse = ''  # Initialize to an empty string or some default value
        understellsnummer = ''
        datoTid = ''
        meldingstekst = ''
        IviDoc = ''
        
        
        if access_token is None:
            logging.error("Could not get an access token.")
            return "Could not get an access token.", None

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        with open(file_path, "r", encoding='utf-16') as f:  
            ivi_document = f.read()
            
        ivi_base64_encoded = base64.b64encode(ivi_document.encode()).decode()
        avgiftskode = avgiftskode_entry.get()
        sitteplasserNorskGodkjenning = sitteplasserNorskGodkjenning_entry.get()
        sengeplasserCampingbil = sengeplasserCampingbil_entry.get()

        data = {
            "ivi": {
                "iviDokument": ivi_base64_encoded,
                "iviReferanse": iviref_uid,
            },
            "avgiftsklassifisering": {
                "avgiftsKode": avgiftskode,
                "sitteplasserNorskGodkjenning": sitteplasserNorskGodkjenning,
                "sengeplasserCampingbil": sengeplasserCampingbil
            }
        }
        
        data_json = json.dumps(data)
        url = "https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/innmelding/meldingompreregistrering/v1/opprette"
        response = requests.post(url, headers=headers, data=data_json)
        print(response)
        
        # Debugging: Print the HTTP status code and content
        print(f"Debug: Headers: {headers}")

        print(f"Debug: HTTP Status Code: {response.status_code}")
        print(f"Debug: Response Content: {response.content}")
        
        
        if response.status_code == 200:
                response_dict = json.loads(response.content)
                iviReferanse = response_dict.get("iviIdentifikator", {}).get("iviReferanse", "")
                understellsnummer = response_dict.get("iviIdentifikator", {}).get("understellsnummerMerke", {}).get("understellsnummer", "")
                datoTid = response_dict.get("datoTid", "")
                meldingstekst = response_dict.get("melding", {}).get("meldingstekst", "")

                try:
                    conn = sqlite3.connect('vegvesen_data.db')
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO responses (iviReferanse, understellsnummer, datoTid, meldingstekst, IviDoc) VALUES (?, ?, ?, ?, ?)",
                        (iviReferanse, understellsnummer, datoTid, meldingstekst, ivi_document)
                    )
                    conn.commit()
                except sqlite3.OperationalError as e:
                    print(f"SQLite error: {e}")
                    logging.error(f"An error occurred: {e}")
                finally:
                    if conn:
                        conn.close()

        # Convert the JSON response to a pretty string, if possible
        try:
            response_dict = json.loads(response.content)
            pretty_response = json.dumps(response_dict, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            pretty_response = response.content.decode('utf-8')  
            logging.error(f"An error occurred: {e}")


        return f"HTTP Status Code: {response.status_code}", f"Vegvesen Response:\n{pretty_response}"



    def update_ivi_reference_in_xml(file_path, new_ivi_ref):
        try:
            # Debug: Print the first 100 characters of the file to check its format
            with open(file_path, "r", encoding='utf-16-le') as f:

                print(f.read(1000))

            # Explicitly set the encoding in the XML Parser
            tree = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8'))


            root = tree.getroot()
            
            # Update the IVIReferenceId value
            for elem in root.iter('IVIReferenceId'):
                elem.text = new_ivi_ref
                break  # Assuming only one IVIReferenceId in the XML

            # Save the updated XML back to the file
            tree.write(file_path, encoding='utf-16')
            
            return file_path  # or return the new file path

        except ET.ParseError as e:
            print(f"An error occurred while parsing the XML file: {e}")
            logging.error(f"An error occurred: {e}")
            return False


    def read_vehicle_identification_number(file_path):
        try:
            tree = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8'))
            root = tree.getroot()
            for elem in root.iter('VehicleIdentificationNumber'):  # Leser fra XML, må være korrekt tag.
                return elem.text
        except ET.ParseError as e:
            print(f"An error occurred while parsing the XML file: {e}")
            logging.error(f"An error occurred while parsing the XML file: {e}")
            return None





    def update_vehicle_identification_number(file_path, new_vin):
        try:
            tree = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8'))
            root = tree.getroot()
            for elem in root.iter('VehicleIdentificationNumber'):  
                elem.text = new_vin
                break  # Assuming only one VIN tag in the XML
            tree.write(file_path, encoding='utf-16')
        except ET.ParseError as e:
            logging.error(f"An error occurred while parsing the XML file: {e}")
            print(f"An error occurred while parsing the XML file: {e}")




    def create_database():
        conn = None
        try:
            conn = sqlite3.connect('vegvesen_data.db')
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                iviReferanse TEXT,
                understellsnummer TEXT,
                datoTid TEXT,
                meldingstekst TEXT,
                IviDoc TEXT
            )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            logging.error(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    # Main GUI Setup
    root = ttk.Window()
    root.title("Easy eCoC")
    root.minsize(width=800, height=600)
    root.protocol("WM_DELETE_WINDOW", on_closing) 
    #root.geometry("2000x1480")
    #root.resizable(0, 0)
    #root.state('zoomed')



    style = Style()
    style.theme_use('darkly')  # dark theme

    image = PhotoImage(file='./img/Icon.png') 
    image = image.subsample(8, 8)
    image_label = ttk.Label(root, image=image)
    image_label.pack(side='left')  # Places the image above the notebook


    # Add a Notebook for tab functionality
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Create frames for each tab
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    # Add tabs to the notebook
    notebook.add(tab1, text="Vegvesen eCoC")
    notebook.add(tab2, text="Settings")
    notebook.add(tab3, text="JWT Keygen")

    # Inner frame to hold frame1, frame2, frame3, and vertical_divider
    inner_frame = ttk.Frame(tab1)
    inner_frame.pack(side='top', fill='both', expand=True, padx=20, pady=20)

    # Create and pack the vertical divider
    vertical_divider = tk.Frame(inner_frame, width=5, bg='grey')
    vertical_divider.pack(side='left', fill='y')

    # Frame1, Frame2, Frame3 as you have them
    frame1 = ttk.Frame(inner_frame)
    frame1.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    frame2 = ttk.Frame(inner_frame)
    frame2.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    frame3 = ttk.Frame(inner_frame)
    frame3.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    # Frame for displaying data from selected row, make this occupy full height
    bottom_frame = ttk.Frame(inner_frame)
    bottom_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    # Frame for "Innsendt XML Data", this will be inside bottom_frame
    frame4 = ttk.Frame(bottom_frame)
    frame4.pack(side='top', fill='both', expand=True, padx=20, pady=20)
    
    frame_line = tk.Frame(root, height=5, bg='grey')
    frame_line.pack(fill='x')


    xml_label = ttk.Label(frame1, text="IVI XML", font=("Arial", 16, "bold"))
    xml_label.pack(pady=(20, 0))

    # Frame 1: Form and Actions
    file_label = ttk.Label(frame1, text="Velg XML Fil:")
    file_label.pack(pady=(20, 0))

    file_entry = ttk.Entry(frame1, width=50)
    file_entry.pack()


    # Function to load settings from the database
    def load_settings_from_db():
        try:
            conn = sqlite3.connect('vegvesen_data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM samarbeidsportalen LIMIT 1") 
            row = c.fetchone()
            if row:
                issuer_entry.delete(0, tk.END)
                issuer_entry.insert(0, row[0])  

                audience_entry.delete(0, tk.END)
                audience_entry.insert(0, row[1])  
                
                resource_entry.delete(0, tk.END)
                resource_entry.insert(0, row[2])  
                
                scope_entry.delete(0, tk.END)
                scope_entry.insert(0, row[3])
                
                keystore_password_entry.delete(0, tk.END)
                keystore_password_entry.insert(0, row[4])
                
                keystore_alias_entry.delete(0, tk.END)
                keystore_alias_entry.insert(0, row[5])
                
                keystore_alias_password_entry.delete(0, tk.END)
                keystore_alias_password_entry.insert(0, row[6])
                


        except sqlite3.Error as e:
            print(f"Database error: {e}")
            logging.error(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    # Function to save settings to the database
    def save_settings_to_db():
        issuer = issuer_entry.get()
        audience = audience_entry.get()
        if not audience:
            audience = "https://maskinporten.no/"   # Default audience (Produksjonsmiljø)
            
        scope = scope_entry.get()
        if not scope:
            scope = "svv:kjoretoy/ecoc"  # Default scope
        
        resource = resource_entry.get()
        if not resource:
            resource = "https://www.vegvesen.no" # Default resource
            
        keystore_password = keystore_password_entry.get()
        if not keystore_password:
            keystore_password = "Keystore Password" # Default keystore password
        
        keystore_alias = keystore_alias_entry.get()
        if not keystore_alias:
            keystore_alias = "Keystore Alias"   # Default keystore alias
            
        keystore_alias_password = keystore_alias_password_entry.get()
        if not keystore_alias_password:
            keystore_alias_password = "Keystore Alias Password" # Default keystore alias password
            

        try:
            conn = sqlite3.connect('vegvesen_data.db')
            c = conn.cursor()
            c.execute("DELETE FROM samarbeidsportalen")  # Clear existing settings
            c.execute("INSERT INTO samarbeidsportalen (issuer, audience, resource, scope, keystore_password, keystore_alias, keystore_alias_password) VALUES (?, ?, ?, ?, ?, ?, ?)", (issuer, audience, resource, scope, keystore_password, keystore_alias, keystore_alias_password))

            conn.commit()
            print("Settings saved.")

            # Now refresh the settings fields to make sure they reflect the current saved settings
            from samarbeidsportalen import load_config_from_db

            
            load_config_from_db()
            
            load_settings_from_db()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            logging.error(f"Database error: {e}")
        finally:
            if conn:
                conn.close()



    # Create a frame for the Samarbeidsportalen settings
    samarbeidsportalen_frame = ttk.LabelFrame(tab2, text="Samarbeidsportalen", padding="10 10 10 10")
    samarbeidsportalen_frame.pack(fill="x", padx=20, pady=20)

    global issuer_entry, audience_entry, scope_entry, resource_entry, keystore_password_entry, keystore_alias_entry, keystore_alias_password_entry

    def add_labeled_entry(frame, label_text):
        label = tk.Label(frame, text=label_text)
        label.pack()
        entry = tk.Entry(frame, width=50, justify='center')
        entry.pack()
        return entry

    issuer_entry = add_labeled_entry(samarbeidsportalen_frame, "Issuer:")
    audience_entry = add_labeled_entry(samarbeidsportalen_frame, "Audience:")
    scope_entry = add_labeled_entry(samarbeidsportalen_frame, "Scope:")
    resource_entry = add_labeled_entry(samarbeidsportalen_frame, "Resource:")
    keystore_password_entry = add_labeled_entry(samarbeidsportalen_frame, "Keystore Password:")
    keystore_alias_entry = add_labeled_entry(samarbeidsportalen_frame, "Keystore Alias:")
    keystore_alias_password_entry = add_labeled_entry(samarbeidsportalen_frame, "Keystore Alias Password:")

    # Button to save settings
    save_button = ttk.Button(samarbeidsportalen_frame, text="Save Settings", command=save_settings_to_db)
    save_button.pack(padx=10, pady=10)

    load_settings_from_db()  # If this is how you are calling it



        # GUI Functions
    def open_file_dialog():
        file_path = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML files", "*.xml")])
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)
            
            # Read the VIN from the selected XML file
            vin = read_vehicle_identification_number(file_path)
            
            # Update the VIN input field
            if vin:
                vin_entry.delete(0, tk.END)
                vin_entry.insert(0, vin)

    file_button = ttk.Button(frame1, text="Last inn XML fil", command=open_file_dialog, bootstyle='primary')
    file_button.pack(pady=(10, 20))

    ivi_label = ttk.Label(frame1, text="IVI Referanse ID:")
    ivi_label.pack(anchor="center")

    ivi_entry = ttk.Entry(frame1, width=50, justify='center')
    ivi_entry.pack()
    
    
    
    def generate_ivi_ref_id():
        iviref_uid = str(uuid.uuid4())
        ivi_entry.delete(0, tk.END)
        ivi_entry.insert(0, iviref_uid)

    generate_button = ttk.Button(frame1, text="Generer", command=generate_ivi_ref_id, bootstyle='info')
    generate_button.pack(pady=(10, 20))


    vin_label = ttk.Label(frame1, text="Vehicle Identification Number:")
    vin_label.pack(anchor="center")

    vin_entry = ttk.Entry(frame1, width=50, justify='center')
    vin_entry.pack()

        
    def execute():
        file_path = file_entry.get()
        iviref_uid = ivi_entry.get()
        new_vin = vin_entry.get()

        if not file_path or not iviref_uid:
            result_text.set("File path or IVI Reference ID cannot be empty.")
            return

        # Check if IVI or VIN exists in the database (pseudo code)
        if check_if_exists_in_database("ivi", iviref_uid) or check_if_exists_in_database("vin", new_vin):
            result_text.set("IVI Reference ID or VIN already exists in the database.")
            return

        user_response = messagebox.askyesno("Confirmation", "Er du sikker på at alt er riktig? Ja eller Nei")
        if not user_response:
            result_text.set("User cancelled the operation.")
            return

        new_file_path = update_ivi_reference_in_xml(file_path, iviref_uid)
        update_vehicle_identification_number(new_file_path, new_vin)
        if not isinstance(new_file_path, str) or not new_file_path:
            result_text.set("Failed to update XML.")
            return

        print(f"Debug: The new_file_path after updating is {new_file_path}")

        status, response = fetch_vegvesen_data(new_file_path, iviref_uid)
        result_text.set(status)
        set_response_text(response)
        populate_table()
        time.sleep(2)

    def check_if_exists_in_database(type_of_id, value):
        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()
        
        column_name = "iviReferanse" if type_of_id == "ivi" else "understellsnummer"
        
        c.execute(f'SELECT COUNT(*) FROM responses WHERE {column_name} = ?', (value,))
        exists = c.fetchone()[0]
        
        conn.close()
        
        return exists > 0
        
        
    #Avgiftskode input
    
    def validate_input(char, value_if_allowed):
        if char in '0123456789' or value_if_allowed == '':
            try:
                if value_if_allowed != '':
                    int(value_if_allowed)
                return True
            except ValueError:
                logging.error(f"An error occurred validating input: {ValueError}")
                return False
        else:
            return False

    # Create a Tcl wrapper for Python function
    validate_input_wrapper = root.register(validate_input)

    # Create a main sub-frame inside frame1 for avgiftskode
    avgiftskode_frame = ttk.Frame(frame1)
    avgiftskode_frame.pack(side=tk.TOP, pady=50)  # Adjust padding as needed

    # Add the "Avgiftsklassifisering:" label with larger, bold font
    avgiftskode1_label = ttk.Label(avgiftskode_frame, text="Avgiftsklassifisering", font=("Arial", 16, "bold"))
    avgiftskode1_label.grid(row=0, column=0, columnspan=2, pady=15)


    # Add "Avgiftskode:" label and entry
    avgiftskode_label = ttk.Label(avgiftskode_frame, text="Avgiftskode:")
    avgiftskode_label.grid(row=1, column=0, padx=5, pady=5)

    avgiftskode_entry = ttk.Entry(avgiftskode_frame, width=10, justify='center',
                                validate='key',
                                validatecommand=(validate_input_wrapper, '%S', '%P'))
    avgiftskode_entry.grid(row=1, column=1, padx=5, pady=5)

    # Add "Sitteplasser Norsk Godkjenning:" label and entry
    sittepl_label = ttk.Label(avgiftskode_frame, text="Sitteplasser Norsk Godkjenning:")
    sittepl_label.grid(row=2, column=0, padx=5, pady=5)

    sitteplasserNorskGodkjenning_entry = ttk.Entry(avgiftskode_frame, width=10, justify='center',
                                                    validate='key',
                                                    validatecommand=(validate_input_wrapper, '%S', '%P'))
    sitteplasserNorskGodkjenning_entry.grid(row=2, column=1, padx=5, pady=5)

    # Add "Sengeplasser Campingbil:" label and entry
    sengepl_label = ttk.Label(avgiftskode_frame, text="Sengeplasser Campingbil:")
    sengepl_label.grid(row=3, column=0, padx=5, pady=5)

    sengeplasserCampingbil_entry = ttk.Entry(avgiftskode_frame, width=10, justify='center',
                                            validate='key',
                                            validatecommand=(validate_input_wrapper, '%S', '%P'))
    sengeplasserCampingbil_entry.grid(row=3, column=1, padx=5, pady=5)

    # Initialize the entry fields
    sitteplasserNorskGodkjenning_entry.insert(0, "0")
    avgiftskode_entry.insert(0, "0")
    sengeplasserCampingbil_entry.insert(0, "0")


    

    nested_frame = ttk.Frame(frame1, relief='solid', borderwidth=0)
    nested_frame.pack(side=tk.TOP, pady=5)
    
    execute_button = ttk.Button(nested_frame, text="Send inn til Vegvesen", command=execute, bootstyle='warning')
    execute_button.grid(row=0, column=0, pady=(10, 20), padx=(0, 10), sticky="w")



    # Frame 2: Response
    

    # Create a frame to hold the table and search bar
    table_and_search_frame = ttk.Frame(frame3)
    table_and_search_frame.pack(fill=tk.BOTH, expand=True)

    # Frame 3: Table
    # Create a Scrollbar for the table
    table_scrollbar = ttk.Scrollbar(table_and_search_frame, orient="vertical")
    table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Table Treeview
    table = ttk.Treeview(table_and_search_frame, height=30, columns=("iviReferanse", "understellsnummer", "datoTid", "meldingstekst"), yscrollcommand=table_scrollbar.set, show='headings')
    table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # Make sure to expand and fill



    table.heading("iviReferanse", text="IVI Reference")
    table.heading("understellsnummer", text="Understellsnummer")
    table.heading("datoTid", text="Dato")
    table.heading("meldingstekst", text="Meldingstekst")

    # Set the column width and alignment for all columns
    table.column("iviReferanse", width=200, anchor="center")
    table.column("understellsnummer", width=200, anchor="center")
    table.column("datoTid", width=100, anchor="center")
    table.column("meldingstekst", width=600, anchor="center")  # Set the width to 600 or any other value that suits your needs

    table_and_boxes_frame = ttk.Frame(frame3)
    table_and_boxes_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create a frame for search bar below the table
    search_frame = ttk.Frame(table_and_search_frame)
    search_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Add search Entry and Button
    search_entry = ttk.Entry(search_frame, width=10)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    search_button = ttk.Button(search_frame, bootstyle="warning", text="Søk", command=lambda: search_table(search_entry.get()))
    search_button.pack(side=tk.RIGHT)
    
    # Create a frame to hold the response and ividoc boxes horizontally
    response_and_ividoc_frame = ttk.Frame(table_and_boxes_frame)
    response_and_ividoc_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(30, 0))

    
    result_text = tk.StringVar()
    result_label = ttk.Label(response_and_ividoc_frame, textvariable=result_text)
    result_label.pack(side=tk.TOP, fill=tk.X)  # pack at the top of the frame
    result_text.set("Respons fra Vegvesen:")

    # Create a Scrollbar and a Text widget for the response box
    response_scrollbar = ttk.Scrollbar(response_and_ividoc_frame, orient="vertical")
    response_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    response_text = tk.Text(response_and_ividoc_frame, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)  # increased height from 10 to 20
    response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Connect the Scrollbar to the Text widget
    response_text.config(yscrollcommand=response_scrollbar.set)
    response_scrollbar.config(command=response_text.yview)

    # Create a Scrollbar and a Text widget for the ividoc box
    ividoc_scrollbar = ttk.Scrollbar(response_and_ividoc_frame, orient="vertical")
    ividoc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    ividoc_text = tk.Text(response_and_ividoc_frame, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED)  # increased height from 10 to 20
    ividoc_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Connect the Scrollbar to the Text widget
    ividoc_text.config(yscrollcommand=ividoc_scrollbar.set)
    ividoc_scrollbar.config(command=ividoc_text.yview)
    



    
    def search_table(search_term):
        for row in table.get_children():
            table.delete(row)
            
        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()

        for row in c.execute('SELECT * FROM responses WHERE iviReferanse LIKE ? OR understellsnummer LIKE ?', (f"%{search_term}%", f"%{search_term}%")):
            if all(row):
                try:
                    date_str = row[2]
                    date_str = date_str.split(".")[0]  # Truncate nanoseconds
                    formatted_date = datetime.fromisoformat(date_str.replace('T', ' ')).strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    logging.error(f"Date formatting error: {e}")
                    formatted_date = row[2]
                table.insert('', tk.END, values=(row[0], row[1], formatted_date, row[3]))
        conn.close()

    
    def populate_table():
        for row in table.get_children():
            table.delete(row)

        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()
        for row in c.execute('SELECT * FROM responses'):
            if all(row):  # Check if all fields in the row are not None or empty
                try:
                    date_str = row[2]
                    date_str = date_str.split(".")[0]  # Truncate nanoseconds
                    formatted_date = datetime.fromisoformat(date_str.replace('T', ' ')).strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Date formatting error: {e}")
                    logging.error(f"Date formatting error: {e}")
                    formatted_date = row[2]

                table.insert('', tk.END, values=(row[0], row[1], formatted_date, row[3]))
            else:
                print("Skipping row with empty or None fields.")
        conn.close()


    # Function to populate the form when a table row is selected
    def on_table_select(event):
        try:
            item = table.selection()[0]
            selected_row = table.item(item, 'values')
            iviReferanse = selected_row[0]
            understellsnummer = selected_row[1]
            datoTid = selected_row[2]
            meldingstekst = selected_row[3]
            
            ivi_entry.delete(0, tk.END)
            ivi_entry.insert(0, iviReferanse)
            
            # Populate the VIN entry field
            vin_entry.delete(0, tk.END)
            vin_entry.insert(0, understellsnummer)
            
            ividoc_text.config(state=tk.NORMAL)
            ividoc_text.delete(1.0, tk.END)
            
            # Fetch the ividoc value from your database for the selected row.
            # Replace this with your actual code for fetching ividoc.
            conn = sqlite3.connect('vegvesen_data.db')
            c = conn.cursor()
            c.execute("SELECT ividoc FROM responses WHERE understellsnummer = ?", (understellsnummer,))
            ividoc_data = c.fetchone()
            if ividoc_data:
                ividoc_text.insert(tk.END, ividoc_data[0])
            
            ividoc_text.config(state=tk.DISABLED)
            
        except IndexError:
            print("No row selected.")

    table.bind('<ButtonRelease-1>', on_table_select)
    table.bind('<<TreeviewSelect>>', on_table_select)
    

        
        
    def set_response_text(text):
        response_text.config(state=tk.NORMAL)
        response_text.delete(1.0, tk.END)
        
        # Configure tags for success and failure
        response_text.tag_configure('success', foreground='green', font=('Arial', 12, 'bold'))
        response_text.tag_configure('failure', foreground='red', font=('Arial', 12, 'bold'))
        
        # Determine the status code from the text (assuming it starts with "HTTP Status Code: ")
        if "HTTP Status Code: 200" in text:
            response_text.insert(tk.END, text.split("\n")[0] + "\n", 'success')
        else:
            response_text.insert(tk.END, text.split("\n")[0] + "\n", 'failure')

        # Insert the rest of the text
        response_text.insert(tk.END, "\n".join(text.split("\n")[1:]))

        response_text.config(state=tk.DISABLED)

        
    


    def delete_entry():
        
        selected_items = table.selection()
        if not selected_items:
            set_response_text("Ingen rader er valgt.")
            return
        
        selected_item = table.selection()[0]  # Get selected item from the table
        vin_to_delete = table.item(selected_item, 'values')[1]  # VIN


        confirm = messagebox.askyesno("Bekreftelse", f"Sikker på at du vil slett VIN: {vin_to_delete}?")
        if not confirm:
            return
        
        access_token = get_access_token()
        if access_token is None:
            return "Could not get an access token."

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        url = f"https://vegvesen.no/ws/no/vegvesen/kjoretoy/felles/innmelding/meldingompreregistrering/v1/slette/understellsnummer/{vin_to_delete}"
        response = requests.delete(url, headers=headers)

        server_response = response.text  
        pretty_server_response = json.dumps(json.loads(server_response), indent=4)


        if response.status_code == 200:
            conn = sqlite3.connect('vegvesen_data.db')
            c = conn.cursor()
            c.execute("DELETE FROM responses WHERE understellsnummer = ?", (vin_to_delete,))
            conn.commit()
            conn.close()

            populate_table()  # Refresh the table
            set_response_text(f"Deleted entry with VIN: {vin_to_delete}\nServer Response: {pretty_server_response}")
        else:
            set_response_text(f"Failed to delete entry with VIN: {vin_to_delete}. HTTP Status Code: {response.status_code}\nServer Response: {pretty_server_response}")


    # GUI Functions
    def open_file_dialog():
        file_path = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML files", "*.xml")])
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)
            
            # Read the VIN from the selected XML file
            vin = read_vehicle_identification_number(file_path)
            
            # Update the VIN input field
            if vin:
                vin_entry.delete(0, tk.END)
                vin_entry.insert(0, vin)



    delete_button = ttk.Button(nested_frame, text="Slett fra Vegvesen", command=delete_entry, bootstyle='danger')
    delete_button.grid(padx=5, pady=5)



    delete_button.config(command=delete_entry)
    

    # Tab 3: JWT Keygen
    # Hovedsaklig brukt for å generere en public key i JWK format
    # Du kan da kopiere denne til maskinportalen for å generere en access token i demo miljøet
    
    def run_pubkeygen():

        private_key = asymmetric.rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Save Private Key to a file if needed
        with open("private_key.pem", "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Step 2: Convert Public Key to JWK
        jwk_dict = jwk.construct(public_key, algorithm='RS256').to_dict()

        # Add extra parameters
        jwk_dict['use'] = 'sig'
        jwk_dict['kid'] = 'min_egen_nokkel'  # Replace with your own key ID
        
        jwk_output = json.dumps([jwk_dict], indent=2)

        pyperclip.copy(jwk_output)
        
        jwt_output_text.delete(1.0, tk.END)  # Clear previous text
        jwt_output_text.insert(tk.END, "Public key in JWK format:\n")
        jwt_output_text.insert(tk.END, jwk_output)


        # Step 3: Print JWK
        # print("Public key in JWK format:")
        # print(jwk_dict)


        # Wrap in a list and convert to JSON string
        jwk_array_json = json.dumps([jwk_dict], indent=2)
        # print("Public key in JWK format as an array:")
        # print(jwk_array_json)

            
    frame3_tab3 = ttk.Frame(tab3)
    frame3_tab3.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    jwt_button = ttk.Button(frame3_tab3, text="Generate JWT Key", command=run_pubkeygen, bootstyle='info')
    jwt_button.pack(pady=(10, 20))

    jwt_output_text = tk.Text(frame3_tab3, wrap='word', width=50, height=10)
    jwt_output_text.pack()
    
    

    icon = './img/Icon.png'
    root.iconphoto(True, PhotoImage(file=icon))
    
    table_scrollbar.config(command=table.yview)

    # Run the main loop
    create_database()
    populate_table()
    root.mainloop()
    
    

        
    
# Start the application
if __name__ == '__main__':
    main_app()


