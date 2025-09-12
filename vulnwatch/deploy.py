#!/usr/bin/env python3
"""
DefenSys Deployment and Management Script

This script handles containerization, Jenkins integration, and production deployment
for the DefenSys DevSecOps platform.

Usage:
    python deploy.py --help
    python deploy.py build
    python deploy.py deploy --env production
    python deploy.py scan --repo https://github.com/user/repo
"""

import argparse
import subprocess
import json
import os
import sys
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional

class DefenSysDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load deployment configuration"""
        config_file = self.project_root / "deploy-config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "registry": "your-registry.com",
            "namespace": "defensys",
            "environments": {
                "development": {
                    "api_url": "http://localhost:5000",
                    "frontend_url": "http://localhost:8080"
                },
                "staging": {
                    "api_url": "https://api-staging.defensys.com",
                    "frontend_url": "https://staging.defensys.com"
                },
                "production": {
                    "api_url": "https://api.defensys.com", 
                    "frontend_url": "https://defensys.com"
                }
            }
        }

    def build_images(self, version: str = "latest") -> bool:
        """Build all Docker images"""
        print(f"🏗️  Building DefenSys images (version: {version})")
        
        images = [
            ("backend/VulnAlert", "defensys-api"),
            ("frontend/vulnwatch-dash", "defensys-frontend"),
            ("backend/scanners/sast", "defensys-sast"),
            ("backend/scanners/secrets", "defensys-secrets"),
            ("backend/scanners/dependencies", "defensys-deps")
        ]
        
        for context, name in images:
            print(f"📦 Building {name}...")
            
            if not self.run_command([
                "docker", "build",
                "-t", f"{self.config['registry']}/{name}:{version}",
                "-t", f"{self.config['registry']}/{name}:latest",
                context
            ]):
                print(f"❌ Failed to build {name}")
                return False
                
            print(f"✅ Built {name}")
        
        return True

    def push_images(self, version: str = "latest") -> bool:
        """Push images to registry"""
        print(f"🚀 Pushing images to {self.config['registry']}")
        
        images = ["defensys-api", "defensys-frontend", "defensys-sast", "defensys-secrets", "defensys-deps"]
        
        for image in images:
            for tag in [version, "latest"]:
                if not self.run_command([
                    "docker", "push", f"{self.config['registry']}/{image}:{tag}"
                ]):
                    print(f"❌ Failed to push {image}:{tag}")
                    return False
                    
        print("✅ All images pushed successfully")
        return True

    def deploy_to_kubernetes(self, environment: str, version: str = "latest") -> bool:
        """Deploy to Kubernetes cluster"""
        print(f"🚀 Deploying to {environment} environment")
        
        # Update image tags in manifests
        k8s_dir = self.project_root / "k8s" / environment
        if not k8s_dir.exists():
            print(f"❌ Kubernetes manifests not found for {environment}")
            return False
            
        # Apply manifests
        if not self.run_command([
            "kubectl", "apply", "-f", str(k8s_dir), "-n", f"defensys-{environment}"
        ]):
            print(f"❌ Failed to apply Kubernetes manifests")
            return False
            
        # Wait for rollout
        deployments = ["defensys-api", "defensys-frontend"]
        for deployment in deployments:
            if not self.run_command([
                "kubectl", "rollout", "status", f"deployment/{deployment}",
                "-n", f"defensys-{environment}"
            ]):
                print(f"❌ Deployment rollout failed for {deployment}")
                return False
                
        print(f"✅ Successfully deployed to {environment}")
        return True

    def deploy_with_docker_compose(self, environment: str = "production") -> bool:
        """Deploy using Docker Compose"""
        print(f"🐳 Deploying with Docker Compose ({environment})")
        
        compose_file = f"docker-compose.{environment}.yml"
        if not Path(compose_file).exists():
            compose_file = "docker-compose.yml"
            
        if not self.run_command([
            "docker-compose", "-f", compose_file, "up", "-d", "--build"
        ]):
            print("❌ Docker Compose deployment failed")
            return False
            
        print("✅ Docker Compose deployment successful")
        return True

    def setup_jenkins_pipeline(self) -> bool:
        """Setup Jenkins pipeline"""
        print("🔧 Setting up Jenkins pipeline")
        
        # Create Jenkins job XML
        jenkins_xml = self.generate_jenkins_job_xml()
        
        # You would typically use Jenkins API here
        print("📝 Jenkinsfile created. Please:")
        print("1. Create a new Pipeline job in Jenkins")
        print("2. Configure it to use the Jenkinsfile from your repository")
        print("3. Set up the required credentials and environment variables")
        
        return True

    def generate_jenkins_job_xml(self) -> str:
        """Generate Jenkins job configuration XML"""
        return """<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <actions/>
  <description>DefenSys DevSecOps Platform CI/CD Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
      <triggers>
        <com.cloudbees.jenkins.GitHubPushTrigger plugin="github@1.34.1">
          <spec></spec>
        </com.cloudbees.jenkins.GitHubPushTrigger>
      </triggers>
    </org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.92">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.8.2">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/your-org/defensys.git</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>"""

    def scan_repository(self, repo_url: str, scan_types: List[str] = None) -> Dict:
        """Trigger repository scan via API"""
        if scan_types is None:
            scan_types = ["SAST", "SECRET", "DEPENDENCY"]
            
        print(f"🔍 Scanning repository: {repo_url}")
        print(f"📋 Scan types: {', '.join(scan_types)}")
        
        api_url = self.config["environments"]["development"]["api_url"]
        
        try:
            response = requests.post(
                f"{api_url}/api/scans",
                json={"repo_url": repo_url, "scan_types": scan_types},
                timeout=30
            )
            
            if response.status_code == 200:
                scan_data = response.json()
                scan_id = scan_data.get("id")
                
                print(f"✅ Scan started successfully (ID: {scan_id})")
                
                # Poll for results
                return self.poll_scan_results(scan_id)
            else:
                print(f"❌ Failed to start scan: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return {"error": str(e)}

    def poll_scan_results(self, scan_id: str, timeout: int = 300) -> Dict:
        """Poll scan results until completion"""
        api_url = self.config["environments"]["development"]["api_url"]
        start_time = time.time()
        
        print(f"⏳ Waiting for scan results...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{api_url}/api/scans/{scan_id}")
                
                if response.status_code == 200:
                    scan_data = response.json()
                    status = scan_data.get("scan", {}).get("status")
                    
                    if status == "COMPLETED":
                        vulnerabilities = scan_data.get("vulnerabilities", [])
                        print(f"✅ Scan completed! Found {len(vulnerabilities)} vulnerabilities")
                        
                        # Print summary
                        self.print_scan_summary(vulnerabilities)
                        return scan_data
                        
                    elif status == "FAILED":
                        print("❌ Scan failed")
                        return scan_data
                        
                    print(f"⏳ Status: {status}")
                    
                time.sleep(10)
                
            except requests.RequestException as e:
                print(f"❌ Error polling results: {e}")
                break
                
        print("⏰ Scan timeout reached")
        return {"error": "timeout"}

    def print_scan_summary(self, vulnerabilities: List[Dict]):
        """Print vulnerability scan summary"""
        if not vulnerabilities:
            print("🎉 No vulnerabilities found!")
            return
            
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN")
            if severity in severity_counts:
                severity_counts[severity] += 1
                
        print("\n📊 Vulnerability Summary:")
        for severity, count in severity_counts.items():
            if count > 0:
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                print(f"   {emoji.get(severity, '⚪')} {severity}: {count}")

    def health_check(self, environment: str = "development") -> bool:
        """Check service health"""
        api_url = self.config["environments"][environment]["api_url"]
        
        try:
            response = requests.get(f"{api_url}/api/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ {environment} environment is healthy")
                return True
            else:
                print(f"⚠️  {environment} environment returned {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ {environment} environment is unreachable: {e}")
            return False

    def run_command(self, cmd: List[str]) -> bool:
        """Run shell command and return success status"""
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {' '.join(cmd)}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False

def main():
    parser = argparse.ArgumentParser(description="DefenSys Deployment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build Docker images")
    build_parser.add_argument("--version", default="latest", help="Image version tag")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to environment")
    deploy_parser.add_argument("--env", choices=["development", "staging", "production"], 
                              default="development", help="Target environment")
    deploy_parser.add_argument("--method", choices=["k8s", "compose"], 
                              default="compose", help="Deployment method")
    deploy_parser.add_argument("--version", default="latest", help="Image version")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan repository")
    scan_parser.add_argument("--repo", required=True, help="Repository URL")
    scan_parser.add_argument("--types", nargs="+", choices=["SAST", "SECRET", "DEPENDENCY"],
                            default=["SAST", "SECRET", "DEPENDENCY"], help="Scan types")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument("--env", choices=["development", "staging", "production"],
                              default="development", help="Environment to check")
    
    # Jenkins setup
    subparsers.add_parser("setup-jenkins", help="Setup Jenkins pipeline")
    
    args = parser.parse_args()
    
    deployer = DefenSysDeployer()
    
    if args.command == "build":
        success = deployer.build_images(args.version)
        sys.exit(0 if success else 1)
        
    elif args.command == "deploy":
        if args.method == "k8s":
            success = deployer.deploy_to_kubernetes(args.env, args.version)
        else:
            success = deployer.deploy_with_docker_compose(args.env)
        sys.exit(0 if success else 1)
        
    elif args.command == "scan":
        result = deployer.scan_repository(args.repo, args.types)
        if "error" in result:
            sys.exit(1)
            
    elif args.command == "health":
        success = deployer.health_check(args.env)
        sys.exit(0 if success else 1)
        
    elif args.command == "setup-jenkins":
        deployer.setup_jenkins_pipeline()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
