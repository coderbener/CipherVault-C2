# CipherVault-C2

A remote-controlled AES-based file encryption system with real-time file monitoring, secure command execution, and audit logging.

---

## Core Objectives

- **Secure File Handling:** Protect sensitive files using AES-based symmetric encryption with integrity verification.  
- **Remote Command Execution:** Enable encryption and decryption of files through a Telegram-based control interface.  
- **Real-Time File Detection:** Monitor a target directory and notify the user when new files are added.  
- **Audit Logging:** Maintain logs of all encryption and decryption activities for traceability and analysis.  

---

## Tech Stack & Environment

- **Operating System:** macOS (Unix-based systems supported)  
- **Language & IDE:** Python 3 | Visual Studio Code (VS Code)  

### Core Libraries

- `cryptography (Fernet)` — AES-128 encryption with built-in authentication  
- `watchdog` — Real-time file system monitoring (FSEvents on macOS)  
- `pyTelegramBotAPI (telebot)` — Remote command execution via Telegram  
- `python-dotenv` — Secure environment variable management  

---

## System Design & Architecture

### Monitoring Engine

Utilizes `watchdog.observers.Observer` to continuously monitor a predefined confidential directory.  
A custom handler filters irrelevant files (hidden/system files and already encrypted `.enc` files) and triggers alerts on valid file creation events.  

---

### Encryption Workflow

Upon receiving a `/lock` command via Telegram, the system:

- Reads the raw file data  
- Encrypts it using Fernet (AES-128 + HMAC)  
- Stores the encrypted output as a `.enc` file  
- Deletes the original plaintext file  

---

### Decryption Workflow

When `/unlock` is issued:

- The encrypted file is read and decrypted  
- The original file is restored  
- The encrypted version is securely removed  

---

### Command & Control Layer

The Telegram bot acts as a secure remote interface.  
Only authorized chat IDs can issue commands, preventing unauthorized access.  

---

### Audit Logging System

All operations (file detection, encryption, decryption, errors) are logged into `Vault_Audit.log` with timestamps, enabling forensic tracking and debugging.  

---

## Project Outcomes

The system successfully demonstrates:

- Real-time detection of newly added files  
- Secure AES-based encryption and decryption via remote commands  
- Controlled access using a Telegram bot interface  
- Reliable logging of all critical operations  
