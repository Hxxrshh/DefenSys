import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.main import app, get_db
from api.database import Base
from scanners.user_friendly import UserFriendlyScanManager, ScanCategory, ProjectType

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_user_friendly.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

class TestUserFriendlyScanManager:
    
    def test_initialization(self):
        manager = UserFriendlyScanManager()
        assert len(manager.scan_options) == 7
        assert ScanCategory.CODE_SECURITY in manager.scan_options
        assert ScanCategory.FULL_SECURITY_AUDIT in manager.scan_options
    
    def test_get_scan_options_for_frontend(self):
        manager = UserFriendlyScanManager()
        options = manager.get_scan_options_for_frontend()
        
        assert len(options) == 7
        
        # Check structure of first option
        first_option = options[0]
        required_fields = ["value", "label", "description", "use_case", "estimated_time", "complexity", "icon", "tools_used"]
        for field in required_fields:
            assert field in first_option
        
        # Check that we have the expected scan types
        values = [opt["value"] for opt in options]
        assert "code_security" in values
        assert "dependency_security" in values
        assert "secret_detection" in values
        assert "full_security_audit" in values
    
    def test_project_type_detection_python(self):
        manager = UserFriendlyScanManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python project structure
            py_file = os.path.join(temp_dir, "main.py")
            with open(py_file, "w") as f:
                f.write("print('hello world')")
                
            requirements_file = os.path.join(temp_dir, "requirements.txt")
            with open(requirements_file, "w") as f:
                f.write("requests==2.28.0")
                
            project_type = manager.detect_project_type(temp_dir)
            assert project_type == ProjectType.PYTHON_APP
    
    def test_project_type_detection_javascript(self):
        manager = UserFriendlyScanManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            package_json = os.path.join(temp_dir, "package.json")
            with open(package_json, "w") as f:
                f.write('{"name": "test-app", "dependencies": {}}')
                
            project_type = manager.detect_project_type(temp_dir)
            assert project_type == ProjectType.JAVASCRIPT_APP
    
    def test_project_type_detection_container(self):
        manager = UserFriendlyScanManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dockerfile = os.path.join(temp_dir, "Dockerfile")
            with open(dockerfile, "w") as f:
                f.write("FROM python:3.9\nRUN pip install requests")
                
            project_type = manager.detect_project_type(temp_dir)
            assert project_type == ProjectType.CONTAINER_APP
    
    def test_get_recommended_scans_python_project(self):
        manager = UserFriendlyScanManager()
        recommendations = manager.get_recommended_scans(ProjectType.PYTHON_APP)
        
        assert len(recommendations) > 0
        
        # Should recommend code security for Python projects
        rec_categories = [rec["category"] for rec in recommendations]
        assert "code_security" in rec_categories
        assert "secret_detection" in rec_categories
        
        # Should be sorted by priority
        assert recommendations[0]["priority"] >= recommendations[-1]["priority"]
    
    def test_get_recommended_scans_container_project(self):
        manager = UserFriendlyScanManager()
        recommendations = manager.get_recommended_scans(ProjectType.CONTAINER_APP)
        
        rec_categories = [rec["category"] for rec in recommendations]
        assert "container_security" in rec_categories
        assert "secret_detection" in rec_categories
    
    def test_map_user_choice_to_technical_scans_code_security(self):
        manager = UserFriendlyScanManager()
        
        config = manager.map_user_choice_to_technical_scans("code_security")
        
        assert "scan_types" in config
        assert "display_info" in config
        assert "execution_config" in config
        
        # Should include appropriate tools for code security
        assert "bandit" in config["scan_types"] or "semgrep" in config["scan_types"]
        
        # Should have display information
        assert "chosen_scan" in config["display_info"]
        assert "Code Security Analysis" in config["display_info"]["chosen_scan"]
    
    def test_map_user_choice_to_technical_scans_with_project_optimization(self):
        manager = UserFriendlyScanManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Python project
            py_file = os.path.join(temp_dir, "main.py")
            with open(py_file, "w") as f:
                f.write("print('hello')")
                
            # Also create requirements.txt to make it more clearly a Python project
            req_file = os.path.join(temp_dir, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("requests==2.25.1")
                
            config = manager.map_user_choice_to_technical_scans("code_security", temp_dir)
            
            # Should have project optimizations for Python
            assert "project_optimizations" in config
            assert "semgrep_config" in config["project_optimizations"]
            assert "exclude_patterns" in config["project_optimizations"]
    
    def test_map_user_choice_invalid_category(self):
        manager = UserFriendlyScanManager()
        
        with pytest.raises(ValueError):
            manager.map_user_choice_to_technical_scans("invalid_category")
    
    def test_optimize_tools_for_python_project(self):
        manager = UserFriendlyScanManager()
        
        tools = ["semgrep", "bandit", "snyk"]
        optimized = manager._optimize_tools_for_project(tools, ProjectType.PYTHON_APP)
        
        # Bandit should be prioritized for Python projects
        assert optimized[0] == "bandit"
    
    def test_optimize_tools_for_javascript_project(self):
        manager = UserFriendlyScanManager()
        
        tools = ["semgrep", "bandit", "snyk"]
        optimized = manager._optimize_tools_for_project(tools, ProjectType.JAVASCRIPT_APP)
        
        # Bandit should be removed for JavaScript projects
        assert "bandit" not in optimized
        assert "semgrep" in optimized
    
    def test_get_project_optimizations(self):
        manager = UserFriendlyScanManager()
        
        # Test Python optimizations
        python_opts = manager._get_project_optimizations(ProjectType.PYTHON_APP)
        assert "semgrep_config" in python_opts
        assert python_opts["semgrep_config"] == "p/python"
        
        # Test JavaScript optimizations
        js_opts = manager._get_project_optimizations(ProjectType.JAVASCRIPT_APP)
        assert "semgrep_config" in js_opts
        assert python_opts["semgrep_config"] == "p/python"

class TestUserFriendlyAPI:
    
    def test_get_scan_options_endpoint(self):
        response = client.get("/api/scan/options")
        assert response.status_code == 200
        
        data = response.json()
        assert "scan_options" in data
        assert "message" in data
        assert len(data["scan_options"]) == 7
        
        # Check structure of options
        first_option = data["scan_options"][0]
        assert "value" in first_option
        assert "label" in first_option
        assert "description" in first_option
    
    def test_simple_scan_endpoint_success(self):
        response = client.post("/api/scan/simple", json={
            "repository_url": "https://github.com/test/repo",
            "scan_category": "code_security",
            "project_name": "Test Project"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "scan_id" in data
        assert "scan_details" in data
        assert data["status"] == "running"
    
    def test_simple_scan_endpoint_missing_url(self):
        response = client.post("/api/scan/simple", json={
            "scan_category": "code_security"
        })
        
        assert response.status_code == 400
        assert "repository_url is required" in response.json()["detail"]
    
    def test_simple_scan_endpoint_missing_category(self):
        response = client.post("/api/scan/simple", json={
            "repository_url": "https://github.com/test/repo"
        })
        
        assert response.status_code == 400
        assert "scan_category is required" in response.json()["detail"]
    
    def test_simple_scan_endpoint_invalid_category(self):
        response = client.post("/api/scan/simple", json={
            "repository_url": "https://github.com/test/repo",
            "scan_category": "invalid_category"
        })
        
        assert response.status_code == 400
        assert "Invalid scan_category" in response.json()["detail"]
    
    def test_scan_recommendations_endpoint_with_url(self):
        response = client.post("/api/scan/recommendations", json={
            "repository_url": "https://github.com/test/python-app"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "detected_project_type" in data
        assert "recommendations" in data
        assert "message" in data
        assert len(data["recommendations"]) > 0
    
    def test_scan_recommendations_endpoint_missing_input(self):
        response = client.post("/api/scan/recommendations", json={})
        
        assert response.status_code == 400
        assert "Either repository_url or path is required" in response.json()["detail"]

class TestScanOptionContent:
    """Test the content and quality of scan options"""
    
    def test_all_scan_options_have_required_fields(self):
        manager = UserFriendlyScanManager()
        
        for category, option in manager.scan_options.items():
            assert option.display_name is not None
            assert len(option.display_name) > 0
            assert option.description is not None
            assert len(option.description) > 10  # Meaningful description
            assert option.use_case is not None
            assert len(option.technical_tools) > 0
            assert option.estimated_time is not None
            assert option.complexity in ["Simple", "Moderate", "Advanced"]
    
    def test_scan_options_cover_all_major_security_areas(self):
        manager = UserFriendlyScanManager()
        options = manager.get_scan_options_for_frontend()
        
        # Check that we cover major security areas
        descriptions = " ".join([opt["description"].lower() for opt in options])
        
        # Should mention key security concepts
        assert "vulnerabilities" in descriptions
        assert "dependencies" in descriptions or "libraries" in descriptions
        assert "secrets" in descriptions or "credentials" in descriptions or "sensitive information" in descriptions
        assert "container" in descriptions or "docker" in descriptions
    
    def test_time_estimates_are_reasonable(self):
        manager = UserFriendlyScanManager()
        
        for option in manager.scan_options.values():
            time_str = option.estimated_time.lower()
            # Should contain time information
            assert any(unit in time_str for unit in ["minute", "min", "second", "sec"])
            # Should not be overly long
            assert "hour" not in time_str  # Scans shouldn't take hours
    
    def test_tools_mapping_makes_sense(self):
        manager = UserFriendlyScanManager()
        
        # Code security should use SAST tools
        code_security = manager.scan_options[ScanCategory.CODE_SECURITY]
        assert any(tool in ["bandit", "semgrep"] for tool in code_security.technical_tools)
        
        # Dependency security should use dependency scanners
        dep_security = manager.scan_options[ScanCategory.DEPENDENCY_SECURITY]
        assert any(tool in ["pip-audit", "snyk"] for tool in dep_security.technical_tools)
        
        # Container security should use container tools
        container_security = manager.scan_options[ScanCategory.CONTAINER_SECURITY]
        assert any(tool in ["trivy", "snyk"] for tool in container_security.technical_tools)

# Cleanup
def teardown_module():
    """Clean up test database"""
    import time
    try:
        # Give some time for connections to close
        time.sleep(1)
        if os.path.exists("./test_user_friendly.db"):
            os.remove("./test_user_friendly.db")
    except PermissionError:
        # Database is still in use, try to close connections
        import gc
        gc.collect()
        time.sleep(2)
        try:
            if os.path.exists("./test_user_friendly.db"):
                os.remove("./test_user_friendly.db")
        except PermissionError:
            print("Warning: Could not clean up test database - it may be in use")