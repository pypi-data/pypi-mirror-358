import subprocess
import tempfile
import os
import uuid
import requests
import asyncio
import httpx
import json
from urllib.parse import urljoin

class NuveproRunner:
    def __init__(self,config):
       
        self.workspace_dir = tempfile.mkdtemp(prefix="nuvepro_")
        self.session_id = str(uuid.uuid4())
        self.config = config

        self.run_url = config.get("baseurl", "http://localhost:9999/")
        
        # 🔐 Authenticate user and store token
         # 🔐 Authenticate user and store token
        auth_result = asyncio.run(authenticate_cloudlab(self.config))

        if auth_result.get("status") == "failed":
            raise Exception(f"Authentication failed: {auth_result['error']}")

        self.token = auth_result.get("token")
        self.session_name = auth_result.get("session_name")
        self.sessid = auth_result.get("sessid")
        self.config["token"] = self.token
        self.config["session_name"] = self.session_name
        self.config["sessid"] = self.sessid

       # Step 2: Create lab if exit take susbcriton id  if not existing
        print(f"NuveproRunner initialized (session: {self.session_id})")
        subscription_id = asyncio.run(create_Lab(self.config))
        self.subscription_id = subscription_id
        self.config["subscription_id"] = subscription_id
        
       # Call Launch api  

        launch_result = asyncio.run(get_launch_details_with_retry(self.config))
        if launch_result.get("status") == "failed":
            raise Exception(f"Launch failed: {launch_result['error']}")

        self.vm_details = launch_result.get("data") 
        # Extract userAccess from launch_result
        user_access_raw = launch_result.get("data", {}).get("userAccess")

      # Ensure user_access is not empty or malformed
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

        # Set the run URL using the DNS
        self.run_url = f"http://{server_dns}:8000"
        return
 
                  
         # Step 4: Retrieve subscription ID (based on lab or user)
        #self.run_url = "http://winpydy7730f.cloudloka.com:8000" 

       
###################################################################################

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

   ###########################################################################
    def run_code(self, code: str):
        # Prepare full endpoint
        url = urljoin(self.run_url, "/run_code")
        # Prepare request payload
        payload = {
            "code": code
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
    

    ###############################################################################
    def exec(self, command: str, cwd=None, timeout=10): 
           # Prepare full endpoint
        url = urljoin(self.run_url, "/exec_command")
          # Prepare request payload (fix: use command, cwd, timeout — not 'code')
        
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


#######################################################################################

    def upload_file(self, path: str, content: bytes):
        url = urljoin(self.run_url, "/upload_file")
        payload = {
            "path": path,
            "content": content.decode("utf-8")  # assuming content is plain UTF-8 text
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


#######################################################################
   # CleanUp Session deatis

def cleanup(self):
        try:
            for f in os.listdir(self.workspace_dir):
                os.remove(os.path.join(self.workspace_dir, f))
            os.rmdir(self.workspace_dir)
            print("Temporary workspace cleaned up.")
        except Exception as e:
            print(f"Cleanup failed: {e}")

    

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
        except httpx.RequestError as exc:
            
            return {"status": "failed", "error": "Request error"}
        except httpx.HTTPStatusError as exc:
           
            return {"status": "failed", "error": f"HTTP error {exc.response.status_code}"}
        




async def create_Lab(config: dict):
    
    session_name = config.get("session_name")
    sessid = config.get("sessid")
    csrf_token = config.get("token")

    if not all([session_name, sessid, csrf_token]):
        return {"status": "failed", "error": "Missing authentication values"}

    cookies = {session_name: sessid}
    headers = {
        "X-CSRF-Token": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }

    createLabPayload = {
        "planId": config.get("planId"),
        "userName": 'user_20250609_143527@cloudlab.com',
        "companyId": config.get("companyId"),
        "teamId": config.get("teamId",53)
    }

    CREATE_LAB_URL = f'{config.get("baseurl")}v1/subscriptions'

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                CREATE_LAB_URL,
                headers=headers,
                data=createLabPayload,
                cookies=cookies
            )
            response.raise_for_status()
            result = response.json()
            
            if "subscriptionId" in result:
                return result["subscriptionId"]
            elif "subscriptionIds" in result:
                return result["subscriptionIds"][0]  # return first if multiple
            else:
                return {"status": "failed", "error": "No subscription ID found", "response": result}

            
        except httpx.RequestError as exc:
            return {"status": "failed", "error": "Lab creation failed: Request error"}

        except httpx.HTTPStatusError as exc:
            return {"status": "failed", "error": f"Lab creation failed: HTTP error {exc.response.status_code}"}     




async def get_launch_details_with_retry(config, max_retries=500, retry_delay=60):
   
    session_name = config.get("session_name")
    sessid = config.get("sessid")
    csrf_token = config.get("token")
    subscription_id = config.get("subscription_id")

    if not all([session_name, sessid, csrf_token, subscription_id]):
        return {"status": "failed", "error": "Missing authentication/session values or subscription ID."}

    cookies = {session_name: sessid}
    headers = {
        "X-CSRF-Token": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }

    payload = {"subscriptionId": subscription_id}
    url = f"{config.get('baseurl')}v1/subscriptions/launch"

    async with httpx.AsyncClient(verify=False) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(url, headers=headers, data=payload, cookies=cookies)
                response.raise_for_status()
                data = response.json()

                user_access = data.get("userAccess")
                if user_access and user_access != "[]":
                    return {"status": "success", "data": data}

            except httpx.RequestError as exc:
                print(f"[Attempt {attempt}] Request error: {exc}")
            except httpx.HTTPStatusError as exc:
                print(f"[Attempt {attempt}] HTTP status error: {exc.response.status_code}")

            await asyncio.sleep(retry_delay)

    return {"status": "failed", "error": "Failed to retrieve valid lab details after retries"}
 