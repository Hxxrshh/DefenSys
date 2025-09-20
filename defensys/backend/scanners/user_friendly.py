from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import os

class ScanCategory(str, Enum):
    """User-friendly scan categories that map to technical tools"""
    CODE_SECURITY = "code_security"
    DEPENDENCY_SECURITY = "dependency_security"
    SECRET_DETECTION = "secret_detection"
    CONTAINER_SECURITY = "container_security"
    INFRASTRUCTURE_SECURITY = "infrastructure_security"
    COMPLIANCE_CHECK = "compliance_check"
    FULL_SECURITY_AUDIT = "full_security_audit"
    # DAST Categories
    WEB_APPLICATION_TESTING = "web_application_testing"
    API_SECURITY_TESTING = "api_security_testing"
    PENETRATION_TESTING = "penetration_testing"

class ProjectType(str, Enum):
    """Project type detection"""
    PYTHON_APP = "python_app"
    JAVASCRIPT_APP = "javascript_app"
    WEB_APPLICATION = "web_application"
    CONTAINER_APP = "container_app"
    INFRASTRUCTURE = "infrastructure"
    MOBILE_APP = "mobile_app"
    GENERAL_PROJECT = "general_project"

@dataclass
class ScanOption:
    """User-friendly scan option with automatic tool mapping"""
    category: ScanCategory
    display_name: str
    description: str
    use_case: str
    recommended_for: List[ProjectType]
    technical_tools: List[str]
    estimated_time: str
    complexity: str

class UserFriendlyScanManager:
    """
    User-friendly interface for security scanning that bridges the gap between
    complex technical tools and simple user choices.
    """
    
    def __init__(self):
        """Initialize with all available scan options"""
        self.scan_options = {
            ScanCategory.CODE_SECURITY: ScanOption(
                category=ScanCategory.CODE_SECURITY,
                display_name="🔍 Code Security Analysis",
                description="Analyzes your source code for security vulnerabilities, coding errors, and potential exploits",
                use_case="Find security bugs in your application code before deployment",
                recommended_for=[
                    ProjectType.PYTHON_APP,
                    ProjectType.JAVASCRIPT_APP,
                    ProjectType.WEB_APPLICATION,
                    ProjectType.MOBILE_APP,
                    ProjectType.GENERAL_PROJECT
                ],
                technical_tools=["bandit", "semgrep"],
                estimated_time="2-5 minutes",
                complexity="Simple"
            ),
            
            ScanCategory.DEPENDENCY_SECURITY: ScanOption(
                category=ScanCategory.DEPENDENCY_SECURITY,
                display_name="📦 Dependency & Library Check",
                description="Scans all third-party libraries and packages for known security vulnerabilities",
                use_case="Ensure external libraries you're using don't have security flaws",
                recommended_for=[
                    ProjectType.PYTHON_APP,
                    ProjectType.JAVASCRIPT_APP,
                    ProjectType.WEB_APPLICATION,
                    ProjectType.MOBILE_APP
                ],
                technical_tools=["pip-audit", "snyk"],
                estimated_time="1-3 minutes",
                complexity="Simple"
            ),
            
            ScanCategory.SECRET_DETECTION: ScanOption(
                category=ScanCategory.SECRET_DETECTION,
                display_name="🔐 Secrets & Credentials Check",
                description="Detects accidentally committed passwords, API keys, tokens, and other sensitive information",
                use_case="Prevent credential leaks that could compromise your systems",
                recommended_for=[
                    ProjectType.PYTHON_APP,
                    ProjectType.JAVASCRIPT_APP,
                    ProjectType.WEB_APPLICATION,
                    ProjectType.CONTAINER_APP,
                    ProjectType.INFRASTRUCTURE,
                    ProjectType.MOBILE_APP,
                    ProjectType.GENERAL_PROJECT
                ],
                technical_tools=["secret", "trivy", "semgrep"],
                estimated_time="1-2 minutes",
                complexity="Simple"
            ),
            
            ScanCategory.CONTAINER_SECURITY: ScanOption(
                category=ScanCategory.CONTAINER_SECURITY,
                display_name="🐳 Container & Docker Security",
                description="Analyzes Docker images, containers, and Kubernetes configurations for security issues",
                use_case="Secure your containerized applications and deployment configurations",
                recommended_for=[
                    ProjectType.CONTAINER_APP,
                    ProjectType.INFRASTRUCTURE,
                    ProjectType.WEB_APPLICATION
                ],
                technical_tools=["trivy", "snyk"],
                estimated_time="3-8 minutes",
                complexity="Moderate"
            ),
            
            ScanCategory.INFRASTRUCTURE_SECURITY: ScanOption(
                category=ScanCategory.INFRASTRUCTURE_SECURITY,
                display_name="🏗️ Infrastructure Configuration",
                description="Reviews cloud configurations, Terraform, Kubernetes, and other infrastructure-as-code for security misconfigurations",
                use_case="Ensure your cloud and infrastructure setup follows security best practices",
                recommended_for=[
                    ProjectType.INFRASTRUCTURE,
                    ProjectType.CONTAINER_APP
                ],
                technical_tools=["trivy", "semgrep", "snyk"],
                estimated_time="2-6 minutes",
                complexity="Moderate"
            ),
            
            ScanCategory.COMPLIANCE_CHECK: ScanOption(
                category=ScanCategory.COMPLIANCE_CHECK,
                display_name="✅ Security Compliance Audit",
                description="Comprehensive check against security standards like OWASP Top 10, CWE Top 25, and industry best practices",
                use_case="Verify your application meets security compliance requirements",
                recommended_for=[
                    ProjectType.WEB_APPLICATION,
                    ProjectType.PYTHON_APP,
                    ProjectType.JAVASCRIPT_APP,
                    ProjectType.MOBILE_APP
                ],
                technical_tools=["semgrep", "snyk", "bandit"],
                estimated_time="3-7 minutes",
                complexity="Moderate"
            ),
            
            ScanCategory.FULL_SECURITY_AUDIT: ScanOption(
                category=ScanCategory.FULL_SECURITY_AUDIT,
                display_name="🛡️ Complete Security Audit",
                description="Runs all available security checks for comprehensive coverage. Recommended for production deployments",
                use_case="Get maximum security coverage before deploying to production",
                recommended_for=[
                    ProjectType.PYTHON_APP,
                    ProjectType.JAVASCRIPT_APP,
                    ProjectType.WEB_APPLICATION,
                    ProjectType.CONTAINER_APP,
                    ProjectType.INFRASTRUCTURE,
                    ProjectType.MOBILE_APP,
                    ProjectType.GENERAL_PROJECT
                ],
                technical_tools=["bandit", "pip-audit", "secret", "snyk", "trivy", "semgrep"],
                estimated_time="5-15 minutes",
                complexity="Advanced"
            ),
            
            # DAST Scan Options
            ScanCategory.WEB_APPLICATION_TESTING: ScanOption(
                category=ScanCategory.WEB_APPLICATION_TESTING,
                display_name="🌐 Live Web Application Security Test",
                description="Tests your running web application for vulnerabilities by simulating real attacks",
                use_case="Find security issues in your live web application that static analysis can't detect",
                recommended_for=[
                    ProjectType.WEB_APPLICATION,
                    ProjectType.JAVASCRIPT_APP,
                    ProjectType.PYTHON_APP
                ],
                technical_tools=["zap", "nuclei", "nikto", "nmap"],
                estimated_time="10-30 minutes",
                complexity="Advanced"
            ),
            
            ScanCategory.API_SECURITY_TESTING: ScanOption(
                category=ScanCategory.API_SECURITY_TESTING,
                display_name="🔌 API & REST Endpoint Security Test",
                description="Specifically tests REST APIs, GraphQL endpoints, and web services for security vulnerabilities",
                use_case="Ensure your APIs are secure against common attacks like injection, broken authentication, etc.",
                recommended_for=[
                    ProjectType.WEB_APPLICATION,
                    ProjectType.PYTHON_APP,
                    ProjectType.JAVASCRIPT_APP
                ],
                technical_tools=["zap", "nuclei", "sqlmap"],
                estimated_time="5-20 minutes",
                complexity="Moderate"
            ),
            
            ScanCategory.PENETRATION_TESTING: ScanOption(
                category=ScanCategory.PENETRATION_TESTING,
                display_name="🎯 Comprehensive Penetration Test",
                description="Full penetration testing suite including web application testing, server scanning, and vulnerability exploitation",
                use_case="Get maximum security coverage with active testing of your running application",
                recommended_for=[
                    ProjectType.WEB_APPLICATION,
                    ProjectType.CONTAINER_APP,
                    ProjectType.GENERAL_PROJECT
                ],
                technical_tools=["zap", "nuclei", "nikto", "sqlmap", "nmap"],
                estimated_time="20-60 minutes",
                complexity="Advanced"
            )
        }
    
    def get_scan_options_for_frontend(self) -> List[Dict]:
        """Get user-friendly scan options formatted for frontend dropdown"""
        options = []
        
        for scan_option in self.scan_options.values():
            options.append({
                "value": scan_option.category.value,
                "label": scan_option.display_name,
                "description": scan_option.description,
                "use_case": scan_option.use_case,
                "estimated_time": scan_option.estimated_time,
                "complexity": scan_option.complexity,
                "icon": self._get_scan_icon(scan_option.category),
                "tools_used": self._format_tools_for_display(scan_option.technical_tools)
            })
            
        return options
    
    def get_recommended_scans(self, project_type: ProjectType) -> List[Dict]:
        """Get recommended scan types based on detected project type"""
        recommendations = []
        
        for scan_option in self.scan_options.values():
            if project_type in scan_option.recommended_for:
                recommendations.append({
                    "category": scan_option.category.value,
                    "display_name": scan_option.display_name,
                    "description": scan_option.description,
                    "priority": self._get_recommendation_priority(scan_option.category, project_type),
                    "complexity": scan_option.complexity
                })
        
        # Sort by priority (higher number = higher priority)
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations

    def detect_project_type(self, project_path: str) -> ProjectType:
        """Detect project type based on files and structure"""
        if not os.path.exists(project_path):
            return ProjectType.GENERAL_PROJECT
        
        files_found = []
        for root, dirs, files in os.walk(project_path):
            files_found.extend(files)
            if len(files_found) > 100:  # Limit search for performance
                break
        
        files_found = [f.lower() for f in files_found]
        
        # Python project detection
        if any(f.endswith(('.py', '.pyw')) for f in files_found) or 'requirements.txt' in files_found:
            return ProjectType.PYTHON_APP
            
        # JavaScript project detection  
        if 'package.json' in files_found or any(f.endswith(('.js', '.ts', '.jsx', '.tsx')) for f in files_found):
            return ProjectType.JAVASCRIPT_APP
            
        if 'Dockerfile' in files_found or 'docker-compose.yml' in files_found:
            return ProjectType.CONTAINER_APP
            
        if any(f.endswith('.tf') for f in files_found) or 'terraform' in str(files_found).lower():
            return ProjectType.INFRASTRUCTURE
            
        if any(f.endswith(('.html', '.css', '.js')) for f in files_found):
            return ProjectType.WEB_APPLICATION
            
        if any(f.endswith(('.swift', '.kt', '.java')) for f in files_found):
            return ProjectType.MOBILE_APP
            
        return ProjectType.GENERAL_PROJECT
    
    def map_user_choice_to_technical_scans(self, user_scan_category: str, project_path: str = None) -> Dict:
        """Convert user-friendly choice to technical scanner configuration"""
        
        if user_scan_category not in [cat.value for cat in ScanCategory]:
            raise ValueError(f"Invalid scan category: {user_scan_category}")
            
        scan_category = ScanCategory(user_scan_category)
        scan_option = self.scan_options[scan_category]
        
        # Auto-detect project type if path provided
        project_type = None
        if project_path:
            project_type = self.detect_project_type(project_path)
        
        # Map to technical configuration
        config = {
            "scan_types": self._optimize_tools_for_project(scan_option.technical_tools, project_type),
            "display_info": {
                "chosen_scan": scan_option.display_name,
                "description": scan_option.description,
                "estimated_time": scan_option.estimated_time,
                "tools_to_run": scan_option.technical_tools
            },
            "execution_config": {
                "parallel": scan_category != ScanCategory.FULL_SECURITY_AUDIT,  # Run full audit sequentially for stability
                "max_workers": 2 if scan_category == ScanCategory.FULL_SECURITY_AUDIT else 3,
                "scanner_timeout": 600 if scan_category == ScanCategory.FULL_SECURITY_AUDIT else 300
            }
        }
        
        # Add project-specific optimizations
        if project_type:
            config["project_optimizations"] = self._get_project_optimizations(project_type)
            
        return config
    
    def _optimize_tools_for_project(self, tools: List[str], project_type: Optional[ProjectType]) -> List[str]:
        """Optimize tool selection based on project type"""
        if not project_type:
            return tools
            
        optimized_tools = tools.copy()
        
        # Project-specific optimizations
        if project_type == ProjectType.PYTHON_APP:
            # Prioritize Python-specific tools
            if "bandit" in optimized_tools:
                optimized_tools.remove("bandit")
                optimized_tools.insert(0, "bandit")
                
        elif project_type == ProjectType.JAVASCRIPT_APP:
            # For JS projects, prioritize Semgrep over Bandit
            if "bandit" in optimized_tools and "semgrep" in optimized_tools:
                optimized_tools.remove("bandit")
                
        elif project_type == ProjectType.CONTAINER_APP:
            # Prioritize container-focused tools
            if "trivy" in optimized_tools:
                optimized_tools.remove("trivy")
                optimized_tools.insert(0, "trivy")
                
        return optimized_tools
    
    def _get_project_optimizations(self, project_type: ProjectType) -> Dict:
        """Get project-specific optimization settings"""
        optimizations = {
            ProjectType.PYTHON_APP: {
                "semgrep_config": "p/python",
                "exclude_patterns": ["*.pyc", "__pycache__/", ".venv/", "venv/"]
            },
            ProjectType.JAVASCRIPT_APP: {
                "semgrep_config": "p/javascript",
                "exclude_patterns": ["node_modules/", "*.min.js", "dist/", "build/"]
            },
            ProjectType.CONTAINER_APP: {
                "trivy_target_type": "fs",
                "exclude_patterns": [".git/", "node_modules/", "__pycache__/"]
            },
            ProjectType.INFRASTRUCTURE: {
                "semgrep_config": "p/terraform",
                "trivy_target_type": "config"
            }
        }
        
        return optimizations.get(project_type, {})
    
    def _get_scan_icon(self, category: ScanCategory) -> str:
        """Get appropriate icon for scan category"""
        icons = {
            ScanCategory.CODE_SECURITY: "🔍",
            ScanCategory.DEPENDENCY_SECURITY: "📦", 
            ScanCategory.SECRET_DETECTION: "🔐",
            ScanCategory.CONTAINER_SECURITY: "🐳",
            ScanCategory.INFRASTRUCTURE_SECURITY: "🏗️",
            ScanCategory.COMPLIANCE_CHECK: "✅",
            ScanCategory.FULL_SECURITY_AUDIT: "🛡️",
            # DAST Icons
            ScanCategory.WEB_APPLICATION_TESTING: "🌐",
            ScanCategory.API_SECURITY_TESTING: "🔌",
            ScanCategory.PENETRATION_TESTING: "🎯"
        }
        return icons.get(category, "🔧")
    
    def _format_tools_for_display(self, tools: List[str]) -> str:
        """Format technical tool names for user display"""
        tool_display_names = {
            "bandit": "Bandit (Python Security)",
            "pip-audit": "pip-audit (Python Dependencies)",
            "secret": "Secret Scanner",
            "snyk": "Snyk (Commercial Grade)",
            "trivy": "Trivy (Container Security)", 
            "semgrep": "Semgrep (Advanced Code Analysis)",
            # DAST Tools
            "zap": "OWASP ZAP (Web App Scanner)",
            "nuclei": "Nuclei (Template-based Scanner)",
            "nikto": "Nikto (Web Server Scanner)",
            "sqlmap": "SQLMap (SQL Injection Tester)",
            "nmap": "Nmap (Network Discovery)"
        }
        
        display_tools = [tool_display_names.get(tool, tool.title()) for tool in tools]
        return ", ".join(display_tools)
    
    def _get_recommendation_priority(self, category: ScanCategory, project_type: ProjectType) -> int:
        """Get priority score for recommendations (higher = more important)"""
        
        # Base priorities for each scan type
        base_priorities = {
            ScanCategory.SECRET_DETECTION: 10,  # Always high priority
            ScanCategory.CODE_SECURITY: 8,
            ScanCategory.DEPENDENCY_SECURITY: 7,
            ScanCategory.WEB_APPLICATION_TESTING: 8,  # High for web apps
            ScanCategory.API_SECURITY_TESTING: 7,
            ScanCategory.CONTAINER_SECURITY: 6,
            ScanCategory.INFRASTRUCTURE_SECURITY: 5,
            ScanCategory.COMPLIANCE_CHECK: 4,
            ScanCategory.PENETRATION_TESTING: 6,
            ScanCategory.FULL_SECURITY_AUDIT: 3  # Lower priority since it's comprehensive
        }
        
        priority = base_priorities.get(category, 5)
        
        # Boost priority based on project type relevance
        if project_type == ProjectType.PYTHON_APP:
            if category == ScanCategory.CODE_SECURITY:
                priority += 2
            elif category == ScanCategory.DEPENDENCY_SECURITY:
                priority += 1
                
        elif project_type == ProjectType.WEB_APPLICATION:
            if category in [ScanCategory.WEB_APPLICATION_TESTING, ScanCategory.API_SECURITY_TESTING]:
                priority += 2
            elif category == ScanCategory.SECRET_DETECTION:
                priority += 1
                
        elif project_type == ProjectType.CONTAINER_APP:
            if category == ScanCategory.CONTAINER_SECURITY:
                priority += 2
            elif category == ScanCategory.PENETRATION_TESTING:
                priority += 1
        
        return priority