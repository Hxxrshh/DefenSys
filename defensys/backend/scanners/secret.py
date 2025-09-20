import re
import os
from typing import List
from .base import Scanner

class SecretScanner(Scanner):
    def __init__(self):
        self.patterns = {
            "aws_access_key": r"AKIA[0-9A-Z]{16}",
            "aws_secret_key": r"[0-9a-zA-Z/+]{40}",
            "api_key": r"['\"]?[a-zA-Z0-9_-]*[kK][eE][yY]['\"]?\s*[:=]\s*['\"][0-9a-zA-Z_-]{16,}['\"]",
            "password": r"['\"]?[pP][aA][sS][sS][wW][oO][rR][dD]['\"]?\s*[:=]\s*['\"][^'\"\s]{8,}['\"]",
            "token": r"['\"]?[tT][oO][kK][eE][nN]['\"]?\s*[:=]\s*['\"][0-9a-zA-Z_-]{16,}['\"]",
            "private_key": r"-----BEGIN [A-Z]+ PRIVATE KEY-----",
        }

    def scan(self, path: str) -> List[dict]:
        vulnerabilities = []
        
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return vulnerabilities
            
        try:
            for root, dirs, files in os.walk(path):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in {'.git', '.svn', 'node_modules', '__pycache__', '.venv', 'venv'}]
                
                for file in files:
                    # Only scan text files
                    if not self._is_text_file(file):
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for secret_type, pattern in self.patterns.items():
                                matches = re.finditer(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    line_number = content[:match.start()].count('\n') + 1
                                    vulnerabilities.append({
                                        "type": "secret",
                                        "subtype": secret_type,
                                        "file": file_path,
                                        "line": line_number,
                                        "description": f"Potential {secret_type.replace('_', ' ')} found",
                                        "severity": "HIGH",
                                        "confidence": "MEDIUM"
                                    })
                    except (UnicodeDecodeError, PermissionError) as e:
                        print(f"Error reading file {file_path}: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scanning directory {path}: {e}")
            
        return vulnerabilities
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is likely to contain text/code"""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.php', '.rb', '.go', '.rs', '.scala', '.kt', '.swift', '.m',
            '.txt', '.md', '.yml', '.yaml', '.json', '.xml', '.html', '.css',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            '.sql', '.r', '.R', '.pl', '.pm', '.lua', '.vim', '.vimrc',
            '.ini', '.cfg', '.conf', '.config', '.env', '.properties'
        }
        
        _, ext = os.path.splitext(filename.lower())
        return ext in text_extensions or not ext  # include files without extension
