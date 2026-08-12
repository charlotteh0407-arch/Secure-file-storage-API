# Architecture

## System Design

The system encryptd and stores files for validated users. It follows a layered architecture structure so each layer handles a seperate part of the system. 

Architecture flow:
Client --> API --> Logic --> Database --> Storage

Each layer has individual jobs to make the code easier to understand an maintain.

Justifications: 

Security:
 This is a big focus of this project. Having different security features menas the risk of vnerablities being exploited is reduced. Examples: Broken access controls (users have access to someone elses file), secutiry attacks like path transversal attaks.
 Included security featrues like authentication (JWT) and encryption to add layers of protection to the system. Authentication ensures only valid users and uncorrupt files are allowed in the system. Encryption protects the content of the files as it prevents anyone being able to access and read from stored files. These are some exaples of the issues I have addressed using this type of architecture.

Maintainablitly: A key factor in choosing this design was its maintainability. Each layer has clear responsibilities so bugs can be easily identified when the code breaks, allowing for easy and quick fixes.

Scailability: The architecture was designed with scalability in mind, more layers can be easily added with additional featrues, e.g. more services, moving storage to cloud, and additional security (covered in security.md), even tiugh this is currently out of scope.


Break Down of Each layer:

Client Layer:
Reponisbilities:
- Handle sending requests
- Sending HTTP requests:
    POST /upload
    GET /files

API Layer:
Responsibilities:
- receiving requests from Client layer
- Validate input
- Return reponses

Logic Layer:
Responsibilites:
- Password hashing
- JWT creation
- File encryption
- Deciding user accessibility

Database layer:
Responsibilities:
- storing users and metadata

File storage Layer:
Responsibilities:
- Store encrypted files

Diagram:
```mermaid
flowchart TB
    subgraph Client Layer
        A[Client]
    end

    subgraph API Layer
        B[FastAPI endpoints]
        B1[Validate request format]
        B2[Check JWT/ Authentication]
    end

    subgraph Logic Layer
        C[Bussiness Logic]
        C1[Hash Password - bcrypt]
        C2[JWT creation/ verification]
        C3[File encryption/ decryption]
        C4[Authorization checks - owner_id match]
    end

    subgraph Database Layer
        D[(SQLAlchemy /SQLite/PastgreSQL)]
        D1[User records]
        D2[File metadata]
    end

    subgraph File Storage Layer
        E[(Encrypted File Storage)]
    end

    A -- "1. HTTP request e.g. POST / file/upload" --> B
    B -- B1
    B1 -- B2
    B2 -- "2. Token Verified" --> C
    C --> C4
    C4 -- "3. Ownership/ Permision confirmed" --> C3
    C3 -- "4. File Encrypted" --> E
    C --> D2
    D2 -- "5. File metadata saved" --> D
    D -- "6. Response Data" --> B
    B --> "7. HTTP Response, e.g. 201 Created" --> A
    ```     

Flow Example - What happens when a users uploads a file.
Client Layer: Sends a HTTP request to upload a file
API layer: Validates the file given for the upload.
Logic Layer: Constructs the meta data about the file, Encrypts the file.
Database Layer: The files meta data is stored.
File Storage Layer: Stores the encrypted file

As shown in the diagram above

Alternatives:
While designing the project multiple other structures were considered but ultimatly rejected. A monolithic structure was considered but rejected due to a lack of security. With all the logic like authentication check and file storage logic all in ine function it would be easier to introduce bugs, like a broken access control bug as there would be no clear checks forcing each file operation to perform an authorization check.A more complex architecture such as microservices was considered, which would keep the authentication checks, file storage, and meta data completly seperate asdifferent services communication over the network. While this was a good option it would work better than the layering architecture as it adds huge overheads especially as its a single-developer project. 