import os
from jose import jwt
import requests
import uuid
from time import time
import sqlite3


def create_database():
    conn = None
    try:
        print("Creating database...")
        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS samarbeidsportalen (
            environment TEXT,
            issuer TEXT,
            audience TEXT,
            resource TEXT,
            scope TEXT
        )
        """)
        conn.commit()
        print("Database created successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


def load_config_from_db(environment=None):
    try:
        print("Loading configuration from database...")
        conn = sqlite3.connect('vegvesen_data.db')
        c = conn.cursor()
        if environment:
            c.execute(
                "SELECT environment, issuer, audience, resource, scope FROM samarbeidsportalen WHERE environment = ? LIMIT 1", (environment,))
        else:
            c.execute(
                "SELECT environment, issuer, audience, resource, scope FROM samarbeidsportalen LIMIT 1")
        row = c.fetchone()
        conn.close()

        if row is not None:
            print(
                f"Configuration loaded successfully for environment: {row[0]}")
            return {
                "issuer": row[1],
                "audience": row[2],
                "resource": row[3],
                "scope": row[4],
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


if not os.path.exists('virksomhet.cer'):
    with open('virksomhet.cer', 'w') as cert_file:
        cert_file.write('')
    print("Created empty virksomhet.cer — import a .p12 certificate to populate it.")


def get_access_token():
    global config
    config = load_config_from_db()
    print("Getting access token...")

    if not os.path.exists('virksomhet.cer') or os.path.getsize('virksomhet.cer') == 0:
        print("virksomhet.cer is missing or empty. Import a .p12 certificate first.")
        return "virksomhet.cer is missing or empty. Import a .p12 certificate via the Certificate Import tab."

    if not os.path.exists('private_key.pem') or os.path.getsize('private_key.pem') == 0:
        print("private_key.pem is missing or empty. Import a .p12 certificate first.")
        return "private_key.pem is missing or empty. Import a .p12 certificate via the Certificate Import tab."

    with open('virksomhet.cer', 'r') as cert_file:
        certificate_data = cert_file.read()

    x5c = [certificate_data]

    with open("private_key.pem", "r") as f:
        PRIVATE_KEY = f.read()

    # Prepare JWT header and payload
    header = {
        "alg": "RS256",
        "x5c": x5c,
        "kid": "min_egen_nokkel"  # Replace with your own key ID
    }

    print(f"Header: {header}")

    # Ensure the issued at and expiration times account for possible clock skew

    payload = {
        "aud": config['audience'],
        "scope": config['scope'],
        "iss": config['issuer'],
        "resource": config['resource'],
        "exp": int(time()) + 60,
        "iat": int(time()),
        "jti": str(uuid.uuid4()),
    }

    # Create and sign the JWT
    encoded_jwt = jwt.encode(payload, PRIVATE_KEY,
                             algorithm='RS256', headers=header)

    # Make POST request to get the access token
    #token_endpoint = payload['aud'] + 'token'
    token_endpoint = "https://test.maskinporten.no/token"

    print(f"Token endpoint: {token_endpoint}")
    
    response = requests.post(token_endpoint, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
    }, data={
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': encoded_jwt
    })

    print(payload)

    # Print out the received access token or error
    if response.status_code == 200:
        # print("Access Token:", response.json()['access_token'])
        print("Access Token Granted")
        # prints the first 10 characters of the token for checking
        print(f"Access Token: {response.json()['access_token'][:10]}...")

        return response.json()['access_token']
    else:
        print("Failed to retrieve access token:", response.content)
        # Failure status, and the error content
        return (response.content.decode('utf-8'))
