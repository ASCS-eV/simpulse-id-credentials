# Notes on the Examples

Notes and comments:

- While participants use did:web in this example, a ledger based method that does not rely on just one unchangeable address would make more sense in the long term for resilience and transparency. This would need a smart contract that lets administrators propose changes to their DID document that must be accepted by the TA.
- While users use did:pkh:tezos in this example, a move to a fully ledger-based, Ethereum-compatible DID method seems advisable for the future.
- Since administrator changes must be accepted by the TA, he can keep track of at least one main contact for any given participant.
- Since we have no existing revocation smart contract right now, the revocation entry instead refers to the base DID document of the maintainer of the revocation registry. We assume, that a service entry in the DID document points to the registry. The fragment syntax is up to DID specification.

## Participant DIDs

The participant DID documents need to be managed by ASCS because the ASCS must control what keys are listed in there as signing keys. However, it is important that these private keys never are in the hands of the ASCS, but instead always are with the respective participant admins.

## Issuance

The participant VC and one admin VC are issued by an ASCS admin and contain the ASCS DID as part of the issuer field. The admin VC is connected to the participant by referencing the participant DID.

Additional credentials detail the specific types of memberships. They are all signed by an ASCS admin and reference the participant DID.

A participant can create arbitrary many user credentials without approval. The user VCs are issued by the participant's admin and contain the participant DID in the issuer field.
