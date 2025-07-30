import sys
import subprocess

# Ensure 'requests' is available
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import tempfile
import os
import uuid
import asyncio
import httpx
import json
from urllib.parse import urljoin

class NuveproRunner:
    def __init__(self, config):
        self.workspace_dir = tempfile.mkdtemp(prefix="nuvepro_")
        self.session_id = str(uuid.uuid4())
        self.config = config
        self.run_url = config.get("baseurl", "http://localhost:9999/")

        auth_result = asyncio.run(authenticate_cloudlab(self.config))
        if auth_result.get("status") == "failed":
            raise Exception(f"Authentication failed: {auth_result['error']}")

        self.token = auth_result.get("token")
        self.session_name = auth_result.get("session_name")
        self.sessid = auth_result.get("sessid")
        self.config.update({
            "token": self.token,
            "session_name": self.session_name,
            "sessid": self.sessid
        })

        print(f"NuveproRunner initialized (session: {self.session_id})")

        subscription_id = asyncio.run(create_Lab(self.config))
        self.subscription_id = subscription_id
        self.config["subscription_id"] = subscription_id

        launch_result = asyncio.run(get_launch_details_with_retry(self.config))
        if launch_result.get("status") == "failed":
            raise Exception(f"Launch failed: {launch_result['error']}")

        self.vm_details = launch_result.get("data")
        user_access_raw = launch_result.get("data", {}).get("userAccess")

        if not user_access_raw:
            raise Exception("Missing userAccess in launch result")

        try:
            user_access_list = json.loads(user_access_raw)
        except json.JSONDecodeError:
            raise Exception("Failed to parse userAccess JSON")

        server_dns = None
        for item in user_access_list:
            if item.get("key") == "ServerDNSName":
                server_dns = item.get("value")
                break

        if not server_dns:
            raise Exception("ServerDNSName not found in userAccess")

        self.run_url = f"http://{server_dns}:8000"

    def exc_file_code(self, filepath: str):
        url = urljoin(self.run_url, "/exc_file_code")
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {
                "success": False,
                "output": f"Could not read file: {str(e)}",
                "exit_code": -1
            }

        payload = {
            "filename": filename,
            "content": content
        }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return {
                "success": data.get("success", False),
                "output": data.get("output", ""),
                "exit_code": data.get("exit_code", -1)
            }
        except requests.Timeout:
            return {"success": False, "output": "Timeout", "exit_code": -1}
        except requests.RequestException as e:
            return {"success": False, "output": f"Error: {str(e)}", "exit_code": -1}

    def run_code(self, code: str):
        url = urljoin(self.run_url, "/run_code")
        payload = { "code": code }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return {
                "success": data.get("success", False),
                "output": data.get("output", ""),
                "exit_code": data.get("exit_code", -1)
            }
        except requests.Timeout:
            return {"success": False, "output": "Timeout", "exit_code": -1}
        except requests.RequestException as e:
            return {"success": False, "output": f"Error: {str(e)}", "exit_code": -1}

    def exec(self, command: str, cwd=None, timeout=10):
        url = urljoin(self.run_url, "/exec_command")
        payload = {
            "command": command,
            "cwd": cwd,
            "timeout": timeout
        }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return {
                "success": data.get("success", False),
                "output": data.get("output", ""),
                "exit_code": data.get("exit_code", -1)
            }
        except requests.Timeout:
            return {"success": False, "output": "Timeout", "exit_code": -1}
        except requests.RequestException as e:
            return {"success": False, "output": f"Error: {str(e)}", "exit_code": -1}

    def upload_file(self, path: str, content: bytes):
        url = urljoin(self.run_url, "/upload_file")
        payload = {
            "path": path,
            "content": content.decode("utf-8")
        }

        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return {
                "success": data.get("success", False),
                "output": data.get("output", ""),
                "exit_code": data.get("exit_code", 0)
            }
        except requests.Timeout:
            return {"success": False, "output": "Timeout", "exit_code": -1}
        except requests.RequestException as e:
            return {"success": False, "output": f"Error: {str(e)}", "exit_code": -1}

    def cleanup(self):
        try:
            for f in os.listdir(self.workspace_dir):
                os.remove(os.path.join(self.workspace_dir, f))
            os.rmdir(self.workspace_dir)
            print("Temporary workspace cleaned up.")
        except Exception as e:
            print(f"Cleanup failed: {e}")

# ------------------------ Async Support Functions ----------------------------

async def authenticate_cloudlab(config):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "username": config.get("userName"),
        "password": config.get("password")
    }

    login_url = f'{config.get("baseurl")}v1/users/login'
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(login_url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "session_name": data.get("session_name"),
                "sessid": data.get("sessid"),
                "token": data.get("token")
            }
        except httpx.RequestError:
            return {"status": "failed", "error": "Request error"}
        except httpx.HTTPStatusError as exc:
            return {"status": "failed", "error": f"HTTP error {exc.response.status_code}"}

async def create_Lab(config: dict):
    cookies = {config.get("session_name"): config.get("sessid")}
    headers = {
        "X-CSRF-Token": config.get("token"),
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    payload = {
        "planId": config.get("planId"),
        "userName": 'user_20250609_143527@cloudlab.com',
        "companyId": config.get("companyId"),
        "teamId": config.get("teamId", 53)
    }

    url = f'{config.get("baseurl")}v1/subscriptions'
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(url, headers=headers, data=payload, cookies=cookies)
            response.raise_for_status()
            result = response.json()
            return result.get("subscriptionId") or result.get("subscriptionIds", [None])[0]
        except httpx.RequestError:
            return {"status": "failed", "error": "Lab creation failed: Request error"}
        except httpx.HTTPStatusError as exc:
            return {"status": "failed", "error": f"Lab creation failed: HTTP error {exc.response.status_code}"}

async def get_launch_details_with_retry(config, max_retries=500, retry_delay=60):
    cookies = {config.get("session_name"): config.get("sessid")}
    headers = {
        "X-CSRF-Token": config.get("token"),
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    payload = {"subscriptionId": config.get("subscription_id")}
    url = f"{config.get('baseurl')}v1/subscriptions/launch"

    async with httpx.AsyncClient(verify=False) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(url, headers=headers, data=payload, cookies=cookies)
                response.raise_for_status()
                data = response.json()
                if data.get("userAccess") and data["userAccess"] != "[]":
                    return {"status": "success", "data": data}
            except Exception:
                pass
            await asyncio.sleep(retry_delay)

    return {"status": "failed", "error": "Failed to retrieve valid lab details after retries"}
