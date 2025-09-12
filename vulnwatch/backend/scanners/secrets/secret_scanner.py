#!/usr/bin/env python3

import pika
import json
import subprocess
import tempfile
import os
import re
import requests
from pathlib import Path

class SecretScanner:
    def __init__(self, broker_url, api_url):
        self.broker_url = broker_url
        self.api_url = api_url
        self.setup_broker_connection()
        
        # Common secret patterns
        self.secret_patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[0-9a-zA-Z/+]{40}',
            'github_token': r'ghp_[0-9a-zA-Z]{36}',
            'slack_token': r'xox[baprs]-[0-9a-zA-Z-]+',
            'stripe_key': r'sk_live_[0-9a-zA-Z]+',
            'jwt_token': r'eyJ[0-9a-zA-Z_-]+\.[0-9a-zA-Z_-]+\.[0-9a-zA-Z_-]+',
            'private_key': r'-----BEGIN.*PRIVATE KEY-----',
            'generic_api_key': r'[aA][pP][iI]_?[kK][eE][yY].*[\'|\"][0-9a-zA-Z]{32,45}[\'|\"]',
            'password_in_url': r'[a-zA-Z]{3,10}://[^/\s:@]{3,20}:[^/\s:@]{3,20}@.{1,100}[\"\'\\s]'
        }

    def setup_broker_connection(self):
        """Setup RabbitMQ connection"""
        connection = pika.BlockingConnection(pika.URLParameters(self.broker_url))
        self.channel = connection.channel()
        
        # Declare queues
        self.channel.queue_declare(queue='secret_scan_queue', durable=True)

    def scan_with_trufflehog(self, repo_path):
        """Run TruffleHog secret scan"""
        try:
            result = subprocess.run([
                'trufflehog', 'filesystem', repo_path, '--json'
            ], capture_output=True, text=True)
            
            secrets = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            secrets.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            return secrets
        except Exception as e:
            print(f"TruffleHog scan failed: {e}")
            return []

    def scan_with_regex_patterns(self, repo_path):
        """Scan for secrets using regex patterns"""
        secrets = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip binary files and large files
                try:
                    if os.path.getsize(file_path) > 1024 * 1024:  # Skip files > 1MB
                        continue
                        
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Check each pattern
                    for secret_type, pattern in self.secret_patterns.items():
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            secrets.append({
                                'type': secret_type,
                                'file': file_path.replace(repo_path, ''),
                                'line': line_num,
                                'match': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                                'confidence': 'HIGH' if secret_type in ['aws_access_key', 'github_token'] else 'MEDIUM'
                            })
                            
                except (UnicodeDecodeError, PermissionError):
                    continue
                    
        return secrets

    def clone_repository(self, repo_url, temp_dir):
        """Clone repository to temporary directory"""
        try:
            subprocess.run([
                'git', 'clone', '--depth', '1', repo_url, temp_dir
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            return False

    def process_scan_request(self, ch, method, properties, body):
        """Process secret scan request"""
        try:
            scan_request = json.loads(body)
            repo_url = scan_request.get('repo_url')
            scan_id = scan_request.get('scan_id')
            
            print(f"Processing secret scan for {repo_url} (ID: {scan_id})")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone repository
                if not self.clone_repository(repo_url, temp_dir):
                    self.send_error_result(scan_id, "Failed to clone repository")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # Run scans
                trufflehog_results = self.scan_with_trufflehog(temp_dir)
                regex_results = self.scan_with_regex_patterns(temp_dir)
                
                # Process and format results
                vulnerabilities = self.format_results(trufflehog_results, regex_results)
                
                # Send results to API
                self.send_results_to_api(scan_id, vulnerabilities)
                
                print(f"Secret scan completed for {repo_url}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"Error processing scan request: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def format_results(self, trufflehog_results, regex_results):
        """Format scan results into standardized format"""
        vulnerabilities = []
        
        # Process TruffleHog results
        for result in trufflehog_results:
            vuln = {
                'scanner': 'trufflehog',
                'severity': 'HIGH',
                'title': f"Secret detected: {result.get('DetectorName', 'Unknown')}",
                'description': f"Potential secret found in repository",
                'file_path': result.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', ''),
                'line_number': result.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('line', 0),
                'secret_type': result.get('DetectorName', 'Unknown'),
                'confidence': 'HIGH' if result.get('Verified', False) else 'MEDIUM'
            }
            vulnerabilities.append(vuln)
        
        # Process regex results
        for result in regex_results:
            vuln = {
                'scanner': 'regex_patterns',
                'severity': 'MEDIUM' if result['confidence'] == 'HIGH' else 'LOW',
                'title': f"Potential secret: {result['type']}",
                'description': f"Pattern match for {result['type']}",
                'file_path': result['file'],
                'line_number': result['line'],
                'secret_type': result['type'],
                'confidence': result['confidence']
            }
            vulnerabilities.append(vuln)
        
        return vulnerabilities

    def send_results_to_api(self, scan_id, vulnerabilities):
        """Send scan results to DefenSys API"""
        try:
            payload = {
                'scan_id': scan_id,
                'scan_type': 'SECRET',
                'vulnerabilities': vulnerabilities,
                'status': 'completed'
            }
            
            response = requests.post(
                f"{self.api_url}/api/scan-results",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"Results sent successfully for scan {scan_id}")
            else:
                print(f"Failed to send results: {response.status_code}")
                
        except Exception as e:
            print(f"Error sending results to API: {e}")

    def send_error_result(self, scan_id, error_message):
        """Send error result to API"""
        try:
            payload = {
                'scan_id': scan_id,
                'scan_type': 'SECRET',
                'status': 'failed',
                'error': error_message
            }
            
            requests.post(
                f"{self.api_url}/api/scan-results",
                json=payload,
                timeout=30
            )
        except Exception as e:
            print(f"Error sending error result: {e}")

    def start_consuming(self):
        """Start consuming messages from queue"""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='secret_scan_queue',
            on_message_callback=self.process_scan_request
        )
        
        print("Secret Scanner started. Waiting for scan requests...")
        self.channel.start_consuming()

if __name__ == "__main__":
    broker_url = os.environ.get('BROKER_URL', 'amqp://admin:admin123@localhost:5672/')
    api_url = os.environ.get('API_URL', 'http://localhost:5000')
    
    scanner = SecretScanner(broker_url, api_url)
    scanner.start_consuming()
