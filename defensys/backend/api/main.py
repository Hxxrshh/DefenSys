from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os

from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from scanners.executor import run_scan_for_project

app = FastAPI(title="DefenSys API")

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

class ScanRequest(BaseModel):
    repository_url: str
    scan_types: List[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the DefenSys API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "DefenSys API is running"}

@app.get("/api/scanners")
def get_scanner_info():
    """Get information about available scanners"""
    from scanners.manager import ScannerManager
    
    scanner_manager = ScannerManager()
    
    return {
        "available_scanners": scanner_manager.get_available_scanners(),
        "scanner_availability": scanner_manager.check_scanner_availability(),
        "scanner_info": {
            name: scanner_manager.get_scanner_info(name) 
            for name in scanner_manager.all_scanners.keys()
        }
    }

@app.get("/api/scan/options")
def get_user_friendly_scan_options():
    """Get user-friendly scan options for frontend dropdown"""
    from scanners.user_friendly import UserFriendlyScanManager
    
    scan_manager = UserFriendlyScanManager()
    return {
        "scan_options": scan_manager.get_scan_options_for_frontend(),
        "message": "Choose the type of security check you want to perform"
    }

@app.post("/api/scan/simple")
async def start_simple_scan(
    scan_request: dict, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Start a scan using user-friendly scan categories
    
    Expected request format:
    {
        "repository_url": "https://github.com/user/repo",
        "scan_category": "code_security",  // User-friendly category
        "project_name": "My Project" (optional)
    }
    """
    from scanners.user_friendly import UserFriendlyScanManager, ScanCategory
    
    # Validate request
    repository_url = scan_request.get("repository_url")
    scan_category = scan_request.get("scan_category")
    project_name = scan_request.get("project_name")
    
    if not repository_url:
        raise HTTPException(status_code=400, detail="repository_url is required")
    if not scan_category:
        raise HTTPException(status_code=400, detail="scan_category is required")
    
    # Validate scan category
    valid_categories = [cat.value for cat in ScanCategory]
    if scan_category not in valid_categories:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid scan_category. Valid options: {valid_categories}"
        )
    
    # Check if project exists, if not create it
    project = crud.get_project_by_repository_url(db, repository_url=repository_url)
    if not project:
        project_name = project_name or repository_url.split("/")[-1]
        project_data = schemas.ProjectCreate(
            name=project_name, 
            repository_url=repository_url,
            description=f"Auto-created for {scan_category} scan"
        )
        project = crud.create_project(db, project_data)

    # Create scan record
    scan_data = schemas.ScanCreate(
        project_id=project.id, 
        status="running",
        scan_type=scan_category
    )
    scan = crud.create_scan(db, scan_data)

    # Get user-friendly scan manager
    friendly_manager = UserFriendlyScanManager()
    
    # Convert user choice to technical configuration
    scan_config = friendly_manager.map_user_choice_to_technical_scans(scan_category)
    
    # Run the scan in background
    background_tasks.add_task(
        run_user_friendly_scan, 
        scan.id, 
        repository_url, 
        scan_config
    )

    return {
        "message": "Security scan started successfully!",
        "scan_id": scan.id,
        "scan_details": scan_config["display_info"],
        "status": "running"
    }

@app.post("/api/scan/recommendations")
def get_scan_recommendations_for_project(request: dict):
    """Get personalized scan recommendations based on project analysis"""
    from scanners.user_friendly import UserFriendlyScanManager
    
    repository_url = request.get("repository_url")
    local_path = request.get("path")
    
    if not repository_url and not local_path:
        raise HTTPException(status_code=400, detail="Either repository_url or path is required")
    
    friendly_manager = UserFriendlyScanManager()
    
    # For now, we'll use a dummy project type detection
    # In a real scenario, we might clone the repo first to analyze it
    if local_path:
        project_type = friendly_manager.detect_project_type(local_path)
    else:
        # Basic detection from URL patterns
        from scanners.user_friendly import ProjectType
        if "python" in repository_url.lower() or "django" in repository_url.lower():
            project_type = ProjectType.PYTHON_APP
        elif "node" in repository_url.lower() or "react" in repository_url.lower():
            project_type = ProjectType.JAVASCRIPT_APP
        elif "docker" in repository_url.lower():
            project_type = ProjectType.CONTAINER_APP
        elif "terraform" in repository_url.lower() or "infrastructure" in repository_url.lower():
            project_type = ProjectType.INFRASTRUCTURE
        else:
            project_type = ProjectType.GENERAL_PROJECT
    
    recommendations = friendly_manager.get_recommended_scans(project_type)
    
    return {
        "detected_project_type": project_type.value,
        "recommendations": recommendations,
        "message": f"Based on your {project_type.value.replace('_', ' ')}, here are our security scan recommendations"
    }

def run_user_friendly_scan(scan_id: int, repository_url: str, scan_config: dict):
    """Run scan using user-friendly configuration"""
    from scanners.executor import run_scan_for_project
    
    # Create a new database session for the background task
    db = SessionLocal()
    try:
        # Extract technical scan types from user-friendly config
        scan_types = scan_config["scan_types"]
        execution_config = scan_config.get("execution_config", {})
        
        print(f"🚀 Starting {scan_config['display_info']['chosen_scan']}")
        print(f"📋 Description: {scan_config['display_info']['description']}")
        print(f"⏱️ Estimated time: {scan_config['display_info']['estimated_time']}")
        print(f"🔧 Tools to run: {', '.join(scan_config['display_info']['tools_to_run'])}")
        
        # Run the scan with optimized configuration
        scan_results = run_scan_for_project(
            repository_url=repository_url,
            scan_types=scan_types,
            **execution_config
        )

        # Process and save results
        if scan_results:
            vulnerability_count = 0
            for result in scan_results:
                vuln_data = schemas.VulnerabilityCreate(
                    scan_id=scan_id,
                    type=result.get("scanner_type", result.get("type", "unknown")),
                    severity=result.get("severity", "UNKNOWN"),
                    description=result.get("description", result.get("title", result.get("message", "N/A"))),
                    file_path=result.get("file_path", result.get("file", result.get("filename", "N/A"))),
                    line_number=result.get("line", result.get("line_number", result.get("start_line"))),
                )
                crud.create_vulnerability(db, vuln_data)
                vulnerability_count += 1
            
            print(f"✅ Scan completed! Found {vulnerability_count} security findings")
            crud.update_scan_status(db, scan_id, "completed")
        else:
            print("✅ Scan completed with no issues found")
            crud.update_scan_status(db, scan_id, "completed")
            
    except Exception as e:
        print(f"❌ Scan failed: {str(e)}")
        crud.update_scan_status(db, scan_id, "failed")
    finally:
        db.close()

@app.post("/api/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project_by_repository_url(db, repository_url=project.repository_url)
    if db_project:
        raise HTTPException(status_code=400, detail="Project with this repository URL already registered")
    return crud.create_project(db=db, project=project)

@app.get("/api/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@app.get("/api/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.post("/api/scans/", response_model=schemas.Scan)
def create_scan(scan: schemas.ScanCreate, db: Session = Depends(get_db)):
    return crud.create_scan(db=db, scan=scan)

@app.get("/api/scans/", response_model=List[schemas.Scan])
def read_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scans = crud.get_scans(db, skip=skip, limit=limit)
    return scans

@app.post("/api/scan")
async def start_new_scan(scan_request: ScanRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if project exists, if not create it
    project = crud.get_project_by_repository_url(db, repository_url=scan_request.repository_url)
    if not project:
        project_data = schemas.ProjectCreate(name=scan_request.repository_url.split("/")[-1], repository_url=scan_request.repository_url)
        project = crud.create_project(db, project_data)

    # Create a new scan record in the database
    scan_data = schemas.ScanCreate(project_id=project.id, status="running")
    scan = crud.create_scan(db, scan_data)

    # Run the scan in the background
    background_tasks.add_task(run_and_process_scan, scan.id, scan_request.repository_url, scan_request.scan_types)

    return {"message": "Scan started in the background", "scan_id": scan.id}

def run_and_process_scan(scan_id: int, repository_url: str, scan_types: list):
    # Create a new database session for the background task
    db = SessionLocal()
    try:
        # Run the scan
        scan_results = run_scan_for_project(
            repository_url=repository_url,
            scan_types=scan_types
        )

        # Process and save the results
        if scan_results:
            for result in scan_results:  # scan_results is now a flat list
                # Extract vulnerability data from the standardized format
                vuln_data = schemas.VulnerabilityCreate(
                    scan_id=scan_id,
                    type=result.get("scanner_type", result.get("type", "unknown")),
                    severity=result.get("severity", "UNKNOWN"),
                    description=result.get("description", result.get("title", result.get("message", "N/A"))),
                    file_path=result.get("file_path", result.get("file", result.get("filename", "N/A"))),
                    line_number=result.get("line", result.get("line_number", result.get("start_line"))),
                )
                crud.create_vulnerability(db, vuln_data)
            
            # Update scan status
            crud.update_scan_status(db, scan_id, "completed")
        else:
            crud.update_scan_status(db, scan_id, "failed")
    finally:
        db.close()

@app.get("/user_friendly_scanner.html")
async def serve_user_friendly_scanner():
    """Serve the user-friendly scanner HTML interface"""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_friendly_scanner.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        raise HTTPException(status_code=404, detail="Scanner interface not found")

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {"message": "DefenSys API - User-Friendly Security Scanner", "scanner_ui": "/user_friendly_scanner.html"}
