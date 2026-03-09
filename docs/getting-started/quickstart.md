# Quick Start

This guide shows you how to work with verifiable credentials in this repository.

## 1. Generate Artifacts

Generate OWL, SHACL, and JSON-LD artifacts from LinkML schemas:

```bash
make generate
```

This creates files in `artifacts/simpulseid/`:
- `*.owl.ttl` — OWL ontology definitions
- `*.shacl.ttl` — SHACL validation shapes
- `*.context.jsonld` — JSON-LD context files

## 2. Create a Credential

Example credential in `examples/simpulseid-user-credential.json`:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "./artifacts/simpulseid/simpulseid.context.jsonld"
  ],
  "type": ["VerifiableCredential", "simpulseid:UserCredential"],
  "issuer": "did:ethr:0x14a34:0x50916c8e454722d2357916d4250500102288bb03",
  "credentialSubject": {
    "id": "did:ethr:0x14a34:0x0f4Dc6903A4B92C6563DD3551421ebb7ACa7d4fC",
    "givenName": "Alice",
    "familyName": "Smith",
    "email": "alice@example.com"
  }
}
```

## 3. Validate the Credential

```bash
make validate
```

Or validate specific files:

```bash
python3 -m src.tools.validators.validation_suite \
  --run check-data-conformance \
  --data-paths examples/simpulseid-user-credential.json
```

## 4. Sign the Credential

Use the harbour-credentials library:

```python
from harbour.keys import generate_p256_keypair, p256_public_key_to_did_key
from harbour.signer import sign_vc_jose

# Generate keypair
private_key, public_key = generate_p256_keypair()
did = p256_public_key_to_did_key(public_key)

# Sign credential
signed_jwt = sign_vc_jose(credential, private_key, kid=f"{did}#{did.split(':')[-1]}")
```

## Next Steps

- [Credential Types](../credentials/index.md) — Learn about available credential types
- [Examples](../examples/index.md) — Browse example credentials
- [Integration](../integration/harbour.md) — Integrate with harbour-credentials
