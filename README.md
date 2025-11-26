# DEMIM Credentials

## Content

A public repository containing examples for (verifiable) credentials, associated json-ld context definitions and json manifests. The crendetials are used in the [Decentralized Digital Membership Management](https://identity.ascs.digital).
The DID of issuers and subjects and the UUIDs of the credentials have been aligned with the content of the following example [revocation registry](https://better-call.dev/ghostnet/KT1PZFXebyGvRFG8enbuVL9nrvTi4krYqeKt/storage.)

## Examples

There are two types of json-ld examples for the credentials. The member credentials and the user credential. The member credential is used to e.g. register a company with an application like e.g. [Simpulse](https://simpulse.de) for creating the company profile with minimal validated information. The user credential is used in asc(s ecosystem applications to set initial rights and roles.
The examples are once given with an external context definition and also with the attributes defined inline in the credential context itself. This is necessary as third-party libraries like [didkit](https://github.com/spruceid/didkit) do not allow external context loading due to security implications.

## Manifests

The manifest files are provided to render an identity card in a SSI wallet like e.g. [altme](https://altme.io) according to the identity foundation [wallet rendering specification](https://identity.foundation/wallet-rendering/).

## Todos

The context json files need to be hosted at <https://schema.ascs.digital/SimpulseId/v1>.
All terms need to be hosted as .pdf files at <https://media.ascs.digital/terms/>.

## Resources

* [Implementation Guide](https://www.w3.org/TR/vc-imp-guide/#creating-new-credential-types)
* [w3c credentials v1](https://www.w3.org/2018/credentials/v1)
* [w3c vc-json-schema](https://w3c.github.io/vc-json-schema/)
* [json schema specification](https://json-schema.org/specification)
* [public schemas](https://schema.org/)
* [transform tools](https://transform.tools/)
* [json-ld best practices](https://w3c.github.io/json-ld-bp/?specStatus=ED)
* [version 4 uuid](https://www.uuidgenerator.net/version4)
* [module: pkh-tezos](https://did.js.org/docs/api/modules/pkh_tezos/)
* [did-pkh-method-draft](https://github.com/w3c-ccg/did-pkh/blob/main/did-pkh-method-draft.md)
* [Multiassets](https://multiformats.io/)
* [Content Identifier (CID)](https://docs.ipfs.tech/concepts/content-addressing/#what-is-a-cid)
* [POC Content Identifier](https://github.com/GAIA-X4PLC-AAD/poc-ipfs-content-identifier)
* [GaiaX Credential Format](https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/24.07/credential_format/#verifiable-credential)
