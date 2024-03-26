import jwt
import requests
import uuid
from time import time
import sqlite3

# production link https://maskinporten.no/token	
#	Set to 'https://www.utv.vegvesen.no' for TEST and 'https://www.vegvesen.no' for PROD
#    "scope": "svv:kjoretoy/ecoc.delegert svv:kjoretoy/ecoc",

# for development
# config = {
#     "issuer": "",
#     "audience": "https://test.maskinporten.no/",
#     "resource": "https://www.utv.vegvesen.no",
#     "scope": "svv:kjoretoy/ecoc",
#     "keystore_password": "Keystore Password", # not implemented but saved in database for future use
#     "keystore_alias": "Keystore Alias", # not implemented
#     "keystore_alias_password": "Keystore Alias Password", # not implemented
# }



def create_database():
    conn = None
    try:
        print("Creating database...")
        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS samarbeidsportalen (
            issuer TEXT,
            audience TEXT,
            resource TEXT,
            scope TEXT,
            keystore_password TEXT,
            keystore_alias TEXT,
            keystore_alias_password TEXT
        )
        """)
        conn.commit()
        print("Database created successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def load_config_from_db():
    try:
        print("Loading configuration from database...")
        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM samarbeidsportalen LIMIT 1") 
        row = c.fetchone()
        conn.close()

        if row is not None:
            print("Configuration loaded successfully.")
            return {
                "issuer": row[0],
                "audience": row[1],
                "resource": row[2], 
                "scope": row[3],
                "keystore_password": row[4],
                "keystore_alias": row[5],
                "keystore_alias_password": row[6]
            }
        else:
            print("Database has no entries. Loading default configuration.")
            return {}  # Default empty config if no entries
    except sqlite3.Error as e:
        print(f"Error loading configuration: {e}")

# Create database if not exists
create_database()

# Load configurations from database
config = load_config_from_db()



with open('virksomhet.cer', 'r') as cert_file:
    certificate_data = cert_file.read()

x5c = [certificate_data]


def get_access_token():
    global config
    config = load_config_from_db()
    print("Getting access token...")
    with open("private_key.pem", "r") as f:
        PRIVATE_KEY = f.read()
        

    # Prepare JWT header and payload
    header = {
        "alg": "RS256",
        "x5c": x5c,
        #"kid": "min_egen_nokkel"
    }
    
    print(f"Header: {header}")


    payload = {
        "aud": config['audience'],
        "scope": config['scope'],
        "iss": config['issuer'],
        "resource": config['resource'],
        "exp": int(time()) + 60,
        "iat": int(time()),
        "jti": str(uuid.uuid4()),
        # "keystore_password": config['keystore_password'],
        # "keystore_alias": config['keystore_alias'],
        # "keystore_alias_password": config['keystore_alias_password']
    }


    # Create and sign the JWT
    encoded_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256', headers=header)

    # Make POST request to get the access token
    token_endpoint = payload['aud'] + 'token'
    print(f"Token endpoint: {token_endpoint}")
    #token_endpoint = "https://test.maskinporten.no/token"
    response = requests.post(token_endpoint, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
    }, data={
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': encoded_jwt
    })
    
    print(payload)

    # Print out the received access token or error
    if response.status_code == 200:
        #print("Access Token:", response.json()['access_token'])
        print("Access Token Granted")
        print(f"Access Token: {response.json()['access_token'][:10]}...")  # prints the first 10 characters of the token for checking

        return response.json()['access_token']
    else:
        print("Failed to retrieve access token:", response.content)
        return (response.content.decode('utf-8'))  # Failure status, and the error content
