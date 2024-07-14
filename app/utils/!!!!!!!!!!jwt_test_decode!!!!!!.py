import base64

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

'''
AUTH0_SECRET=MRP5BAsfD2cfZWlIx1Fa6rxklRG3Kcva6YbEJUzVfZZpMbVJ6CdQlxD7ACDZ1BHt
AUTH0_DOMAIN=dev-8y2zbk3ly7hqi1x2.eu.auth0.com
AUTH0_API_AUDIENCE=https://meduzzen-app
AUTH0_ALGORITHM=HS256
ISSUER=https://dev-8y2zbk3ly7hqi1x2.eu.auth0.com/
TOKEN_EXPIRATION=240000
'''


client_secret1 = "TVJQNUJBc2ZEMmNmWldsSXgxRmE2cnhrbFJHM0tjdmE2WWJFSlV6VmZaWnBNYlZKNkNkUWx4RDdBQ0RaMUJIdA=="
client_secret2 = "MRP5BAsfD2cfZWlIx1Fa6rxklRG3Kcva6YbEJUzVfZZpMbVJ6CdQlxD7ACDZ1BHt"

algorithm = "HS256"
audience = "https://meduzzen-app"


def decode_jwt(token, secret, algo, aud):
    try:
        decoded = jwt.decode(
            token,
            secret,
            algorithms=[algo],
            audience=aud,
        )
        return decoded
    except ExpiredSignatureError:
        return "Token has expired"
    except InvalidTokenError as e:
        return f"Invalid token: {e}"


token1Auth0 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXIwNjA2dXNlckBnbWFpbC5jb20iLCJpc3MiOiJodHRwczovL2Rldi04eTJ6YmszbHk3aHFpMXgyLmV1LmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExODM4MjgyNTg4MTE2OTUyMTExNCIsImF1ZCI6WyJodHRwczovL21lZHV6emVuLWFwcCJdLCJpYXQiOjE3MjA5MzUxMzIsImV4cCI6MTcyMTAyMTUzMiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImF6cCI6InRLdDU1Mmw4UWZmdkJJQ1VKSXdLdU1qZG5Pemk2d1ZDIn0.VfC4pi0w7ICydQHGMG2GrVSxmYPHmYkiC_w0wUwQL34"
token2MyBack = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IjExMTExMTExQGdtYWlsLmNvbSIsImZyb20iOiJub2F1dGgwIiwiZXhwIjoxNzM1MzM1MDg3LCJpYXQiOjE3MjA5MzUwODcsImlzcyI6Imh0dHBzOi8vZGV2LTh5MnpiazNseTdocWkxeDIuZXUuYXV0aDAuY29tLyIsImF1ZCI6Imh0dHBzOi8vbWVkdXp6ZW4tYXBwIn0.KgqsQTAzNcFldYkJwn50ASm6VqSpAdAsQ1AuAoY_eCw"

decoded_token1 = decode_jwt(token1Auth0, client_secret1, algorithm, audience)
decoded_token2 = decode_jwt(token2MyBack, client_secret2, algorithm, audience)

print()
print("Decoded Token 1:", decoded_token1)
print()
print("Decoded Token 2:", decoded_token2)


client_secret = "MRP5BAsfD2cfZWlIx1Fa6rxklRG3Kcva6YbEJUzVfZZpMbVJ6CdQlxD7ACDZ1BHt"
encoded_secret = base64.b64encode(client_secret.encode()).decode()

print()

print(encoded_secret)
