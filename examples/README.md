# Examples and explanations

Notes and comments:

- While participants use `did:web` in this example, a ledger based method that does not rely on just one unchangeable address would make more sense in the long term for resilience and transparency. This would need a smart contract that lets administrators propose changes to their DID document that must be accepted by the next higher authority (e.g., TA).
- While users use `did:pkh:tezos` in this example, a move to a fully ledger-based, Ethereum-compatible DID method seems advisable.
- Since administrator changes must be accepted by the next higher authority, that authority can keep track of at least one main contact for any given participant under the authority's responsibility.
- Since we have no existing revocation smart contract right now, the revocation entry instead refers to the base DID document of the maintainer of the revocation registry. We assume, that a service entry in the DID document points to the registry. The fragment syntax is up to DID specification.

## Trust Anchor Level

Haven can create a special participant credential for the ASCS that is not strictly necessary, but may be useful further down the line:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.reachhaven.com/HavenId/v1"
  ],
  "type": ["VerifiableCredential", "VerifiedHavenParticipant"],
  "id": "urn:uuid:576fbefb-35e8-4b71-bb1a-53d1803c86de",
  "issuer": "did:web:did.identity.reachhaven.com",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:did.identity.ascs.digital",
    "legalName": "Automotive Solution Center for Simulation e.V.",
    "legalForm": "e.V.",
    "registrationNumber": {
      "@type": "gx:VatID",
      "countryCode": "DE",
      "vatID": "DE129273398"
    },
    "duns": "313995269",
    "email": "info@asc-s.de",
    "website": "https://www.asc-s.de/",
    "legalAddress": {
      "@type": "gx:Address",
      "streetAddress": "Curiestrasse 2",
      "postalCode": "70563",
      "addressLocality": "Stuttgart",
      "countrySubdivisionCode": "DE-BW",
      "country": "DE"
    },
    "headquartersAddress": {
      "@type": "gx:Address",
      "streetAddress": "Curiestrasse 2",
      "postalCode": "70563",
      "addressLocality": "Stuttgart",
      "countrySubdivisionCode": "DE-BW",
      "country": "DE"
    },
    "termsAndConditions": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.reachhaven.com/terms/privacy_policy_2025-08-05.pdf#cidv1",
        "description": "Using Haven by vDL Digital credentials means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.reachhaven.com#revocation-registry?sid=608101d3a8430e61f60dcf1be0f42ab3ceb52b6abffb9f75b6f36c80362fc26a",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

The credential is signed by one of Haven's administrators. His key is one of the keys listed in the `did:web` document managed by Haven itself.

Along with the participant credential, the Haven administrator must also create at least one admin credential for the new trust anchor. The admin is connected to the participant be referencing the participant DID:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.reachhaven.com/HavenId/v1"
  ],
  "type": ["VerifiableCredential", "HavenVerifiedParticipantAdmin"],
  "id": "urn:uuid:9d3a0c1b-4d4e-4f9a-9b0c-1d2e3f4a5b6e",
  "issuer": "did:web:did.identity.reachhaven.com",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:pkh:tezos:NetXnHfVqm9iesp:tz1TrustAnchorAdminAddressExample",
    "adminFor": "did:web:did.identity.reachhaven.com:ascs-participant",
    "givenName": "Bert",
    "familyName": "Admin",
    "email": "bert.admin@asc-s.de",
    "address": {
      "@type": "gx:Address",
      "streetAddress": "Curiestrasse 2",
      "postalCode": "70563",
      "addressLocality": "Stuttgart",
      "countrySubdivisionCode": "DE-BW",
      "country": "DE"
    },
    "termsAndConditions": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.reachhaven.com/terms/admin_privacy_policy_2025-08-05.pdf#cidv1",
        "description": "Using Haven by vDL Digital credentials means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.reachhaven.com#revocation-registry?sid=f8b8a8150acbbbf936df9692ed7ca809c9a6a66b190149ce9d4e9557587829ec",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

## Participant Level

### Core Credentials

The ASCS as trust anchor can create arbitrary many participant credentials without Haven's approval:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.ascs.digital/SimpulseId/v1"
  ],
  "type": ["VerifiableCredential", "SimpulseIdParticipant"],
  "id": "urn:uuid:576fbefb-35e8-4b71-bb1a-53d1803c86de",
  "issuer": "did:web:did.identity.reachhaven.com:ascs-participant",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:did.identity.ascs.digital:bmw-participant",
    "legalName": "Bayerische Motoren Werke Aktiengesellschaft",
    "legalForm": "AG",
    "registrationNumber": {
      "@type": "gx:VatID",
      "countryCode": "DE",
      "vatID": "DE129273398"
    },
    "duns": "313995269",
    "email": "imprint@bmw.com",
    "website": "https://www.bmwgroup.com/",
    "legalAddress": {
      "@type": "gx:Address",
      "streetAddress": "Petuelring 130",
      "postalCode": "80809",
      "addressLocality": "München",
      "countrySubdivisionCode": "DE-BY",
      "country": "DE"
    },
    "headquartersAddress": {
      "@type": "gx:Address",
      "streetAddress": "Petuelring 130",
      "postalCode": "80809",
      "addressLocality": "München",
      "countrySubdivisionCode": "DE-BY",
      "country": "DE"
    },
    "termsAndConditions": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.ascs.digital/terms/privacy_policy_2025-08-05.pdf#cidv1",
        "description": "Using SimpulseId credentials means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.ascs.digital#revocation-registry?sid=608101d3a8430e61f60dcf1be0f42ab3ceb52b6abffb9f75b6f36c80362fc25a",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

The credential is signed by one of the ASCS's administrators. His key is one of the keys listed in the `did:web` document managed by the next higher authority, which is Haven.

Along with the participant credential, the ASCS administrator must also create at least one admin credential for the new participant. The admin is connected to the participant be referencing the participant DID:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.ascs.digital/SimpulseId/v1"
  ],
  "type": ["VerifiableCredential", "SimpulseIdParticipantAdmin"],
  "id": "urn:uuid:9d3a0c1b-4d4e-4f9a-9b0c-1d2e3f4a5b6e",
  "issuer": "did:web:did.identity.reachhaven.com:ascs-participant",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:pkh:tezos:NetXnHfVqm9iesp:tz1AdminAddressExample",
    "adminFor": "did:web:did.identity.ascs.digital:bmw-participant",
    "givenName": "Andreas",
    "familyName": "Admin",
    "email": "andreas.admin@bmw.com",
    "address": {
      "@type": "gx:Address",
      "streetAddress": "Petuelring 130",
      "postalCode": "80809",
      "addressLocality": "München",
      "countrySubdivisionCode": "DE-BY",
      "country": "DE"
    },
    "termsAndConditions": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.ascs.digital/terms/administrator_privacy_policy_2025-08-05.pdf#cidv1"
        "description": "Using SimpulseId credentials means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.ascs.digital#revocation-registry?sid=f8b8a8150acbbbf936df9692ed7ca809c9a6a66b190149ce9d4e9557587829ec",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

### Additional Credentials

Additional credentials detail the specific types of memberships. They are all signed by an ASCS admin.

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.ascs.digital/SimpulseId/v1"
  ],
  "type": ["VerifiableCredential", "AscsBaseMembershipCredential"],
  "id": "urn:uuid:7f3f7c6a-4b4d-4e9e-8f0a-9b1b2c3d4e5f",
  "issuer": "did:web:did.identity.reachhaven.com:ascs-participant",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:did.identity.ascs.digital:bmw-participant",
    "memberSince": "2023-01-01",
    "termsAndConditions": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.ascs.digital/terms/base_membership_terms_2025-08-05.pdf#cidv1",
        "description": "Using this membership credential means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.ascs.digital#revocation-registry?sid=6239c5abac53d33fff4a9babaaae70f6c71ac495cface74d26ac1e3affee8c61",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.ascs.digital/SimpulseId/v1"
  ],
  "type": ["VerifiableCredential", "AscsEnvitedMembershipCredential"],
  "id": "urn:uuid:7f3f7c6a-4b4d-4e9e-8f0a-9b1b2c3d4e5f",
  "issuer": "did:web:did.identity.reachhaven.com:ascs-participant",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:did.identity.ascs.digital:bmw-participant",
    "memberSince": "2023-01-01",
    "termsAndConditions": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.ascs.digital/terms/envited_membership_terms_2025-08-05.pdf#cidv1",
        "description": "Using this membership credential means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.ascs.digital#revocation-registry?sid=b8ca800e6cf1807ed35c682ca7c84f07df55ad53a20784fe0ee896f279a6a047",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

## User Level

A participant can create arbitrary many user credentials without TA approval:

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schema.ascs.digital/SimpulseId/v1"
  ],
  "type": ["VerifiableCredential", "SimpulseIdUser"],
  "id": "urn:uuid:6a0e7e84-2e88-4b9a-977b-9e92a6d87a0f",
  "issuer": "did:web:did.identity.ascs.digital:bmw-participant",
  "issuanceDate": "2025-08-06T10:15:22Z",
  "expirationDate": "2030-08-05T00:00:00Z",
  "credentialSubject": {
    "id": "did:pkh:tezos:NetXnHfVqm9iesp:tz1SfdVU1mor3Sgej3FmmwMH4HM1EjTzqqeE",
    "givenName": "Max",
    "familyName": "Mustermann",
    "email": "max.mustermann@bmw.com",
    "title": "Virtual Test Engineer",
    "termsOfService": [
      {
        "@type": "gx:TermsAndConditions",
        "@id": "https://media.ascs.digital/terms/privacy_policy_2025-08-05.pdf#cidv1",
        "description": "Using SimpulseId credentials means you agree to these terms."
      }
    ]
  },
  "credentialStatus": {
    "id": "did:web:did.identity.ascs.digital#revocation-registry?sid=9396f1d42a2a5eaa93a1a3211e4b0db85c8185d533b835984cd98d24ecba6440",
    "type": "CRSetEntry",
    "statusPurpose": "revocation"
  }
}
```

The credential is signed by one of the company's administrators. His key is one of the keys listed in the `did:web` document managed by the next higher authority, which is the TA.
