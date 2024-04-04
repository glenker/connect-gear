from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello World"}

#########################################
#  O                                H   #
#                                       #
#                                       #
#                                       #
#                                       #
#                  T                    #
#                                       #
#                                       #
#                                       #
#                                       #
# ^ V ####                              #
# c2                                    #
# c                                     #
#########################################

# graph background image
# engine view/map
# fragment view
# hierarchy view/map
# text version with movement, zoom, etc.
# text w/ full program on wasi
# text-core d3?
# text-core python in wasi
# text-core C in wasi
# text-core _ in wasi, ideal environment

# The OAuth 1.0 Protocol
# RFC5849: The OAuth 1.0 Protocol
# The OAuth 2.0 Authorization Framework
# RFC6749: The OAuth 2.0 Authorization Framework
# RFC6750: The OAuth 2.0 Authorization Framework: Bearer Token Usage
# RFC7009: OAuth 2.0 Token Revocation
# RFC7523: JWT Profile for OAuth 2.0 Client Authentication and Authorization Grants
# RFC7591: OAuth 2.0 Dynamic Client Registration Protocol
# RFC7592: OAuth 2.0 Dynamic Client Registration Management Protocol
# RFC7636: Proof Key for Code Exchange by OAuth Public Clients
# RFC7662: OAuth 2.0 Token Introspection
# RFC8414: OAuth 2.0 Authorization Server Metadata
# RFC8628: OAuth 2.0 Device Authorization Grant
# Javascript Object Signing and Encryption
# RFC7515: JSON Web Signature
# RFC7516: JSON Web Encryption
# RFC7517: JSON Web Key
# RFC7518: JSON Web Algorithms
# RFC7519: JSON Web Token
# RFC7638: JSON Web Key (JWK) Thumbprint
#  RFC7797: JSON Web Signature (JWS) Unencoded Payload Option
# RFC8037: ECDH in JWS and JWE
#  draft-madden-jose-ecdh-1pu-04: Public Key Authenticated Encryption for JOSE: ECDH-1PU
# OpenID Connect 1.0
#  OpenID Connect Core 1.0
#  OpenID Connect Discovery 1.0