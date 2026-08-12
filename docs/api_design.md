## API Design

## Purpose
This document defines how each endpoint behaves, what it requires and what it returns.
Built with FastAPI, JWT for authentication, and SQLAlchemy for metadata persitence.

## Authentication
All endpoints except /register and /login require a valid JWT, sent as:
    Authorization: Bearer <token>

POST/register: creates a new user account

Request body:
{
    "email": user@email.com
    "password": plaintext-password
}

Per the securtity.md, Authentication section the password is hashed and salted using bcrypt before storage and the plaintext password is never saved.

Responses:
HTTP status code        Meaning
201                     Account created
400                     Invalid email/ weak password
409                     Email already registered

POST/login:Authenticates a user and issues a JWT

Request body:
{ 
    "email": user@email.com
    "password": plaintext-password

}

Response:
HTTP status code        Meaning
200                     Correct credentials --> Returns {"access token": "...", "token_type": "bearer"}
401                     Invalid credentials

The 401 response uses the same message for either an incorrect email or password. This prevents user enumeration - addressed in the "Password theft" threat listed against User Accounts in the security.md.

Token Contents
JWT payloads includes, at minimum:

{
    "sub": "<user_id>",
    "exp": "<expiry timestamp>"
}

The token will expire every 60 minutes, this is a long time but without refresh tokens it is the comprimise between security and the users experience as they dont want tohave to re-login every 15 minutes. Refresh tokens is future improvement in the security.md.

Any request that has a missing, malformed, or expired tokens recives a 401 Unothorized before moving onto the logic layer.

## Authorization

Every user should only have access to the files that uploaded as stated in the secuity.md. Every file specific endpoint enforces this by:

file.owner_id == token.sub

If a user requests a file they do not own, the API returns a 404 Not Found error. 404 was chose instead of a 403 deliberatly as retruning a 403 confirms that the file does exist but the user cannot access it. This is a small infomation leak. The user only need to know the information that the file dosnet exist and not if it exists and is not available for them, this supports the Unorthorise Access threat entry for Uploaded files in the security.md.

## Endpoints
POST/file/upload
Uploads and encrypts a file, matching the flow of the diagram in the README.md

Request: multipart/ form-data, field name = file
Server-side validation, in order:
1. Check file size against the maximum limit (25 MB)
2. Check the file extension against the allowed list (jpg, pdf, docx, mp4)
3. Check the contents of the file/ magic bytes to ensure they match the given extension
4. Generate a new server-side storgae filename/ID - the given filename is never used to prevents path transversal and injection attakcs via file name
5. Encrypt the file (at rest) before passing onto the storage layer
6. Extract the metadata by SQLAlchemy (original filename, size, MIME type, owner_ID, storage key, created_at)

Response:
{
    "id": "generated_id",
    "filename": "original_name.extension",
    "size": file_size as integer
    "uploaded_at": "2026-08-05T12:00:00Z"
}

HTTP status code        Meaning
201                     Upload successful
400                     File too large/ disallowed type/ failed contnet validation
401                     Missing /invalid token

GET /files
Lists the metadata of all the files of a authrosied user. A query always has a limit clause by the user_id; there is no endpoint that lists another users files.

Response:
[
    {"id": "uuid", "filename": "file.extension", "size": file_size integer, "uploaded_at": "..."}
]

GET/files/{id}
Returns file metadata and streams the decrypted file content, after the ownership check above.
HTTP status code        Meaning
200                     File returned
404                     File not found
401                     Missing/ invalid token

Error response format
When an error is thrown the message is kept generic and dosent give away any internal information on the cause of the error (SQL errors, file paths, administrative errors)
Display message:
{
    "details": "message"
}


## Gaps
In line with security limitations in security.md, this API does not implement:
    Rate limiting (repeated /login attempts)
    Multifactor authentication
    Anitivirus/ malware scanning of uploaded files
    Audit logging of uploads / downloads/ delets
    HTTPs enforcment - encryption in transit is not implemented.

## Example Upload Flow
Request
POST/ api/v1/files/upload
Authorization: Bearer ery23jfla9snf-hfe-he1
Content Type: multipart/form-data

file = report.pdf

Success response: 201
{
    "id": 4rjpo8hv9nebv93-uir
    "filename": report.pdf
    "size": 10345,
    "uploaded_at": "2026-08-06T12:00:00Z
}
Failure response: 404
{
    Detail: "File not found"
}
