import locale
import time
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

import logging
import tkinter as tk
from tkinter import PhotoImage, messagebox, filedialog

import ttkbootstrap as ttk
from ttkbootstrap import Style

import ecoc_service as svc

# Logging configuration
logging.basicConfig(filename='application.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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

    # --- Main window setup ---
    root = ttk.Window()
    root.title("Easy eCoC")
    root.minsize(width=800, height=600)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    style = Style()
    style.theme_use('darkly')

    image = PhotoImage(file='./img/Icon.png')
    image = image.subsample(8, 8)
    image_label = ttk.Label(root, image=image)
    image_label.pack(side='left')

    # --- Notebook / Tabs ---
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)

    notebook.add(tab1, text="Vegvesen eCoC")
    notebook.add(tab2, text="Settings")
    notebook.add(tab3, text="JWT Keygen")

    # ==================== Tab 1: Vegvesen eCoC ====================

    inner_frame = ttk.Frame(tab1)
    inner_frame.pack(side='top', fill='both', expand=True, padx=20, pady=20)

    vertical_divider = tk.Frame(inner_frame, width=5, bg='grey')
    vertical_divider.pack(side='left', fill='y')

    frame1 = ttk.Frame(inner_frame)
    frame1.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    frame2 = ttk.Frame(inner_frame)
    frame2.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    frame3 = ttk.Frame(inner_frame)
    frame3.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    bottom_frame = ttk.Frame(inner_frame)
    bottom_frame.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    frame4 = ttk.Frame(bottom_frame)
    frame4.pack(side='top', fill='both', expand=True, padx=20, pady=20)

    frame_line = tk.Frame(root, height=5, bg='grey')
    frame_line.pack(fill='x')

    # --- Frame 1: XML form ---

    xml_label = ttk.Label(frame1, text="IVI XML", font=("Arial", 16, "bold"))
    xml_label.pack(pady=(20, 0))

    file_label = ttk.Label(frame1, text="Velg XML Fil:")
    file_label.pack(pady=(20, 0))

    file_entry = ttk.Entry(frame1, width=50)
    file_entry.pack()

    def open_file_dialog():
        file_path = filedialog.askopenfilename(
            title="Select XML File", filetypes=[("XML files", "*.xml")])
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)
            vin = svc.read_vehicle_identification_number(file_path)
            if vin:
                vin_entry.delete(0, tk.END)
                vin_entry.insert(0, vin)

    file_button = ttk.Button(
        frame1, text="Last inn XML fil", command=open_file_dialog, bootstyle='primary')
    file_button.pack(pady=(10, 20))

    ivi_label = ttk.Label(frame1, text="IVI Referanse ID:")
    ivi_label.pack(anchor="center")

    ivi_entry = ttk.Entry(frame1, width=50, justify='center')
    ivi_entry.pack()

    def on_generate_ivi_ref():
        ivi_entry.delete(0, tk.END)
        ivi_entry.insert(0, svc.generate_ivi_ref_id())

    generate_button = ttk.Button(
        frame1, text="Generer", command=on_generate_ivi_ref, bootstyle='info')
    generate_button.pack(pady=(10, 20))

    vin_label = ttk.Label(frame1, text="Vehicle Identification Number:")
    vin_label.pack(anchor="center")

    vin_entry = ttk.Entry(frame1, width=50, justify='center')
    vin_entry.pack()

    # --- Avgiftsklassifisering ---

    def validate_input(char, value_if_allowed):
        if char in '0123456789' or value_if_allowed == '':
            try:
                if value_if_allowed != '':
                    int(value_if_allowed)
                return True
            except ValueError:
                return False
        return False

    validate_input_wrapper = root.register(validate_input)

    avgiftskode_frame = ttk.Frame(frame1)
    avgiftskode_frame.pack(side=tk.TOP, pady=50)

    avgiftskode1_label = ttk.Label(
        avgiftskode_frame, text="Avgiftsklassifisering", font=("Arial", 16, "bold"))
    avgiftskode1_label.grid(row=0, column=0, columnspan=2, pady=15)

    avgiftskode_label = ttk.Label(avgiftskode_frame, text="Avgiftskode:")
    avgiftskode_label.grid(row=1, column=0, padx=5, pady=5)
    avgiftskode_entry = ttk.Entry(avgiftskode_frame, width=10, justify='center',
                                  validate='key',
                                  validatecommand=(validate_input_wrapper, '%S', '%P'))
    avgiftskode_entry.grid(row=1, column=1, padx=5, pady=5)

    sittepl_label = ttk.Label(avgiftskode_frame, text="Sitteplasser Norsk Godkjenning:")
    sittepl_label.grid(row=2, column=0, padx=5, pady=5)
    sitteplasserNorskGodkjenning_entry = ttk.Entry(avgiftskode_frame, width=10, justify='center',
                                                   validate='key',
                                                   validatecommand=(validate_input_wrapper, '%S', '%P'))
    sitteplasserNorskGodkjenning_entry.grid(row=2, column=1, padx=5, pady=5)

    sengepl_label = ttk.Label(avgiftskode_frame, text="Sengeplasser Campingbil:")
    sengepl_label.grid(row=3, column=0, padx=5, pady=5)
    sengeplasserCampingbil_entry = ttk.Entry(avgiftskode_frame, width=10, justify='center',
                                             validate='key',
                                             validatecommand=(validate_input_wrapper, '%S', '%P'))
    sengeplasserCampingbil_entry.grid(row=3, column=1, padx=5, pady=5)

    sitteplasserNorskGodkjenning_entry.insert(0, "0")
    avgiftskode_entry.insert(0, "0")
    sengeplasserCampingbil_entry.insert(0, "0")

    # --- Execute / Delete buttons ---

    nested_frame = ttk.Frame(frame1, relief='solid', borderwidth=0)
    nested_frame.pack(side=tk.TOP, pady=5)

    def execute():
        file_path = file_entry.get()
        iviref_uid = ivi_entry.get()
        new_vin = vin_entry.get()

        if not file_path or not iviref_uid:
            result_text.set("File path or IVI Reference ID cannot be empty.")
            return

        if svc.check_if_exists_in_database("ivi", iviref_uid) or svc.check_if_exists_in_database("vin", new_vin):
            result_text.set("IVI Reference ID or VIN already exists in the database.")
            return

        user_response = messagebox.askyesno(
            "Confirmation", "Er du sikker på at alt er riktig? Ja eller Nei")
        if not user_response:
            result_text.set("User cancelled the operation.")
            return

        new_file_path = svc.update_ivi_reference_in_xml(file_path, iviref_uid)
        svc.update_vehicle_identification_number(new_file_path, new_vin)
        if not isinstance(new_file_path, str) or not new_file_path:
            result_text.set("Failed to update XML.")
            return

        print(f"Debug: The new_file_path after updating is {new_file_path}")

        status, response = svc.fetch_vegvesen_data(
            new_file_path, iviref_uid,
            avgiftskode_entry.get(),
            sitteplasserNorskGodkjenning_entry.get(),
            sengeplasserCampingbil_entry.get()
        )
        result_text.set(status)
        set_response_text(response)
        populate_table()
        time.sleep(2)

    execute_button = ttk.Button(
        nested_frame, text="Send inn til Vegvesen", command=execute, bootstyle='warning')
    execute_button.grid(row=0, column=0, pady=(10, 20), padx=(0, 10), sticky="w")

    def delete_entry():
        selected_items = table.selection()
        if not selected_items:
            set_response_text("Ingen rader er valgt.")
            return

        selected_item = table.selection()[0]
        vin_to_delete = table.item(selected_item, 'values')[1]

        confirm = messagebox.askyesno(
            "Bekreftelse", f"Sikker på at du vil slett VIN: {vin_to_delete}?")
        if not confirm:
            return

        success, status_code, pretty_response = svc.delete_vegvesen_entry(vin_to_delete)
        if success:
            populate_table()
            set_response_text(
                f"Deleted entry with VIN: {vin_to_delete}\nServer Response: {pretty_response}")
        else:
            set_response_text(
                f"Failed to delete entry with VIN: {vin_to_delete}. "
                f"HTTP Status Code: {status_code}\nServer Response: {pretty_response}")

    delete_button = ttk.Button(
        nested_frame, text="Slett fra Vegvesen", command=delete_entry, bootstyle='danger')
    delete_button.grid(padx=5, pady=5)

    # ==================== Frame 3: Table & Response ====================

    table_and_search_frame = ttk.Frame(frame3)
    table_and_search_frame.pack(fill=tk.BOTH, expand=True)

    table_scrollbar = ttk.Scrollbar(table_and_search_frame, orient="vertical")
    table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    table = ttk.Treeview(table_and_search_frame, height=30,
                         columns=("iviReferanse", "understellsnummer", "datoTid", "meldingstekst"),
                         yscrollcommand=table_scrollbar.set, show='headings')
    table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    table.heading("iviReferanse", text="IVI Reference")
    table.heading("understellsnummer", text="Understellsnummer")
    table.heading("datoTid", text="Dato")
    table.heading("meldingstekst", text="Meldingstekst")

    table.column("iviReferanse", width=200, anchor="center")
    table.column("understellsnummer", width=200, anchor="center")
    table.column("datoTid", width=100, anchor="center")
    table.column("meldingstekst", width=600, anchor="center")

    table_and_boxes_frame = ttk.Frame(frame3)
    table_and_boxes_frame.pack(fill=tk.BOTH, expand=True)

    search_frame = ttk.Frame(table_and_search_frame)
    search_frame.pack(side=tk.BOTTOM, fill=tk.X)

    search_entry = ttk.Entry(search_frame, width=10)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def on_search():
        for row in table.get_children():
            table.delete(row)
        for row in svc.search_responses(search_entry.get()):
            if all(row):
                formatted_date = svc.format_date(row[2])
                table.insert('', tk.END, values=(row[0], row[1], formatted_date, row[3]))

    search_button = ttk.Button(search_frame, bootstyle="warning",
                               text="Søk", command=on_search)
    search_button.pack(side=tk.RIGHT)

    # --- Response & IVI doc text boxes ---

    response_and_ividoc_frame = ttk.Frame(table_and_boxes_frame)
    response_and_ividoc_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(30, 0))

    result_text = tk.StringVar()
    result_label = ttk.Label(response_and_ividoc_frame, textvariable=result_text)
    result_label.pack(side=tk.TOP, fill=tk.X)
    result_text.set("Respons fra Vegvesen:")

    response_scrollbar = ttk.Scrollbar(response_and_ividoc_frame, orient="vertical")
    response_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    response_text = tk.Text(response_and_ividoc_frame, wrap=tk.WORD, width=50,
                            height=20, state=tk.DISABLED)
    response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    response_text.config(yscrollcommand=response_scrollbar.set)
    response_scrollbar.config(command=response_text.yview)

    ividoc_scrollbar = ttk.Scrollbar(response_and_ividoc_frame, orient="vertical")
    ividoc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    ividoc_text = tk.Text(response_and_ividoc_frame, wrap=tk.WORD, width=50,
                          height=20, state=tk.DISABLED)
    ividoc_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    ividoc_text.config(yscrollcommand=ividoc_scrollbar.set)
    ividoc_scrollbar.config(command=ividoc_text.yview)

    def set_response_text(text):
        response_text.config(state=tk.NORMAL)
        response_text.delete(1.0, tk.END)
        response_text.tag_configure('success', foreground='green', font=('Arial', 12, 'bold'))
        response_text.tag_configure('failure', foreground='red', font=('Arial', 12, 'bold'))

        if "HTTP Status Code: 200" in text:
            response_text.insert(tk.END, text.split("\n")[0] + "\n", 'success')
        else:
            response_text.insert(tk.END, text.split("\n")[0] + "\n", 'failure')

        response_text.insert(tk.END, "\n".join(text.split("\n")[1:]))
        response_text.config(state=tk.DISABLED)

    def populate_table():
        for row in table.get_children():
            table.delete(row)
        for row in svc.get_all_responses():
            if all(row):
                formatted_date = svc.format_date(row[2])
                table.insert('', tk.END, values=(row[0], row[1], formatted_date, row[3]))
            else:
                print("Skipping row with empty or None fields.")

    def on_table_select(event):
        try:
            item = table.selection()[0]
            selected_row = table.item(item, 'values')
            iviReferanse = selected_row[0]
            understellsnummer = selected_row[1]

            ivi_entry.delete(0, tk.END)
            ivi_entry.insert(0, iviReferanse)

            vin_entry.delete(0, tk.END)
            vin_entry.insert(0, understellsnummer)

            ividoc_text.config(state=tk.NORMAL)
            ividoc_text.delete(1.0, tk.END)
            ividoc_data = svc.get_ividoc_by_vin(understellsnummer)
            if ividoc_data:
                ividoc_text.insert(tk.END, ividoc_data)
            ividoc_text.config(state=tk.DISABLED)
        except IndexError:
            print("No row selected.")

    table.bind('<ButtonRelease-1>', on_table_select)
    table.bind('<<TreeviewSelect>>', on_table_select)

    table_scrollbar.config(command=table.yview)

    # ==================== Tab 2: Settings ====================

    # --- Environment selector ---
    env_frame = ttk.LabelFrame(tab2, text="Environment")
    env_frame.pack(fill="x", padx=20, pady=(20, 10), ipadx=10, ipady=10)

    env_var = tk.StringVar(value=svc.get_environment())

    def on_env_change():
        selected = env_var.get()
        if selected == "Production":
            confirm = messagebox.askyesno(
                "Warning",
                "You are switching to the PRODUCTION environment.\n"
                "Submissions will create real registrations.\n\nAre you sure?")
            if not confirm:
                env_var.set("Test")
                return
        svc.set_environment(selected)
        env_status_label.config(
            text=f"Active: {selected}",
            bootstyle='danger' if selected == "Production" else 'success')
        populate_settings_fields()

    env_test_rb = ttk.Radiobutton(
        env_frame, text="Test (synt.utv.vegvesen.no)",
        variable=env_var, value="Test", command=on_env_change, bootstyle='success')
    env_test_rb.pack(side='left', padx=(10, 20), pady=5)

    env_prod_rb = ttk.Radiobutton(
        env_frame, text="Production (vegvesen.no)",
        variable=env_var, value="Production", command=on_env_change, bootstyle='danger')
    env_prod_rb.pack(side='left', padx=(0, 20), pady=5)

    env_status_label = ttk.Label(env_frame, text=f"Active: {svc.get_environment()}",
                                 bootstyle='success')
    env_status_label.pack(side='left', padx=10, pady=5)

    samarbeidsportalen_frame = ttk.LabelFrame(tab2, text="Samarbeidsportalen")
    samarbeidsportalen_frame.pack(fill="x", padx=20, pady=20, ipadx=10, ipady=10)

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

    def populate_settings_fields():
        settings = svc.load_settings_from_db()
        entries = [
            (issuer_entry, "issuer"),
            (audience_entry, "audience"),
            (resource_entry, "resource"),
            (scope_entry, "scope"),
        ]
        for entry, key in entries:
            entry.delete(0, tk.END)
            if settings:
                entry.insert(0, settings[key])

    def on_save_settings():
        svc.save_settings_to_db(
            issuer_entry.get(),
            audience_entry.get(),
            resource_entry.get(),
            scope_entry.get(),
        )
        populate_settings_fields()

    save_button = ttk.Button(samarbeidsportalen_frame,
                             text="Save Settings", command=on_save_settings)
    save_button.pack(padx=10, pady=10)

    populate_settings_fields()

    # ==================== Tab 3: JWT Keygen ====================

    frame3_tab3 = ttk.Frame(tab3)
    frame3_tab3.pack(side='left', fill='both', expand=True, padx=20, pady=20)

    def on_generate_jwt():
        jwk_output = svc.generate_keypair()
        jwt_output_text.delete(1.0, tk.END)
        jwt_output_text.insert(tk.END, "Public key in JWK format:\n")
        jwt_output_text.insert(tk.END, jwk_output)

    jwt_button = ttk.Button(
        frame3_tab3, text="Generate JWT Key", command=on_generate_jwt, bootstyle='info')
    jwt_button.pack(pady=(10, 20))

    jwt_output_text = tk.Text(frame3_tab3, wrap='word', width=50, height=10)
    jwt_output_text.pack()

    # ==================== Tab 4: Certificate Import ====================

    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="Certificate Import")

    cert_frame = ttk.LabelFrame(tab4, text="Import .p12 Certificate")
    cert_frame.pack(fill="x", padx=20, pady=20, ipadx=10, ipady=10)

    p12_file_label = ttk.Label(cert_frame, text="P12 File:")
    p12_file_label.pack(pady=(10, 0))

    p12_file_entry = ttk.Entry(cert_frame, width=50, justify='center')
    p12_file_entry.pack()

    def browse_p12():
        path = filedialog.askopenfilename(
            title="Select .p12 Certificate",
            filetypes=[("PKCS12 files", "*.p12"), ("PFX files", "*.pfx"), ("All files", "*.*")])
        if path:
            p12_file_entry.delete(0, tk.END)
            p12_file_entry.insert(0, path)

    p12_browse_button = ttk.Button(
        cert_frame, text="Browse", command=browse_p12, bootstyle='primary')
    p12_browse_button.pack(pady=(5, 10))

    p12_password_label = ttk.Label(cert_frame, text="Password:")
    p12_password_label.pack()

    p12_password_entry = ttk.Entry(cert_frame, width=50, justify='center', show='*')
    p12_password_entry.pack()

    p12_status_label = ttk.Label(cert_frame, text="", wraplength=500)
    p12_status_label.pack(pady=(10, 0))

    def on_import_p12():
        p12_path = p12_file_entry.get()
        password = p12_password_entry.get()
        if not p12_path:
            p12_status_label.config(text="Please select a .p12 file.", bootstyle='danger')
            return
        try:
            result = svc.import_p12_certificate(p12_path, password)
            p12_status_label.config(text=result, bootstyle='success')
        except Exception as e:
            p12_status_label.config(text=f"Error: {e}", bootstyle='danger')

    p12_import_button = ttk.Button(
        cert_frame, text="Import Certificate", command=on_import_p12, bootstyle='warning')
    p12_import_button.pack(pady=(10, 10))

    # --- Icon & startup ---
    icon = './img/Icon.png'
    root.iconphoto(True, PhotoImage(file=icon))

    svc.create_database()
    populate_table()
    root.mainloop()


if __name__ == '__main__':
    main_app()
