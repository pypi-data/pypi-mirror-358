
# Heimdall-CLI

**Heimdall** is a CLI tool to **encrypt**, **upload**, **download**, and manage your files securely using **AES encryption** and a remote server backend.

🔐 Built for privacy. ⚙️ Simple to use. ☁️ Backed by a fast API.

> Server repo: [heimdall_server](https://github.com/aminmasoudi/heimdall_server)

---

## 🚀 Features

- 🔐 **Encrypt files** locally using AES before uploading
- ☁️ **Upload, download, list, and delete files** from the server
- 🔑 **Secure authentication** using JWT tokens
- 🧾 **Configuration stored locally** at `~/.config/heimdall_config.ini`
- 🛠️ Simple, consistent CLI interface

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install heimdall
```

---

## 🧪 Usage
### 🔐 Login

```bash
heimdall login --username USERNAME --password PASSWORD
```
Authenticates with the server and stores tokens for future use.

---
### 📤 Upload a File
```
heimdall upload path/to/file.txt --encrypt --key YOUR_ENCRYPTION_KEY
```
-    `--encrypt`: Optional flag to encrypt the file before upload
-    `--key`: AES key to use for encryption (must match on download)

---

### 📥 Download a File
```bash
heimdall download FILE_ID --key YOUR_ENCRYPTION_KEY
```
- `FILE_ID`: The identifier shown in heimdall list
- `--key`: Required if the file was encrypted

---

### 📄 List Your Files

```bash
heimdall list
```

Displays all your uploaded files.

---
### 🗑️ Delete a File

```bash
heimdall delete FILE_ID
```

Deletes the file from the cloud.

---

## ⚙️ Configuration

On first run, Heimdall creates a config file at:
```bash
~/.config/heimdall_config.ini
```
Sections:

- `[CloudService]`: Stores host URL and tokens

- `[Encryption]`: Stores AES settings if configured

This file is used to persist login and encryption preferences between commands.

---

## 🧱 Dependencies

- `click` – CLI command framework

- `httpx` – HTTP client for server communication

---

## 🧑 Author

**Amin Masoudi**
🔗 github.com/aminmasoudi

---

## 📄 License

MIT License. See `LICENSE` for details.

---

## TODO:
- [ ] Key flow: from where?
- [ ] Cleaning All functions
- [ ] Documentation 
- [x] Login

