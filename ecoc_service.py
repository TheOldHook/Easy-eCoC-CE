"""Business logic for Easy eCoC — API, database, XML, and crypto operations."""

import base64
import json
import logging
import sqlite3
import uuid
from datetime import datetime

import requests
import pyperclip
import xml.etree.ElementTree as ET
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, asymmetric
from cryptography.hazmat.primitives.serialization import pkcs12
from jose import jwk

from samarbeidsportalen import get_access_token

# Environment URLs
_ENVIRONMENTS = {
    "Test": {
        "submit": "https://synt.utv.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/innmelding/meldingompreregistrering/v1/opprette",
        "delete": "https://synt.utv.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/innmelding/meldingompreregistrering/v1/slette/understellsnummer",
    },
    "Production": {
        "submit": "https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/innmelding/meldingompreregistrering/v1/opprette",
        "delete": "https://www.vegvesen.no/ws/no/vegvesen/kjoretoy/felles/innmelding/meldingompreregistrering/v1/slette/understellsnummer",
    },
}

_current_environment = "Test"


def get_environment():
    return _current_environment


def set_environment(env_name):
    global _current_environment
    if env_name not in _ENVIRONMENTS:
        raise ValueError(f"Unknown environment: {env_name}")
    _current_environment = env_name
    print(f"Environment switched to: {env_name}")
    print(f"  Submit URL: {_ENVIRONMENTS[env_name]['submit']}")
    print(f"  Delete URL: {_ENVIRONMENTS[env_name]['delete']}")


def get_submit_url():
    return _ENVIRONMENTS[_current_environment]["submit"]


def get_delete_url():
    return _ENVIRONMENTS[_current_environment]["delete"]


DB_PATH = 'vegvesen_data.db'


# --- Database operations ---

def create_database():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
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


def create_settings_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT,
                 password TEXT)''')
    conn.commit()
    conn.close()


def load_settings_from_db():
    """Load samarbeidsportalen settings for the current environment. Returns a dict or None."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT issuer, audience, resource, scope, kid FROM samarbeidsportalen WHERE environment = ? LIMIT 1",
            (_current_environment,)
        )
        row = c.fetchone()
        if row:
            return {
                "issuer": row[0],
                "audience": row[1],
                "resource": row[2],
                "scope": row[3],
                "kid": row[4],
            }
        return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        logging.error(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def save_settings_to_db(issuer, audience, resource, scope, kid=""):
    """Save samarbeidsportalen settings for the current environment. Applies defaults for empty values."""
    if not audience:
        audience = "https://maskinporten.no/"
    if not scope:
        scope = "svv:kjoretoy/ecoc"
    if not resource:
        resource = "https://www.vegvesen.no"

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM samarbeidsportalen WHERE environment = ?",
                  (_current_environment,))
        c.execute(
            "INSERT INTO samarbeidsportalen "
            "(environment, issuer, audience, resource, scope, kid) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (_current_environment, issuer, audience, resource, scope, kid)
        )
        conn.commit()
        print(f"Settings saved for {_current_environment}.")

        from samarbeidsportalen import load_config_from_db
        load_config_from_db(_current_environment)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def check_if_exists_in_database(type_of_id, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    column_name = "iviReferanse" if type_of_id == "ivi" else "understellsnummer"
    c.execute(
        f'SELECT COUNT(*) FROM responses WHERE {column_name} = ?', (value,))
    exists = c.fetchone()[0]
    conn.close()
    return exists > 0


def get_all_responses():
    """Return all rows from the responses table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute('SELECT * FROM responses').fetchall()
    conn.close()
    return rows


def search_responses(search_term):
    """Search responses by iviReferanse or understellsnummer."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute(
        'SELECT * FROM responses WHERE iviReferanse LIKE ? OR understellsnummer LIKE ?',
        (f"%{search_term}%", f"%{search_term}%")
    ).fetchall()
    conn.close()
    return rows


def get_ividoc_by_vin(vin):
    """Fetch the IVI document for a given VIN."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ividoc FROM responses WHERE understellsnummer = ?", (vin,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def delete_response_by_vin(vin):
    """Delete a response row from the local database by VIN."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM responses WHERE understellsnummer = ?", (vin,))
    conn.commit()
    conn.close()


# --- Date formatting ---

def format_date(date_str):
    """Format an ISO date string to YYYY-MM-DD. Returns original on failure."""
    try:
        truncated = date_str.split(".")[0]
        return datetime.fromisoformat(truncated.replace('T', ' ')).strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Date formatting error: {e}")
        logging.error(f"Date formatting error: {e}")
        return date_str


# --- XML operations ---

def read_vehicle_identification_number(file_path):
    try:
        tree = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8'))
        root = tree.getroot()
        for elem in root.iter('VehicleIdentificationNumber'):
            return elem.text
    except ET.ParseError as e:
        print(f"An error occurred while parsing the XML file: {e}")
        logging.error(f"An error occurred while parsing the XML file: {e}")
        return None


def update_ivi_reference_in_xml(file_path, new_ivi_ref):
    try:
        with open(file_path, "r", encoding='utf-16-le') as f:
            print(f.read(1000))

        tree = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8'))
        root = tree.getroot()

        for elem in root.iter('IVIReferenceId'):
            elem.text = new_ivi_ref
            break

        tree.write(file_path, encoding='utf-16')
        return file_path
    except ET.ParseError as e:
        print(f"An error occurred while parsing the XML file: {e}")
        logging.error(f"An error occurred: {e}")
        return False


def update_vehicle_identification_number(file_path, new_vin):
    try:
        tree = ET.parse(file_path, parser=ET.XMLParser(encoding='utf-8'))
        root = tree.getroot()
        for elem in root.iter('VehicleIdentificationNumber'):
            elem.text = new_vin
            break
        tree.write(file_path, encoding='utf-16')
    except ET.ParseError as e:
        logging.error(f"An error occurred while parsing the XML file: {e}")
        print(f"An error occurred while parsing the XML file: {e}")


# --- Vegvesen API operations ---

def fetch_vegvesen_data(file_path, iviref_uid, avgiftskode, sitteplasser, sengeplasser):
    """Submit vehicle data to Vegvesen. Returns (status_str, response_str)."""
    print(f"Debug: The file_path is {file_path}")

    access_token = get_access_token(_current_environment)

    if access_token is None:
        logging.error("Could not get an access token.")
        return "Could not get an access token.", None

    if "error" in access_token:
        return "Could not get an access token.", access_token

    print("Access token retrieved successfully.")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    with open(file_path, "r", encoding='utf-16') as f:
        ivi_document = f.read()

    ivi_base64_encoded = base64.b64encode(ivi_document.encode()).decode()

    data = {
        "ivi": {
            "iviDokument": ivi_base64_encoded,
            "iviReferanse": iviref_uid,
        },
        "avgiftsklassifisering": {
            "avgiftsKode": avgiftskode,
            "sitteplasserNorskGodkjenning": sitteplasser,
            # "sengeplasserCampingbil": sengeplasser
        }
    }

    data_json = json.dumps(data)
    response = requests.post(get_submit_url(), headers=headers, data=data_json)
    print(response)
    print(f"Debug: Headers: {headers}")
    print(f"Debug: HTTP Status Code: {response.status_code}")
    print(f"Debug: Response Content: {response.content}")

    if response.status_code == 200:
        response_dict = json.loads(response.content)
        iviReferanse = response_dict.get(
            "iviIdentifikator", {}).get("iviReferanse", "")
        understellsnummer = response_dict.get(
            "iviIdentifikator", {}).get("understellsnummerMerke", {}).get("understellsnummer", "")
        datoTid = response_dict.get("datoTid", "")
        meldingstekst = response_dict.get(
            "melding", {}).get("meldingstekst", "")

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT INTO responses (iviReferanse, understellsnummer, datoTid, meldingstekst, IviDoc) "
                "VALUES (?, ?, ?, ?, ?)",
                (iviReferanse, understellsnummer,
                 datoTid, meldingstekst, ivi_document)
            )
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"SQLite error: {e}")
            logging.error(f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()
    else:
        return f"HTTP Status Code: {response.status_code}", f"Vegvesen Response:\n{response.content}"

    try:
        response_dict = json.loads(response.content)
        pretty_response = json.dumps(
            response_dict, ensure_ascii=False, indent=4)
    except json.JSONDecodeError as e:
        pretty_response = response.content.decode('utf-8')
        logging.error(f"An error occurred: {e}")

    return f"HTTP Status Code: {response.status_code}", f"Vegvesen Response:\n{pretty_response}"


def delete_vegvesen_entry(vin):
    """Delete an entry from Vegvesen by VIN. Returns (success, status_code, pretty_response)."""
    access_token = get_access_token(_current_environment)
    if access_token is None:
        return False, None, "Could not get an access token."

    headers = {'Authorization': f'Bearer {access_token}'}
    url = f"{get_delete_url()}/{vin}"
    response = requests.delete(url, headers=headers)

    server_response = response.text
    pretty_server_response = json.dumps(json.loads(server_response), indent=4)

    if response.status_code == 200:
        delete_response_by_vin(vin)
        return True, response.status_code, pretty_server_response
    else:
        return False, response.status_code, pretty_server_response


# --- JWT / Key generation ---

def generate_keypair():
    """Generate RSA keypair, save to files, return JWK JSON string."""
    private_key = asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    with open("private_key.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open("public_key.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    jwk_dict = jwk.construct(public_key, algorithm='RS256').to_dict()
    jwk_dict['use'] = 'sig'
    jwk_dict['kid'] = 'min_egen_nokkel'

    jwk_output = json.dumps([jwk_dict], indent=2)
    pyperclip.copy(jwk_output)
    return jwk_output


# --- Utility ---

def import_p12_certificate(p12_path, password):
    """Import a .p12 certificate, extracting private key, public key, and cert chain."""
    with open(p12_path, "rb") as f:
        p12_data = f.read()

    private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
        p12_data, password.encode("utf-8"), default_backend()
    )

    if private_key is None:
        raise ValueError("No private key found in the .p12 file.")
    if certificate is None:
        raise ValueError("No certificate found in the .p12 file.")

    # Write private key
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write public key
    public_key = certificate.public_key()
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Write full chain to virksomhet.cer (base64 DER, no BEGIN/END lines)
    all_certs = [certificate] + list(additional_certs or [])
    with open("virksomhet.cer", "w") as f:
        for cert in all_certs:
            der_bytes = cert.public_bytes(serialization.Encoding.DER)
            b64 = base64.b64encode(der_bytes).decode("ascii")
            f.write(b64 + "\n")

    return f"Imported {len(all_certs)} certificate(s).\nFiles written: private_key.pem, public_key.pem, virksomhet.cer"


def generate_ivi_ref_id():
    return str(uuid.uuid4())
