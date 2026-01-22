# SimpulseID

## Implementation Choice: Address Property Aliasing

To ensure consistency with the Verifiable Credentials Data Model and other CamelCase properties in the Gaia-X ecosystem (e.g., `gx:countryCode`), this model aliases standard vCard address properties to CamelCase keys in the JSON-LD payload.

- `streetAddress` -> `vcard:street-address`
- `postalCode` -> `vcard:postal-code`
- `locality` -> `vcard:locality`

This decouples the JSON interface from specific ontology predicates and maintains a uniform style across the credential payload.
