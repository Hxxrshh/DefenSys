#!/usr/bin/env python3

import pika
import json
import subprocess
import tempfile
import os
import shutil
import requests
from pathlib import Path

class SASTScanner:
    def __init__(self, broker_url, api_url):
        self.broker_url = broker_url
        self.api_url = api_url
        self.setup_broker_connection()

    def setup_broker_connection(self):
        """Setup RabbitMQ connection"""
        connection = pika.BlockingConnection(pika.URLParameters(self.broker_url))
        self.channel = connection.channel()
        
        # Declare queues
        self.channel.queue_declare(queue='sast_scan_queue', durable=True)
        self.channel.queue_declare(queue='scan_results_queue', durable=True)

    def scan_with_bandit(self, repo_path):
        """Run Bandit SAST scan"""
        try:
            result = subprocess.run([
                'bandit', '-r', repo_path, '-f', 'json'
            ], capture_output=True, text=True)
            
            if result.stdout:
                return json.loads(result.stdout)
            return {"results": []}
        except Exception as e:
            print(f"Bandit scan failed: {e}")
            return {"results": []}

    def scan_with_semgrep(self, repo_path):
        """Run Semgrep SAST scan"""
        try:
            result = subprocess.run([
                'semgrep', '--config=auto', '--json', repo_path
            ], capture_output=True, text=True)
            
            if result.stdout:
                return json.loads(result.stdout)
            return {"results": []}
        except Exception as e:
            print(f"Semgrep scan failed: {e}")
            return {"results": []}

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
        """Process SAST scan request"""
        try:
            scan_request = json.loads(body)
            repo_url = scan_request.get('repo_url')
            scan_id = scan_request.get('scan_id')
            
            print(f"Processing SAST scan for {repo_url} (ID: {scan_id})")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone repository
                if not self.clone_repository(repo_url, temp_dir):
                    self.send_error_result(scan_id, "Failed to clone repository")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # Run scans
                bandit_results = self.scan_with_bandit(temp_dir)
                semgrep_results = self.scan_with_semgrep(temp_dir)
                
                # Process and format results
                vulnerabilities = self.format_results(bandit_results, semgrep_results)
                
                # Send results to API
                self.send_results_to_api(scan_id, vulnerabilities)
                
                print(f"SAST scan completed for {repo_url}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"Error processing scan request: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def format_results(self, bandit_results, semgrep_results):
        """Format scan results into standardized format"""
        vulnerabilities = []
        
        # Process Bandit results
        for result in bandit_results.get('results', []):
            vuln = {
                'scanner': 'bandit',
                'severity': result.get('issue_severity', 'UNKNOWN').upper(),
                'title': result.get('test_name', 'Unknown'),
                'description': result.get('issue_text', ''),
                'file_path': result.get('filename', ''),
                'line_number': result.get('line_number', 0),
                'cwe_id': result.get('test_id', ''),
                'confidence': result.get('issue_confidence', 'UNKNOWN')
            }
            vulnerabilities.append(vuln)
        
        # Process Semgrep results
        for result in semgrep_results.get('results', []):
            vuln = {
                'scanner': 'semgrep',
                'severity': result.get('extra', {}).get('severity', 'INFO').upper(),
                'title': result.get('check_id', 'Unknown'),
                'description': result.get('extra', {}).get('message', ''),
                'file_path': result.get('path', ''),
                'line_number': result.get('start', {}).get('line', 0),
                'cwe_id': result.get('extra', {}).get('metadata', {}).get('cwe', ''),
                'confidence': 'HIGH'
            }
            vulnerabilities.append(vuln)
        
        return vulnerabilities

    def send_results_to_api(self, scan_id, vulnerabilities):
        """Send scan results to DefenSys API"""
        try:
            payload = {
                'scan_id': scan_id,
                'scan_type': 'SAST',
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
                'scan_type': 'SAST',
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
            queue='sast_scan_queue',
            on_message_callback=self.process_scan_request
        )
        
        print("SAST Scanner started. Waiting for scan requests...")
        self.channel.start_consuming()

if __name__ == "__main__":
    broker_url = os.environ.get('BROKER_URL', 'amqp://admin:admin123@localhost:5672/')
    api_url = os.environ.get('API_URL', 'http://localhost:5000')
    
    scanner = SASTScanner(broker_url, api_url)
    scanner.start_consuming()
