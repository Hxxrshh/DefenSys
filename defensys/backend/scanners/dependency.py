import subprocess
import json
import os
from typing import List
from .base import Scanner

class PipAuditScanner(Scanner):
    def scan(self, path: str) -> List[dict]:
        # Look for requirements.txt in common locations
        possible_paths = [
            os.path.join(path, "requirements.txt"),
            os.path.join(path, "requirements", "requirements.txt"),
            os.path.join(path, "requirements", "base.txt"),
        ]
        
        requirements_path = None
        for req_path in possible_paths:
            if os.path.exists(req_path):
                requirements_path = req_path
                break
        
        if not requirements_path:
            print(f"No requirements.txt found in {path}")
            return []
            
        try:
            result = subprocess.run(
                ["pip-audit", "-r", requirements_path, "--format", "json"],
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(result.stdout)
            return data.get("vulnerabilities", [])
        except subprocess.CalledProcessError as e:
            print(f"Error running pip-audit scanner: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing pip-audit output: {e}")
            return []
        except FileNotFoundError:
            print("pip-audit not found. Please install it.")
            return []
