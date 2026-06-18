import validators
from urllib.parse import urlparse
import socket
import ipaddress
import hashlib
import requests


class URLValidator:
    #Basic Validation
    def is_valid_url(self,url:str) -> bool:
        return bool(validators.url(url))

    #Protocol Validation
    def validate_scheme(self,url:str):
        parsed=urlparse(url)

        return parsed.scheme in ["http","https"]
    
    #block dangerous validation
    def is_private_ip(self,hostname):
        try:
            ip = socket.gethostbyname(hostname)

            return ipaddress.ip_address(ip).is_private

        except Exception:
            return True
        
    #URL Normalization
    def normalize_url(self,url):
        parsed=urlparse(url)

        scheme=parsed.scheme.lower()
        netloc=parsed.netloc.lower()
        return f"{scheme}://{netloc}{parsed.path}"
    
    #reachability check
    def check_url_accessible(self,url):
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=10
            )

            return response.status_code < 400

        except Exception:
            return False
        
    #Content type validation
    def validate_content_type(self,url):
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=10
            )

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            allowed = [
                "text/html",
                "application/pdf"
            ]

            return any(x in content_type for x in allowed)

        except:
            return False
    