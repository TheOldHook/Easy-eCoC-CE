# Test Certificate Guide

How to generate a self-signed test certificate for the eCoC test environment.

## Prerequisites

- OpenSSL installed (`openssl version` to check)

## Quick Start

Run the provided script from the project root:

```bash
chmod +x generate_test_cert.sh
./generate_test_cert.sh
```

This generates three files in the project root:

| File | Purpose |
|---|---|
| `private_key.pem` | RSA private key used to sign JWTs for Maskinporten |
| `public_key.pem` | RSA public key for JWK registration |
| `virksomhet.cer` | Full certificate chain (base64 DER, one line per cert) |

## Manual Steps

If you prefer to run the commands yourself:

### 1. Create a Root CA

```bash
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -key rootCA.key -sha256 -days 3650 -out rootCA.pem \
  -subj "/C=NO/O=TestCompany/CN=TestCompany Root CA"
```

### 2. Create an end-entity certificate

```bash
openssl genrsa -out private_key.pem 2048
openssl req -new -key private_key.pem -out cert.csr \
  -subj "/C=NO/O=TestCompany/CN=TestCompany eCoC Test"
openssl x509 -req -in cert.csr -CA rootCA.pem -CAkey rootCA.key \
  -CAcreateserial -out cert.pem -days 365 -sha256
```

### 3. Extract the public key

```bash
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

### 4. Build `virksomhet.cer`

The app expects one base64-encoded DER certificate per line, with no `BEGIN`/`END` markers:

```bash
openssl x509 -in cert.pem -outform DER | base64 | tr -d '\n' > virksomhet.cer
echo "" >> virksomhet.cer
openssl x509 -in rootCA.pem -outform DER | base64 | tr -d '\n' >> virksomhet.cer
```

### 5. Clean up temporary files

```bash
rm -f rootCA.key rootCA.pem rootCA.srl cert.csr cert.pem
```

## Registering with Maskinporten Test

After generating the certificate:

1. Open the app and go to the **JWT Keygen** tab
2. Click **Generate JWK** to produce the JSON Web Key from your `public_key.pem`
3. Register the JWK in the [Maskinporten test dashboard](https://sjolvbetjening.test.samarbeid.digdir.no/)
4. In the **Settings** tab, select the **Test** environment and fill in issuer, audience, scope, and resource

## Using a .p12 Certificate Instead

If you already have a `.p12` file (e.g. from Buypass or Commfides test):

1. Go to the **Certificate Import** tab
2. Select your `.p12` file and enter the password
3. The app extracts `private_key.pem`, `public_key.pem`, and `virksomhet.cer` automatically

## Troubleshooting

| Problem | Solution |
|---|---|
| `virksomhet.cer is missing or empty` | Run the script or import a `.p12` via the Certificate Import tab |
| `private_key.pem is missing or empty` | Run the script or import a `.p12` via the Certificate Import tab |
| `Failed to retrieve access token` | Verify your Maskinporten test integration settings (issuer, audience, scope, resource) in the Settings tab |
| Token request returns 400 | Ensure the JWK registered in Maskinporten matches your `public_key.pem` |
