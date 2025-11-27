# Wallet Rendering Manifests for SimpulseID Credentials

This folder contains **wallet rendering manifests** for each credential type.
These files follow the **Decentralized Identity Foundation (DIF) Wallet Rendering**
specification and define how SSI wallets (such as Altme) should display the
credential to end users.

## Purpose

Manifests control:

- Title and subtitle displayed on the credential card
- Key fields shown on the card (e.g., name, organization, membership type)
- How credentials appear in credential lists and detail views
- Icons, colors, and layout options (if supported by the wallet)

All manifest files correspond 1:1 to credential types found in:

```txt
../examples/
```

and are intended for use by wallets integrated with:

**<https://identity.ascs.digital>**

## Files

### `SimpulseIdParticipantCredentialManifest.json`

Defines card rendering for Participant Credentials (gx:LegalPerson).

### `SimpulseIdAscsBaseMembershipCredentialManifest.json`

Defines rendering for ASCS Base Membership credentials.

### `SimpulseIdAscsEnvitedMembershipCredentialManifest.json`

Rendering for ENVITED Program Membership credentials.

### `SimpulseIdAdministratorCredentialManifest.json`

Rendering of administrator credentials issued by ASCS.

### `SimpulseIdUserCredentialManifest.json`

Rendering of user credentials issued by participant administrators.

## Usage

Wallets use these manifests to visually render credentials when they are:

- Added to the wallet
- Displayed in a card list
- Displayed in detail view
- Offered for presentation via OIDC4VP

They do **not** affect cryptographic validity—only **UX rendering**.
