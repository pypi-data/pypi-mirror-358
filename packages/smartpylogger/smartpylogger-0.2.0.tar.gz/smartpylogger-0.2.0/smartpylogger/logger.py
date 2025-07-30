"""
FastAPI middleware for request/response logging

This logger ONLY sends POST request data to api_server.py
api_server.py handles all database operations and dashboard communication
"""

import subprocess
import os
import time
import platform
from datetime import datetime
from random import randint

# Colors for console output
from colorama import Fore, Style

import json
# import requests
import httpx # replace requests with httpx for async support & speed
from typing import Dict, Any, Optional

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint


API_URL="http://51.12.61.210:8000"  ### CHANGE TO EXTERNAL IP LATER

class ClientError(Exception):
    pass

class LoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware - intercepts requests and sends to api_server.py"""
    
    def __init__(self, app, api_key: str = "", allowed_origins: Optional[list[str]] = None, api_limit_daily: int = 1000, censored_words: Optional[list[str]] = None, banned_words_path: Optional[str] = None):
        """Initialize middleware with API credentials"""

        print(f"""{Fore.GREEN}
..............................................................................
..........................................-++=..:.............................
.............-.........................=**#######+:.........-.................
.............................-.......:=#***##**##*=.....................-.....
......-.............................:+******#**##*#=..........................
.............-...................:=*********####%##*:.........................
..............................:+************#*####=..................-........
...-*+=:.................-=****##*****####*######%+:..........................
...-*#*#**##*********##**#*******#######**#%%#***#%+..........................
...:=*****#*##*######****#*****#####*#*++--*%##***##=.........-...............
....-******###*##**###**###*#*###****+-...:-*%%#**##%-..................-.....
....:=******###*###****#**#**#####**+:......-*%##***%#-.......................
.....:+*#***##***###******##**###**+:.......:-*%##**#%*-......................
......-*#****######***#**#*##*##**+:.........:-*%#*+*#%#:.....................
......:-*******#**********#***##**-...........-:=*##***#%*:...................
........:-+#***************##**##**-............:=*##****#%*-.................
............:=*#************+*###*#+.............-=*###**#%@%#-...............
.............:-+#*************+*###*-......-......:-+*#%####%%*:..............
.......-.......:-=*#***************+.................-=*#%%%*###%=............
..................:--##*************-.................:-+*%#****#%*...........
............-.......:--+#************#..................-=*#%#**#%%%-.........
........................::*********--+:...................:-=*###***#%*.......
.../PPPP/PPPPPPPPP..........++#*****--#....................:-=+###*#%%%.......
..| PPPPPPPPPPPPPPP..............-'++-#......................:=#%#***%%+......
..| PPPP_______/PPPP..-.........................-.............:=#%#***%%+.....
..| PPPP......| PPPP..........................................:=#%#***%%+.....
..| PPPPPPPPPPPPPPP./YYYY..../YYYY........-...................:=#%#***%%+.....
..| PPPP/PPPPPPPP..| YYYY...| YYYY............................:=*%##**#%#-....
..| PPPP_______/...| YYYY...| YYYY.............................=*%%##*#%%=....
..| PPPP............( YYYYYYYYYYYY.....ooo....................=+%%%#**%%+.....
..| PPPP.............( YYYYY_/YYYY.../OOOOO....-.............:=+###**#%#:.....
../____/..............(__/..| YYYY...| OOO....................=+#%#**#%#:.....
...................../YYYY..| YYYY....(__/...................:=+***++++**-....
.............-......| YYYYY/ YYYYY...-........................................
.....................( YYYYYYYYYY.............................................
.......-..............(________/..............................................
..............................................................................
..............................................................................
{Style.RESET_ALL}
Thank you so much for downloading and using SmartPyLogger!
Developed by Niklavs Visockis, Ludvig Bergström and Jonas Lorenz -
in June of 2025 at the Couchbase x AWS x Cillers Hackathon.
Special thanks goes out to the Couchbase team and AWS for sponsoring this project.
              
        """)


        # Timing start:
        start = time.perf_counter()

        print(f"{Fore.MAGENTA}[STATUS]{Style.RESET_ALL}:    Initializing LoggingMiddleware...")

        # Basic configuration
        self.api_key = api_key
        self.api_url = API_URL
        self.allowed_origins = allowed_origins or []
        self.api_limit_daily = api_limit_daily  # Limit for API requests, default to 1000
        self.censored_words = censored_words or []
        self.banned_words_path = banned_words_path

        # Validator paths
        self.content_validator_path = ""
        self.ip_validator_path = ""

        super().__init__(app) # Inhereting from BaseHTTPMiddleware

        self.app_name = getattr(app, "title", None)

        ### ---- VALIDATE USER ---- ###

        ### Check if API key is provided and return session ID if it is, otherwise raise error
        try:
            response = httpx.post(
                self.api_url + "/api/auth/validate",
                json={"api_key": self.api_key, "appSessionName": self.app_name},
                timeout=10.0  # 10 second timeout
            )
            
            self.auth = response.json()["app_session_id"] ### Get session ID to see if API key is valid

            # print(self.auth)

            if self.auth != "0":
                print(f"{Fore.MAGENTA}[STATUS]{Style.RESET_ALL}:    API key loaded successfully. Session initialization...")
                print(f"{Fore.MAGENTA}[STATUS]{Style.RESET_ALL}:    Session init success! Session ID: "
                      f"{Fore.BLUE}{str(self.auth)}")
                
            elif self.auth == "0":
                print(f"{Fore.RED}[ERROR]:    Invalid API key")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key"
                )
            
            else:
                print(f"{Fore.RED}[ERROR]:      Unknown error during API key validation or session initialization")
                raise HTTPException(
                    status_code=500,
                    detail="Unknown error during API key validation"
                )
                
        except httpx.ConnectError:
            print(f"{Fore.RED}[ERROR]:    Cannot connect to validation server at {self.api_url}")
            raise HTTPException(
                status_code=503,
                detail="Validation server unavailable"
            )
        except httpx.TimeoutException:
            print(f"{Fore.RED}[ERROR]:    Timeout connecting to validation server")
            raise HTTPException(
                status_code=503,
                detail="Validation server timeout"
            )
        except Exception as e:
            print(f"{Fore.RED}[ERROR]:    Unexpected error during validation: {e}")
            raise HTTPException(
                status_code=500,
                detail="Validation error"
            )

        ### ---- CHECK USER MACHINE AND PICK EXEC. PATH ---- ###

        current_dir = os.path.dirname(os.path.abspath(__file__))
        system = platform.system().lower()
        try:
            if system == "windows": # obviously
                self.ip_validator_path = os.path.join(current_dir, "validators", "ip_validator_windows.exe")
                self.content_validator_path = os.path.join(current_dir, "validators", "contains_windows.exe")

            elif system == "darwin":  # macOS
                self.ip_validator_path = os.path.join(current_dir, "validators", "ip_validator_mac")
                self.content_validator_path = os.path.join(current_dir, "validators", "contains_mac")

            else:  # linux
                self.ip_validator_path = os.path.join(current_dir, "validators", "ip_validator_linux")
                self.content_validator_path = os.path.join(current_dir, "validators", "contains_linux")

        except Exception as e:
            print(f"{Fore.RED}[ERROR]:     Error setting validator paths: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error setting validator paths"
            )

        print(f"{Fore.MAGENTA}[STATUS]{Style.RESET_ALL}:    You're all set up! Using {system} validators.")

        # Timing end:
        end = time.perf_counter()

        print(f"{Fore.MAGENTA}[STATUS]{Style.RESET_ALL}:    LoggingMiddleware initialized in {1000 * (end - start):.3f} ms.")
    

    ### ---- MAIN ASYNC DISPATCH METHOD ---- ###
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response: # type: ignore
        """Intercept request/response, sensor for bad words quickly and send off to api_server.py"""
        # Read the request body & load to JSON to send off to API
        body = await request.body()
        sender_ip = request.client.host # type: ignore
        request_method = request.method
        timestamp = datetime.now().strftime("%Y/%m/%d/%H:%M:%S")

        try:
            body_dict = json.loads(body)
        except Exception:
            body_dict = {}

        # Wrap it for the /api/schemas endpoint
        payload = {"api_key":self.api_key,
                    "session_id":self.auth,
                    "app_name": self.app_name,
                    "request_method": request_method, 
                    "request_data": body_dict,
                    "allowed_origins": self.allowed_origins,
                    "sender_ip": sender_ip,
                    "timestamp": timestamp,
                    "flag": 0}
        
        # 1. IP VALIDATION (fatal, but log first)
        ip_validator_path = self.ip_validator_path
        payload_json = json.dumps(payload)
        result = subprocess.run(
            [ip_validator_path, payload_json],
            capture_output=True,
            text=True,
            timeout=5
        )

        # print("Go IP validator output:", repr(result.stdout))
        if result.stdout:
            try:
                validated_payload = json.loads(result.stdout)
                print("Go validator returned valid JSON:", validated_payload)
            except json.JSONDecodeError:
                print("Go validator did not return valid JSON:", result.stdout)
                validated_payload = payload  # fallback to original here
        else:
            print("Go validator returned no output!")
            validated_payload = payload  # fallback to original also


        # 4. If IP was blocked, now raise the HTTP error COPY OF CORS BROTHA
        if result.returncode != 0:

            try:
                httpx.post(
                    self.api_url + "/api/schemas",
                    json=validated_payload,
                    timeout=5.0
                )
            except Exception as e:
                print(f"{Fore.YELLOW}[WARNING]:    Could not send blocked request to API: {e}")

            raise HTTPException(
                status_code=403,
                detail=f"Request blocked: Unauthorized IP address. {result.stdout.strip()}"
            )
        

        # 2. CONTENT VALIDATION (non-fatal, but log)
        content_validator_path = self.content_validator_path
        banned_words_path = self.banned_words_path or "bad_words.txt"  # fallback if not set
        result = subprocess.run(
            [content_validator_path, payload_json, banned_words_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        # print("Go validator output:", repr(result.stdout))

        try:
            httpx.post(
                self.api_url + "/api/schemas",
                json=validated_payload,
                timeout=5.0
            )
        except Exception as e:
            print(f"{Fore.YELLOW}[WARNING]:    Could not send request to API: {e}")

        # Decriment the API limit
        self.api_limit_daily -= 1

        # 5. Otherwise, continue as normal
        response = await call_next(request)
        return response
