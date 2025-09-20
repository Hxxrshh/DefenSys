"""
Enhanced DefenSys API with Local File Upload Support
===================================================

This file extends the main API to support local file and folder uploads
for security scanning, providing users with multiple testing options.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import tempfile
import zipfile
import shutil
from pathlib import Path
import json

# Import existing API components
from api.main import app as main_app
from api import crud, models, schemas
from api.database import SessionLocal, get_db
from scanners.executor import run_scan_for_project

# Enhanced endpoints for local file/folder testing

@main_app.post("/api/upload/file")
async def upload_single_file_for_scan(
    file: UploadFile = File(...),
    scan_category: str = Form(...),
    project_name: Optional[str] = Form(None)
):
    """
    Upload a single file for security scanning
    
    Supports: .py, .js, .java, .php, .go, .rb, .ts, .jsx, etc.
    """
    from scanners.user_friendly import UserFriendlyScanManager
    
    # Validate file type
    allowed_extensions = {'.py', '.js', '.java', '.php', '.go', '.rb', '.ts', '.jsx', '.vue', '.c', '.cpp', '.cs'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary directory for the file
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / file.filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create project record
        db = SessionLocal()
        try:
            project_name = project_name or f"Upload-{file.filename}"
            project_data = schemas.ProjectCreate(
                name=project_name,
                repository_url=f"file:///{file.filename}",
                description=f"Uploaded file scan: {file.filename}"
            )
            project = crud.create_project(db, project_data)
            
            # Create scan record
            scan_data = schemas.ScanCreate(
                project_id=project.id,
                status="running", 
                scan_type=scan_category
            )
            scan = crud.create_scan(db, scan_data)
            
            # Get scan configuration
            friendly_manager = UserFriendlyScanManager()
            scan_config = friendly_manager.map_user_choice_to_technical_scans(scan_category)
            
            # Run scan on the temporary file
            scan_results = run_scan_for_project(
                repository_url=str(temp_dir),  # Scan the temp directory
                scan_types=scan_config["scan_types"]
            )
            
            # Process results
            vulnerability_count = 0
            if scan_results:
                for result in scan_results:
                    vuln_data = schemas.VulnerabilityCreate(
                        scan_id=scan.id,
                        type=result.get("scanner_type", "unknown"),
                        severity=result.get("severity", "UNKNOWN"),
                        description=result.get("description", "N/A"),
                        file_path=result.get("file_path", file.filename),
                        line_number=result.get("line", result.get("line_number"))
                    )
                    crud.create_vulnerability(db, vuln_data)
                    vulnerability_count += 1
                
                crud.update_scan_status(db, scan.id, "completed")
            else:
                crud.update_scan_status(db, scan.id, "completed")
            
            return {
                "message": f"File '{file.filename}' scanned successfully!",
                "scan_id": scan.id,
                "vulnerabilities_found": vulnerability_count,
                "scan_type": scan_category,
                "file_name": file.filename,
                "status": "completed"
            }
            
        finally:
            db.close()

@main_app.post("/api/upload/folder")
async def upload_folder_zip_for_scan(
    zip_file: UploadFile = File(...),
    scan_category: str = Form(...),
    project_name: Optional[str] = Form(None)
):
    """
    Upload a ZIP file containing a project folder for security scanning
    
    The ZIP file will be extracted and scanned as a complete project.
    """
    from scanners.user_friendly import UserFriendlyScanManager
    
    # Validate it's a ZIP file
    if not zip_file.filename.lower().endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported for folder uploads")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / zip_file.filename
        extract_path = Path(temp_dir) / "extracted"
        
        # Save uploaded ZIP file
        with open(zip_path, "wb") as buffer:
            content = await zip_file.read()
            buffer.write(content)
        
        # Extract ZIP file
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        
        # Create project record
        db = SessionLocal()
        try:
            project_name = project_name or f"Upload-{Path(zip_file.filename).stem}"
            project_data = schemas.ProjectCreate(
                name=project_name,
                repository_url=f"upload:///{zip_file.filename}",
                description=f"Uploaded project scan: {zip_file.filename}"
            )
            project = crud.create_project(db, project_data)
            
            # Create scan record
            scan_data = schemas.ScanCreate(
                project_id=project.id,
                status="running",
                scan_type=scan_category
            )
            scan = crud.create_scan(db, scan_data)
            
            # Get scan configuration
            friendly_manager = UserFriendlyScanManager()
            scan_config = friendly_manager.map_user_choice_to_technical_scans(scan_category)
            
            # Run scan on extracted folder
            scan_results = run_scan_for_project(
                repository_url=str(extract_path),
                scan_types=scan_config["scan_types"]
            )
            
            # Process results
            vulnerability_count = 0
            if scan_results:
                for result in scan_results:
                    # Make file paths relative to uploaded project
                    relative_path = result.get("file_path", "").replace(str(extract_path), "")
                    if relative_path.startswith("/") or relative_path.startswith("\\"):
                        relative_path = relative_path[1:]
                    
                    vuln_data = schemas.VulnerabilityCreate(
                        scan_id=scan.id,
                        type=result.get("scanner_type", "unknown"),
                        severity=result.get("severity", "UNKNOWN"), 
                        description=result.get("description", "N/A"),
                        file_path=relative_path or "unknown",
                        line_number=result.get("line", result.get("line_number"))
                    )
                    crud.create_vulnerability(db, vuln_data)
                    vulnerability_count += 1
                
                crud.update_scan_status(db, scan.id, "completed")
            else:
                crud.update_scan_status(db, scan.id, "completed")
            
            return {
                "message": f"Project '{zip_file.filename}' scanned successfully!",
                "scan_id": scan.id,
                "vulnerabilities_found": vulnerability_count,
                "scan_type": scan_category,
                "uploaded_file": zip_file.filename,
                "status": "completed"
            }
            
        finally:
            db.close()

@main_app.post("/api/scan/local-path")
async def scan_local_path(request: dict):
    """
    Scan a local file system path (for server-side file access)
    
    Useful when DefenSys is running on the same machine as the code to scan.
    """
    from scanners.user_friendly import UserFriendlyScanManager
    
    local_path = request.get("path")
    scan_category = request.get("scan_category", "code_security")
    project_name = request.get("project_name")
    
    if not local_path:
        raise HTTPException(status_code=400, detail="path is required")
    
    # Validate path exists
    path_obj = Path(local_path)
    if not path_obj.exists():
        raise HTTPException(status_code=404, detail=f"Path '{local_path}' does not exist")
    
    # Create project record
    db = SessionLocal()
    try:
        project_name = project_name or f"Local-{path_obj.name}"
        project_data = schemas.ProjectCreate(
            name=project_name,
            repository_url=f"file:///{local_path}",
            description=f"Local path scan: {local_path}"
        )
        project = crud.create_project(db, project_data)
        
        # Create scan record
        scan_data = schemas.ScanCreate(
            project_id=project.id,
            status="running",
            scan_type=scan_category
        )
        scan = crud.create_scan(db, scan_data)
        
        # Get scan configuration
        friendly_manager = UserFriendlyScanManager()
        scan_config = friendly_manager.map_user_choice_to_technical_scans(scan_category)
        
        # Run scan on local path
        scan_results = run_scan_for_project(
            repository_url=local_path,
            scan_types=scan_config["scan_types"]
        )
        
        # Process results
        vulnerability_count = 0
        if scan_results:
            for result in scan_results:
                vuln_data = schemas.VulnerabilityCreate(
                    scan_id=scan.id,
                    type=result.get("scanner_type", "unknown"),
                    severity=result.get("severity", "UNKNOWN"),
                    description=result.get("description", "N/A"),
                    file_path=result.get("file_path", "unknown"),
                    line_number=result.get("line", result.get("line_number"))
                )
                crud.create_vulnerability(db, vuln_data)
                vulnerability_count += 1
            
            crud.update_scan_status(db, scan.id, "completed")
        else:
            crud.update_scan_status(db, scan.id, "completed")
        
        return {
            "message": f"Local path '{local_path}' scanned successfully!",
            "scan_id": scan.id,
            "vulnerabilities_found": vulnerability_count,
            "scan_type": scan_category,
            "scanned_path": local_path,
            "status": "completed"
        }
        
    finally:
        db.close()

@main_app.get("/api/upload/supported-types")
def get_supported_file_types():
    """Get information about supported file types and scan categories"""
    return {
        "supported_file_extensions": [
            ".py", ".js", ".java", ".php", ".go", ".rb", ".ts", ".jsx", 
            ".vue", ".c", ".cpp", ".cs", ".scala", ".kotlin", ".swift"
        ],
        "supported_config_files": [
            "Dockerfile", "docker-compose.yml", "package.json", "requirements.txt",
            "pom.xml", "build.gradle", ".env", "config.py", "settings.py"
        ],
        "scan_categories": [
            "code_security", "secrets_check", "dependency_audit", 
            "container_security", "quick_overview", "comprehensive_audit"
        ],
        "upload_methods": [
            "single_file", "zip_folder", "local_path", "git_repository"
        ],
        "max_file_size": "50MB",
        "max_project_size": "100MB (compressed)"
    }

print("Enhanced DefenSys API loaded with local file upload support!")
print("New endpoints:")
print("• POST /api/upload/file - Upload single file for scanning")
print("• POST /api/upload/folder - Upload ZIP folder for scanning")  
print("• POST /api/scan/local-path - Scan local file system path")
print("• GET /api/upload/supported-types - Get supported file types")