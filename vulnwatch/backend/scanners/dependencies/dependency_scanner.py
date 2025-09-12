#!/usr/bin/env python3

import pika
import json
import subprocess
import tempfile
import os
import requests
from pathlib import Path

class DependencyScanner:
    def __init__(self, broker_url, api_url):
        self.broker_url = broker_url
        self.api_url = api_url
        self.setup_broker_connection()

    def setup_broker_connection(self):
        """Setup RabbitMQ connection"""
        connection = pika.BlockingConnection(pika.URLParameters(self.broker_url))
        self.channel = connection.channel()
        
        # Declare queues
        self.channel.queue_declare(queue='dependency_scan_queue', durable=True)

    def scan_python_dependencies(self, repo_path):
        """Scan Python dependencies using pip-audit and safety"""
        vulnerabilities = []
        
        # Look for requirements files
        req_files = ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml', 'Pipfile']
        
        for req_file in req_files:
            req_path = os.path.join(repo_path, req_file)
            if os.path.exists(req_path):
                print(f"Found {req_file}, scanning...")
                
                # Run pip-audit
                try:
                    result = subprocess.run([
                        'pip-audit', '--requirement', req_path, '--format', 'json'
                    ], capture_output=True, text=True, cwd=repo_path)
                    
                    if result.stdout:
                        audit_data = json.loads(result.stdout)
                        for vuln in audit_data.get('vulnerabilities', []):
                            vulnerabilities.append({
                                'scanner': 'pip-audit',
                                'package': vuln.get('package'),
                                'version': vuln.get('installed_version'),
                                'vulnerability_id': vuln.get('id'),
                                'severity': self.map_severity(vuln.get('severity')),
                                'description': vuln.get('description', ''),
                                'fixed_versions': vuln.get('fixed_versions', []),
                                'file': req_file
                            })
                except Exception as e:
                    print(f"pip-audit failed for {req_file}: {e}")
                
                # Run safety check
                try:
                    result = subprocess.run([
                        'safety', 'check', '--json', '--file', req_path
                    ], capture_output=True, text=True, cwd=repo_path)
                    
                    if result.stdout:
                        safety_data = json.loads(result.stdout)
                        for vuln in safety_data:
                            vulnerabilities.append({
                                'scanner': 'safety',
                                'package': vuln.get('package'),
                                'version': vuln.get('installed_version'),
                                'vulnerability_id': vuln.get('vulnerability_id'),
                                'severity': 'HIGH',  # Safety doesn't provide severity
                                'description': vuln.get('advisory', ''),
                                'fixed_versions': [],
                                'file': req_file
                            })
                except Exception as e:
                    print(f"safety check failed for {req_file}: {e}")
        
        return vulnerabilities

    def scan_nodejs_dependencies(self, repo_path):
        """Scan Node.js dependencies using npm audit"""
        vulnerabilities = []
        
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            print("Found package.json, scanning...")
            
            try:
                # Run npm audit
                result = subprocess.run([
                    'npm', 'audit', '--json'
                ], capture_output=True, text=True, cwd=repo_path)
                
                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    
                    for vuln_id, vuln in audit_data.get('vulnerabilities', {}).items():
                        vulnerabilities.append({
                            'scanner': 'npm-audit',
                            'package': vuln.get('name'),
                            'version': vuln.get('range'),
                            'vulnerability_id': vuln_id,
                            'severity': vuln.get('severity', 'UNKNOWN').upper(),
                            'description': vuln.get('title', ''),
                            'fixed_versions': [],
                            'file': 'package.json'
                        })
                        
            except Exception as e:
                print(f"npm audit failed: {e}")
        
        return vulnerabilities

    def generate_sbom(self, repo_path):
        """Generate Software Bill of Materials (SBOM)"""
        sbom_data = {
            'python_packages': [],
            'nodejs_packages': []
        }
        
        # Python SBOM
        req_files = ['requirements.txt', 'pyproject.toml']
        for req_file in req_files:
            req_path = os.path.join(repo_path, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '==' in line:
                                package, version = line.split('==')
                                sbom_data['python_packages'].append({
                                    'name': package.strip(),
                                    'version': version.strip(),
                                    'file': req_file
                                })
                except Exception as e:
                    print(f"Error parsing {req_file}: {e}")
        
        # Node.js SBOM
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                for dep_type in ['dependencies', 'devDependencies']:
                    for name, version in package_data.get(dep_type, {}).items():
                        sbom_data['nodejs_packages'].append({
                            'name': name,
                            'version': version,
                            'type': dep_type,
                            'file': 'package.json'
                        })
            except Exception as e:
                print(f"Error parsing package.json: {e}")
        
        return sbom_data

    def map_severity(self, severity):
        """Map various severity formats to standard levels"""
        if not severity:
            return 'UNKNOWN'
        
        severity = str(severity).upper()
        severity_mapping = {
            'CRITICAL': 'CRITICAL',
            'HIGH': 'HIGH',
            'MODERATE': 'MEDIUM',
            'MEDIUM': 'MEDIUM',
            'LOW': 'LOW',
            'INFO': 'INFO',
            'INFORMATIONAL': 'INFO'
        }
        
        return severity_mapping.get(severity, 'UNKNOWN')

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
        """Process dependency scan request"""
        try:
            scan_request = json.loads(body)
            repo_url = scan_request.get('repo_url')
            scan_id = scan_request.get('scan_id')
            
            print(f"Processing dependency scan for {repo_url} (ID: {scan_id})")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone repository
                if not self.clone_repository(repo_url, temp_dir):
                    self.send_error_result(scan_id, "Failed to clone repository")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # Run scans
                python_vulns = self.scan_python_dependencies(temp_dir)
                nodejs_vulns = self.scan_nodejs_dependencies(temp_dir)
                sbom = self.generate_sbom(temp_dir)
                
                # Combine all vulnerabilities
                all_vulnerabilities = python_vulns + nodejs_vulns
                
                # Process and format results
                vulnerabilities = self.format_results(all_vulnerabilities)
                
                # Send results to API
                self.send_results_to_api(scan_id, vulnerabilities, sbom)
                
                print(f"Dependency scan completed for {repo_url}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"Error processing scan request: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def format_results(self, vulnerabilities):
        """Format scan results into standardized format"""
        formatted_vulns = []
        
        for vuln in vulnerabilities:
            formatted_vuln = {
                'scanner': vuln.get('scanner'),
                'severity': vuln.get('severity', 'UNKNOWN'),
                'title': f"Vulnerable dependency: {vuln.get('package')}",
                'description': vuln.get('description', ''),
                'package_name': vuln.get('package'),
                'package_version': vuln.get('version'),
                'vulnerability_id': vuln.get('vulnerability_id'),
                'fixed_versions': vuln.get('fixed_versions', []),
                'file_path': vuln.get('file', ''),
                'confidence': 'HIGH'
            }
            formatted_vulns.append(formatted_vuln)
        
        return formatted_vulns

    def send_results_to_api(self, scan_id, vulnerabilities, sbom):
        """Send scan results to DefenSys API"""
        try:
            payload = {
                'scan_id': scan_id,
                'scan_type': 'DEPENDENCY',
                'vulnerabilities': vulnerabilities,
                'sbom': sbom,
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
                'scan_type': 'DEPENDENCY',
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
            queue='dependency_scan_queue',
            on_message_callback=self.process_scan_request
        )
        
        print("Dependency Scanner started. Waiting for scan requests...")
        self.channel.start_consuming()

if __name__ == "__main__":
    broker_url = os.environ.get('BROKER_URL', 'amqp://admin:admin123@localhost:5672/')
    api_url = os.environ.get('API_URL', 'http://localhost:5000')
    
    scanner = DependencyScanner(broker_url, api_url)
    scanner.start_consuming()
