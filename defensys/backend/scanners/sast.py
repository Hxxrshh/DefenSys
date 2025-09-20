import subprocess
import json
import os
from typing import List
from .base import Scanner

class BanditScanner(Scanner):
    def scan(self, path: str) -> List[dict]:
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return []
            
        try:
            result = subprocess.run(
                ["bandit", "-r", path, "-f", "json"],
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(result.stdout)
            return data.get("results", [])
        except subprocess.CalledProcessError as e:
            print(f"Error running bandit scanner: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing bandit output: {e}")
            return []
        except FileNotFoundError:
            print("bandit not found. Please install it.")
            return []
