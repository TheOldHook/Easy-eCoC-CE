from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, asymmetric
from jose import jwk
import json

# Step 1: Generate RSA key pair
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
jwk_dict['kid'] = 'min_egen_nokkel'

# Step 3: Print JWK
print("Public key in JWK format:")
print(jwk_dict)


# Wrap in a list and convert to JSON string
jwk_array_json = json.dumps([jwk_dict], indent=2)
print("Public key in JWK format as an array:")
print(jwk_array_json)