# Polymorphic AES Wrapper

## 1. Concept: What is it?
Static signature-based antivirus software relies on identifying known patterns or hashes in malicious files. "Polymorphism" means the code changes its appearance every time it is generated, even if the underlying behavior remains the same.

The Polymorphic AES Wrapper takes any payload (like a PowerShell script) and encrypts it with a randomly generated AES-256 key. It then generates a unique decryption stub where all variable names are completely randomized. **Every single run produces a completely unique file hash and structure.**

## 2. Implementation: How does it work?
In `poly_engine.py`, the process works as follows:
1. `_rand_key()` and `_rand_iv()` generate 32 bytes and 16 bytes of random entropy.
2. The input payload is padded and encrypted using AES-256-CBC.
3. The CipherText (CT), Key, and IV are Base64 encoded.
4. `_rand_var()` generates random 8-character string names (e.g., `$Xa1B9cQw`).
5. A PowerShell decryption stub is dynamically assembled using these randomized variables.
6. When the script runs on the target, it rebuilds the AES object, decrypts the CT in memory, and passes the plaintext to `IEX` (Invoke-Expression) without ever touching disk.

The `--layers` argument allows wrapping the payload multiple times in nested AES decryption stubs.

## 3. Usage
**CLI Command:**
```bash
# Wrap an inline PowerShell payload
python3 hider.py poly --payload "Write-Host 'Hello'" --out unique.ps1

# Wrap an entire script file with 3 layers of encryption
python3 hider.py poly --file my_beacon.ps1 --layers 3 --out nested_beacon.ps1
```
