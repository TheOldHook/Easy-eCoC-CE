#!/bin/bash
# Generate a self-signed test certificate with full chain for the eCoC test environment.
# Produces: private_key.pem, public_key.pem, virksomhet.cer

set -e

SUBJECT_ROOT="/C=NO/O=TestCompany/CN=TestCompany Root CA"
SUBJECT_CERT="/C=NO/O=TestCompany/CN=TestCompany eCoC Test"

echo "=== Generating Root CA ==="
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -key rootCA.key -sha256 -days 3650 -out rootCA.pem \
  -subj "$SUBJECT_ROOT"

echo "=== Generating end-entity certificate ==="
openssl genrsa -out private_key.pem 2048
openssl req -new -key private_key.pem -out cert.csr \
  -subj "$SUBJECT_CERT"
openssl x509 -req -in cert.csr -CA rootCA.pem -CAkey rootCA.key \
  -CAcreateserial -out cert.pem -days 365 -sha256

echo "=== Extracting public key ==="
openssl rsa -in private_key.pem -pubout -out public_key.pem

echo "=== Building virksomhet.cer (base64 DER, full chain) ==="
openssl x509 -in cert.pem -outform DER | base64 | tr -d '\n' > virksomhet.cer
echo "" >> virksomhet.cer
openssl x509 -in rootCA.pem -outform DER | base64 | tr -d '\n' >> virksomhet.cer

echo "=== Cleaning up temporary files ==="
rm -f rootCA.key rootCA.pem rootCA.srl cert.csr cert.pem

echo ""
echo "Done! Files created:"
echo "  - private_key.pem"
echo "  - public_key.pem"
echo "  - virksomhet.cer"
