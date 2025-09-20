"""
Enhanced Caching and Streaming System for DefenSys
Implements intelligent caching and file streaming for optimal performance
"""

import asyncio
import aiofiles
import aioredis
import hashlib
import json
import pickle
import gzip
import time
from typing import Dict, List, Optional, AsyncGenerator, Tuple
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

@dataclass
class FileChunk:
    """Represents a file chunk for streaming processing"""
    chunk_id: str
    path: str
    start_line: int
    end_line: int
    content: str
    size: int  # bytes

@dataclass
class StreamingResult:
    """Streaming scan result for progressive updates"""
    scanner_name: str
    chunk_id: str
    findings: List[dict]
    progress: float  # 0.0 to 1.0
    total_chunks: int
    processed_chunks: int

class AdvancedCacheManager:
    """
    Redis-based caching system with intelligent invalidation
    Achieves O(1) lookup and storage complexity
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.cache_ttl = {
            "scan_results": 3600,  # 1 hour for scan results
            "file_hashes": 86400,  # 24 hours for file hashes
            "project_analysis": 7200,  # 2 hours for project analysis
            "dependency_cache": 14400,  # 4 hours for dependencies
        }
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False  # We'll handle binary data
            )
            await self.redis_client.ping()
            print("✅ Advanced cache manager initialized")
        except Exception as e:
            print(f"⚠️ Redis cache unavailable: {e}")
            self.redis_client = None
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _generate_hierarchical_cache_key(self, category: str, scanner: str, path: str, **kwargs) -> str:
        """Generate hierarchical cache key for efficient organization"""
        # Create path hierarchy
        path_parts = Path(path).parts
        path_hierarchy = "/".join(path_parts[-3:])  # Last 3 path components
        
        # Include relevant kwargs in key
        relevant_kwargs = {k: v for k, v in kwargs.items() if k in [
            'scan_type', 'language', 'config', 'target_type'
        ]}
        
        key_data = {
            "scanner": scanner,
            "path_hierarchy": path_hierarchy,
            "kwargs": sorted(relevant_kwargs.items())
        }
        
        key_hash = hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:12]
        return f"{category}:{scanner}:{key_hash}"
    
    async def get_cached_scan_result(self, scanner: str, path: str, **kwargs) -> Optional[Dict]:
        """Get cached scan result with O(1) lookup"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_hierarchical_cache_key("scan", scanner, path, **kwargs)
            
            # Check if cache entry exists and is valid
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                # Decompress and deserialize
                decompressed_data = gzip.decompress(cached_data)
                result = pickle.loads(decompressed_data)
                
                # Validate cache freshness
                if await self._is_cache_valid(cache_key, path):
                    print(f"🎯 Cache hit for {scanner}")
                    return result
                else:
                    # Cache is stale, remove it
                    await self.redis_client.delete(cache_key)
                    print(f"🔄 Cache invalidated for {scanner}")
            
        except Exception as e:
            print(f"Cache lookup error: {e}")
        
        return None
    
    async def cache_scan_result(self, scanner: str, path: str, result: Dict, **kwargs):
        """Cache scan result with compression and TTL"""
        if not self.redis_client:
            return
        
        try:
            cache_key = self._generate_hierarchical_cache_key("scan", scanner, path, **kwargs)
            
            # Add cache metadata
            cached_result = {
                "result": result,
                "cached_at": time.time(),
                "scanner": scanner,
                "path_checksum": await self._get_path_checksum_async(path)
            }
            
            # Compress and serialize
            serialized_data = pickle.dumps(cached_result)
            compressed_data = gzip.compress(serialized_data)
            
            # Store with TTL
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl["scan_results"],
                compressed_data
            )
            
            # Store path checksum for validation
            checksum_key = f"checksum:{path}"
            await self.redis_client.setex(
                checksum_key,
                self.cache_ttl["file_hashes"],
                cached_result["path_checksum"]
            )
            
        except Exception as e:
            print(f"Cache storage error: {e}")
    
    async def _is_cache_valid(self, cache_key: str, path: str) -> bool:
        """Check if cached result is still valid based on file changes"""
        try:
            # Get current path checksum
            current_checksum = await self._get_path_checksum_async(path)
            
            # Get cached checksum
            checksum_key = f"checksum:{path}"
            cached_checksum = await self.redis_client.get(checksum_key)
            
            if cached_checksum:
                return current_checksum == cached_checksum.decode() if isinstance(cached_checksum, bytes) else current_checksum == cached_checksum
            
        except Exception as e:
            print(f"Cache validation error: {e}")
        
        return False
    
    async def _get_path_checksum_async(self, path: str) -> str:
        """Asynchronously calculate path checksum"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_path_checksum_sync, path)
    
    def _get_path_checksum_sync(self, path: str) -> str:
        """Synchronously calculate path checksum"""
        hasher = hashlib.md5()
        try:
            for root, dirs, files in os.walk(path):
                for file in sorted(files):
                    filepath = os.path.join(root, file)
                    try:
                        stat = os.stat(filepath)
                        hasher.update(f"{file}:{stat.st_mtime}:{stat.st_size}".encode())
                    except:
                        continue
        except:
            hasher.update(path.encode())
        return hasher.hexdigest()
    
    async def cache_dependency_analysis(self, path: str, dependencies: Dict):
        """Cache dependency analysis results"""
        if not self.redis_client:
            return
        
        cache_key = f"deps:{hashlib.md5(path.encode()).hexdigest()}"
        serialized_data = pickle.dumps(dependencies)
        compressed_data = gzip.compress(serialized_data)
        
        await self.redis_client.setex(
            cache_key,
            self.cache_ttl["dependency_cache"],
            compressed_data
        )
    
    async def get_cached_dependency_analysis(self, path: str) -> Optional[Dict]:
        """Get cached dependency analysis"""
        if not self.redis_client:
            return None
        
        cache_key = f"deps:{hashlib.md5(path.encode()).hexdigest()}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            decompressed_data = gzip.decompress(cached_data)
            return pickle.loads(decompressed_data)
        
        return None
    
    async def invalidate_cache_for_path(self, path: str):
        """Invalidate all cache entries for a specific path"""
        if not self.redis_client:
            return
        
        try:
            # Find all keys related to this path
            pattern = f"*{hashlib.md5(path.encode()).hexdigest()[:8]}*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                await self.redis_client.delete(*keys)
                print(f"🗑️ Invalidated {len(keys)} cache entries for {path}")
        
        except Exception as e:
            print(f"Cache invalidation error: {e}")


class StreamingFileProcessor:
    """
    File streaming processor for handling large files efficiently
    Reduces memory usage from O(n) to O(1) where n = file size
    """
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        self.chunk_size = chunk_size
        self.supported_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
            '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala'
        }
    
    async def stream_file_chunks(self, file_path: str) -> AsyncGenerator[FileChunk, None]:
        """Stream file in chunks for memory-efficient processing"""
        if not self._should_stream_file(file_path):
            # For small files, read entire content
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
                yield FileChunk(
                    chunk_id="full",
                    path=file_path,
                    start_line=1,
                    end_line=content.count('\n') + 1,
                    content=content,
                    size=len(content.encode('utf-8'))
                )
            return
        
        # Stream large files in chunks
        chunk_number = 0
        current_line = 1
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk_content = ""
                chunk_start_line = current_line
                bytes_read = 0
                
                while bytes_read < self.chunk_size:
                    line = await f.readline()
                    if not line:
                        break
                    
                    chunk_content += line
                    bytes_read += len(line.encode('utf-8'))
                    current_line += 1
                
                if not chunk_content:
                    break
                
                yield FileChunk(
                    chunk_id=f"chunk_{chunk_number}",
                    path=file_path,
                    start_line=chunk_start_line,
                    end_line=current_line - 1,
                    content=chunk_content,
                    size=bytes_read
                )
                
                chunk_number += 1
    
    def _should_stream_file(self, file_path: str) -> bool:
        """Determine if file should be streamed based on size and type"""
        try:
            file_size = os.path.getsize(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            # Stream if file is large or has supported extension
            return (file_size > self.chunk_size or 
                   file_ext in self.supported_extensions)
        except:
            return False
    
    async def process_directory_streaming(self, directory: str) -> AsyncGenerator[Tuple[str, FileChunk], None]:
        """Stream process all files in directory"""
        for root, dirs, files in os.walk(directory):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                'node_modules', '__pycache__', 'build', 'dist', 'target'
            }]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip binary files and common non-source files
                if self._is_source_file(file_path):
                    try:
                        async for chunk in self.stream_file_chunks(file_path):
                            yield (file_path, chunk)
                    except Exception as e:
                        print(f"⚠️ Error processing {file_path}: {e}")
    
    def _is_source_file(self, file_path: str) -> bool:
        """Check if file is a source code file worth scanning"""
        file_ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        # Include source code files and common config files
        source_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
            '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.yaml', '.yml', '.json', '.xml', '.toml', '.ini',
            '.sql', '.sh', '.bash', '.ps1', '.dockerfile'
        }
        
        config_files = {
            'dockerfile', 'requirements.txt', 'package.json', 'pom.xml',
            'build.gradle', 'cargo.toml', 'go.mod', 'composer.json'
        }
        
        return (file_ext in source_extensions or 
                filename in config_files or
                'dockerfile' in filename)


class IncrementalScanManager:
    """
    Manages incremental scanning to minimize redundant work
    Achieves O(k) complexity where k = number of changed files
    """
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.git_available = self._check_git_availability()
    
    def _check_git_availability(self) -> bool:
        """Check if git is available for change tracking"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    async def get_changed_files_since_commit(self, repo_path: str, commit_hash: Optional[str] = None) -> List[str]:
        """Get list of files changed since specific commit"""
        if not self.git_available:
            return []
        
        try:
            if commit_hash is None:
                # Get files changed since last commit
                cmd = ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD']
            else:
                cmd = ['git', 'diff', '--name-only', commit_hash, 'HEAD']
            
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                changed_files = [
                    os.path.join(repo_path, line.strip())
                    for line in result.stdout.strip().split('\n')
                    if line.strip()
                ]
                return changed_files
        
        except Exception as e:
            print(f"Git change detection failed: {e}")
        
        return []
    
    async def get_incremental_scan_plan(self, path: str, scanners: List[str]) -> Dict[str, List[str]]:
        """Create incremental scan plan based on file changes"""
        changed_files = await self.get_changed_files_since_commit(path)
        
        scan_plan = {
            "full_scan_needed": [],
            "partial_scan_needed": [],
            "cache_valid": []
        }
        
        if not changed_files:
            # No changes detected, check cache validity
            for scanner in scanners:
                if await self.cache_manager.get_cached_scan_result(scanner, path):
                    scan_plan["cache_valid"].append(scanner)
                else:
                    scan_plan["full_scan_needed"].append(scanner)
        else:
            # Determine which scanners need to run based on changed files
            for scanner in scanners:
                if self._scanner_affected_by_changes(scanner, changed_files):
                    scan_plan["partial_scan_needed"].append(scanner)
                else:
                    # Check if we have valid cache for this scanner
                    if await self.cache_manager.get_cached_scan_result(scanner, path):
                        scan_plan["cache_valid"].append(scanner)
                    else:
                        scan_plan["full_scan_needed"].append(scanner)
        
        return scan_plan
    
    def _scanner_affected_by_changes(self, scanner: str, changed_files: List[str]) -> bool:
        """Determine if scanner is affected by file changes"""
        scanner_file_patterns = {
            "sast": [".py"],
            "dependency": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "secret": ["*"],  # All files could contain secrets
            "snyk": ["package.json", "requirements.txt", "pom.xml", "build.gradle"],
            "trivy": ["Dockerfile", "requirements.txt", "package.json"],
            "semgrep": [".py", ".js", ".ts", ".java", ".go"],
            "gitleaks": ["*"],  # All files could contain secrets
            "safety": ["requirements.txt", "setup.py"],
            "npm_audit": ["package.json", "package-lock.json"],
            "yarn_audit": ["package.json", "yarn.lock"]
        }
        
        patterns = scanner_file_patterns.get(scanner, ["*"])
        
        for file_path in changed_files:
            filename = Path(file_path).name
            file_ext = Path(file_path).suffix
            
            for pattern in patterns:
                if pattern == "*":
                    return True
                elif pattern.startswith(".") and file_ext == pattern:
                    return True
                elif filename == pattern:
                    return True
        
        return False


# Integration class
class OptimizedScanningSystem:
    """
    Complete optimized scanning system combining all optimization techniques
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.cache_manager = AdvancedCacheManager(redis_url)
        self.file_processor = StreamingFileProcessor()
        self.incremental_manager = IncrementalScanManager(self.cache_manager)
    
    async def initialize(self):
        """Initialize all components"""
        await self.cache_manager.initialize()
    
    async def close(self):
        """Close all components"""
        await self.cache_manager.close()
    
    async def optimized_scan_with_streaming(
        self, 
        scanner_name: str, 
        path: str, 
        **kwargs
    ) -> AsyncGenerator[StreamingResult, None]:
        """
        Perform optimized scan with streaming results
        Best case: O(1) with cache hit
        Worst case: O(k) where k = number of changed files
        """
        # Check cache first
        cached_result = await self.cache_manager.get_cached_scan_result(scanner_name, path, **kwargs)
        if cached_result:
            yield StreamingResult(
                scanner_name=scanner_name,
                chunk_id="cached",
                findings=cached_result.get("result", []),
                progress=1.0,
                total_chunks=1,
                processed_chunks=1
            )
            return
        
        # Stream process files
        total_chunks = 0
        processed_chunks = 0
        all_findings = []
        
        # Count total chunks for progress tracking
        async for file_path, chunk in self.file_processor.process_directory_streaming(path):
            total_chunks += 1
        
        # Process chunks and stream results
        async for file_path, chunk in self.file_processor.process_directory_streaming(path):
            # Process chunk with scanner (simplified - would integrate with actual scanners)
            chunk_findings = await self._process_chunk_with_scanner(scanner_name, chunk, **kwargs)
            all_findings.extend(chunk_findings)
            processed_chunks += 1
            
            # Yield progressive result
            yield StreamingResult(
                scanner_name=scanner_name,
                chunk_id=chunk.chunk_id,
                findings=chunk_findings,
                progress=processed_chunks / total_chunks if total_chunks > 0 else 1.0,
                total_chunks=total_chunks,
                processed_chunks=processed_chunks
            )
        
        # Cache the final result
        await self.cache_manager.cache_scan_result(scanner_name, path, all_findings, **kwargs)
    
    async def _process_chunk_with_scanner(self, scanner_name: str, chunk: FileChunk, **kwargs) -> List[dict]:
        """Process file chunk with specific scanner (simplified implementation)"""
        # This would integrate with actual scanner implementations
        # For demonstration, return empty findings
        return []


# Example usage
async def demo_optimized_scanning():
    """Demonstrate optimized scanning capabilities"""
    system = OptimizedScanningSystem()
    await system.initialize()
    
    try:
        path = "/path/to/project"
        
        print("🚀 Starting optimized streaming scan...")
        start_time = time.time()
        
        async for result in system.optimized_scan_with_streaming("sast", path):
            print(f"📊 Progress: {result.progress:.1%} - "
                  f"{result.scanner_name} found {len(result.findings)} issues in {result.chunk_id}")
        
        total_time = time.time() - start_time
        print(f"⚡ Scan completed in {total_time:.2f}s")
        
    finally:
        await system.close()

if __name__ == "__main__":
    asyncio.run(demo_optimized_scanning())