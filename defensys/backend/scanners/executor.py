import subprocess
import tempfile
import os
from datetime import datetime
from .manager import ScannerManager

def run_scan_for_project(repository_url: str, scan_types: list = None, **kwargs):
    """
    Clones a repository and runs scans on it using the enhanced scanner manager.
    
    Args:
        repository_url: URL of the repository to scan
        scan_types: List of scan types to run (defaults to ["basic"])
        **kwargs: Additional execution configuration options
    
    Returns:
        List of vulnerability findings from all scanners
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository
            clone_path = os.path.join(temp_dir, "repo")
            subprocess.run(
                ["git", "clone", repository_url, clone_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for cloning
            )

            # Initialize scanner manager
            scanner_manager = ScannerManager()
            
            # Determine scan types to run
            if not scan_types:
                scan_types = ["basic"]
            
            # Get scan recommendations based on project content
            recommendations = scanner_manager.get_scan_recommendations(clone_path)
            print(f"📋 Scan recommendations: {recommendations}")
            
            # Check scanner availability
            availability = scanner_manager.check_scanner_availability()
            print(f"🔧 Scanner availability: {availability}")
            
            # Run scans
            all_results = []
            timestamp = datetime.now().isoformat()
            
            for scan_type in scan_types:
                try:
                    print(f"🚀 Starting {scan_type} scan...")
                    
                    # Prepare scan arguments - merge defaults with passed kwargs
                    scan_kwargs = {
                        'timestamp': timestamp,
                        'parallel': kwargs.get('parallel', True),  # Use passed value or default
                        'max_workers': kwargs.get('max_workers', 3),  # Use passed value or default  
                        'scanner_timeout': kwargs.get('scanner_timeout', 600)  # Use passed value or default
                    }
                    
                    # Run the scan
                    results = scanner_manager.run_scan(scan_type, clone_path, **scan_kwargs)
                    all_results.extend(results)
                    
                    print(f"✅ {scan_type} scan completed with {len(results)} findings")
                    
                except Exception as e:
                    print(f"❌ {scan_type} scan failed: {e}")
                    continue
            
            print(f"🎯 Total findings: {len(all_results)}")
            return all_results

        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e.stderr}")
            return []
        except subprocess.TimeoutExpired:
            print("Repository cloning timed out")
            return []
        except Exception as e:
            print(f"An error occurred during the scan: {str(e)}")
            return []

def run_local_scan(path: str, scan_types: list = None, **kwargs):
    """
    Run scans on a local directory without cloning.
    
    Args:
        path: Local path to scan
        scan_types: List of scan types to run
        **kwargs: Additional scanner arguments
    
    Returns:
        List of vulnerability findings
    """
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return []
        
    scanner_manager = ScannerManager()
    
    # Default to basic scan if no types specified
    if not scan_types:
        scan_types = ["basic"]
        
    all_results = []
    timestamp = datetime.now().isoformat()
    
    # Add default kwargs
    scan_kwargs = {
        'timestamp': timestamp,
        'parallel': kwargs.get('parallel', True),
        'max_workers': kwargs.get('max_workers', 3),
        'scanner_timeout': kwargs.get('scanner_timeout', 600),
        **kwargs
    }
    
    for scan_type in scan_types:
        try:
            print(f"🚀 Starting {scan_type} scan on local path...")
            results = scanner_manager.run_scan(scan_type, path, **scan_kwargs)
            all_results.extend(results)
            print(f"✅ {scan_type} scan completed with {len(results)} findings")
        except Exception as e:
            print(f"❌ {scan_type} scan failed: {e}")
            
    return all_results
