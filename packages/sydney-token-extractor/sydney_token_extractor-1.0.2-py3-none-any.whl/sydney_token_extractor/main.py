from playwright.sync_api import sync_playwright
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import json
import base64
import os

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
USER_DATA_DIR = os.path.join(
    os.environ.get('LOCALAPPDATA', ''), 
    'Microsoft', 'Edge', 'User Data', 'Default'
)
TARGET_URL = "m365Copilot/GetChats"

def log_ws_handshakes(request):
    if TARGET_URL in request.url:
        auth_header = request.headers.get("authorization")
        if auth_header:
            print("=" * 60)
            print(f"Request to: {request.url}")            
            if auth_header.lower().startswith("bearer "):
                token = auth_header[7:]
                keyName = extract_oid_from_jwt(token)
                secret = client.set_secret(keyName, token)
                print(f"Token: {token}")

            print("=" * 60)

def extract_oid_from_jwt(token):
    try:
        parts = token.split('.')
        payload = parts[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload)        
        claims = json.loads(decoded_payload)
        oid = claims.get('oid')
        return oid
        
    except Exception as e:
        print(f"Error extracting oid: {e}")
        return None

def main():
    global client
    credential = DefaultAzureCredential()
    vault_url = "https://sydneykv.vault.azure.net/"
    client = SecretClient(vault_url=vault_url, credential=credential)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            executable_path=EDGE_PATH,
            headless=False,
            args=[
                '--profile-directory=Default'
            ]
        )
        page = browser.new_page()
        page.on("request", log_ws_handshakes)
        page.goto("https://m365.cloud.microsoft/chat/?auth=2")
        page.wait_for_timeout(120000)
        browser.close()

if __name__ == "__main__":
    main()