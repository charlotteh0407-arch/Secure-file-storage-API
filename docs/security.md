# Security

## Purpose

Security is an essential feature of a file stoarge system beacuse of the many cyber threats that it may face. The system holds sensitive information including users login details e.g. hashed passwords and email addresses and private data within files. These are desirable peices of information for hackers as they are valuable to sell or the system could be vunerable to ransomware attacks. During evey stage of development secuirity was considered and incorporated within the design. For example the layered architecture seen in the arcitecture.md was chosen partly to to support secuity design.

## Threat model

Each asset has its own threat each with the goal of gaining access to the system. I have assessed the assets and given the threats that it may face and the mitigattion for each threat.

| Assets | Threats | Mitigation |
|---|---|---|
| User Accounts | Password theft | Authentication - Hashing passwords |
| Uploaded files | Unautharised access | Authorization - Admin controls |
| API | Abuser by unautherised users | Authorization - Admin controls |
| Database | Data Leak | Hashing and salting passwords, file content not saved on database only metadata |
| Storage Folder | Direct file access | Files encrypted at rest, filenames replaced with ID. |

## Authentication

Authentication is a key feature of any system. Incorporated into the file storage system are multiple tequniques to ensure the saftey of the system. Users must log into the system in order to upload and access files. Each user may only download, edit or delete their own files so must login to idnetlify themselves and differentiate form other users.

Another techniqual feature is the salting and hashing of passwords. This adds an extra layer of protection in the event that the database is compromised as user passwords would not be saved in plain text. Therefore, not allowing easy access into the system. Salting also protects against weaker /repeated passwords as the passwords cannot be figured out by using rainbow tables.

## Authorisation
Having secure admin controls is important for the integrity of this system. Every user should only have access to the files that they uploaded and should not be able to modify of delete any other users files. If the contols are not set up correctly it can cause many issue. Some issues are users having access to the wrong information, low protection against viruses as they can more easily spread throughout the sytem with lax controls.

## Encryption
Encryption is one of the most important features of this project. This will ensure that in the case the storage file is taken or someone gains access to the server that they won't be able to understand any infrmation saved on the files. It can also be used to delay a hacker if they are looking for certian files to use for a ransomware attack as they won't be able to tell easily what each file is. This means there will be more time to detect them within the system and able to prevent attacks before they happen. The AES-256 encryption algorithm will be used for the files following industry standards. The encryption key will be stored using enviroment varivables that will have strict file permissions that can only be accessed by me.

There are two types of encryption that could be used for this system: ecrtyption in rest and ecryption in transit. Ecryption at rest will encrypt the physical data on the files when they are saved in the storage file. This will protect the clients data even if the files are stolen. Encryption in transit encrypts the files when they are being uploaded or downloaded from the server. This protects the data from being intercepted when moving across the network. This system implements encryption at rest using AES-265. Encryption in transit will not yet be implemneted (see Limitations) as HTTP deployment is out of the current scope.

## File upload security
A hacker can exploit the file upload system in multiple different ways to induce a cyber attack. Multiple preventitive measure can be taken. The ones included within this project are: 
Limiting File Sizes and Allowed File Types - Preventing executable files from reaching the server and restricting scripts or binary files from being uploaded. Large files can crash or slow down the server so no one else can use it. They may also contain malware that can be missed when scanning a large file, file scanning is currently not implemented in this project (see Limitations) but it is still important to consider.
Sanitizing File Names - Changing the names of files so that input injection attacks are prevented as the file name provided by users will not be saved on the server. For example: commands in file names cannot be run.
Validating Extensions - Strict list of allowed file extensions so executable script cannot be uploaded

## Security Limitations
This project currently does not include:

| Assets | Impacts |
|---|---|
| Rate Limiting | System is left vunerable to brute force attacks and credential surfing |
| Multi-factor Authentication | Attackers can gain quick access to accounts by brute force attacks, credential surfing, and users are vunerable to phishing scam where they input passwords |
| Antivirus scanning of uploded files | Bad files containing malicious software, ransomeware and spyware can be uploded |
| Audit Logging | Can lead to undetected breaches, and data breaches cannot be investogated |
| HTTPS deployment | The file manager cannot be accessed via a website, inconvenient for users |
| Cloud Key Managment | No key control, cannot change keys quickly if a leak happens. |


All these features would be a good addition to the project to imporve it and increase its security.

## Futrure Imporvments
If this project was to be deployed for the public to use the these are the features from the list above that should be added.

Multi-factor authentication - Adds a layer of protection to prevent hackers using stolen usernames and passwords,and limit brute force attacks.

Refresh Tokens - When the access token expires (currently after 60 minutes) the refresh token is sent to the server to get a new acccess token. This stops the user from needing to keep logging back in once the access token has expired. This also means the access token expiery time can be shortened to increase security as it will be less inconvieninet to the consumer. 

Audit Logging - To keep a log of user actions like logins, uploads, downloads, or deletion. The audit log would keep track of who performed which action, on which file, and when. Providing several benefits: Detecting unusual behaviour, investigating incidents, and regulatory compliance.
    Detecting unusual behaviour - Actions like downloading multiple files in a short period or multiple failed logins could suggest a compromised account or a brute force attempt in progress.
    Investigating incidents - if a data breach did occurr the logs provided an insite into the sequence of events which can be inestigated from
    Regulatory compliance - Under GDPR a production system containing personal data must maintain auidit logs so data breaches can be tracked and investigated. This project currently does not implement auidit logging to meet the requirments, as it is a portfolio project and will not be deployed to real users. If this was to be implimented it would need to be designed in from the start.

File Virus Scanning - Scan the files behaviour and structure and comparing it to known threats and using heuristic analysis to idnetify malicious software within the file.

Encryption Key Rotation - To increase security of the files saved as the encryption key used for files is constantly changing. A hacker would only have access to files encrypted with that specific key, if a hacker stole a key, limiting the damage. A hacker will constantly need to try and steal more keys as they change to gain access to more files, increasing there risk of being caught. Cryproanalysis relise on having enough data to find a pattern, by changing the keys there is not enough data to crack the algorithm.

Cloud Storage - Larger amounts of data require more space that cloud storage can provide at a lower cost. During development local servers are perfect as there is only test files that need to be uploaded. For more users space on the local server may run out quickly requiring more hardware to be bought which is costly. Cloud starage can be used in unison with local servers.

Docker - Makes the application easily scalable, so system dosent crash with more traffic with increased users. The above updates can be easily added to the system and reverted back to the old system if there is an issue with the update. Intorduces the ability to switch between diffrent types of storage like local servers and cloud without having to rewrite code for seperate architectures. Also allows for the system to work on both local servers and cloud storage at the same time.

Using Azure Key Vault - This is a safer way of securing the encryption keys. It will automatically track who accessed the keys and when creating audit logs and can automatically change the keys. For using this platofrom on large scale this is a good place to centerlize the keys across several platforms.