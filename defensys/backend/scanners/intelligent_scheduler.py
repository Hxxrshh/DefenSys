"""
Intelligent Scheduler and Resource Manager for DefenSys
Implements dynamic resource allocation and optimal task scheduling
Achieves best-case O(log n) complexity for task scheduling
"""

import asyncio
import psutil
import time
import heapq
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import multiprocessing
import math
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1    # Security-critical scans (secrets, high-risk vulns)
    HIGH = 2        # Important scans (SAST, dependency)
    MEDIUM = 3      # Standard scans (linting, code quality)
    LOW = 4         # Optional scans (performance, documentation)

class ResourceType(Enum):
    """System resource types"""
    CPU_INTENSIVE = "cpu"       # CPU-bound tasks
    IO_INTENSIVE = "io"         # I/O-bound tasks  
    MEMORY_INTENSIVE = "memory" # Memory-bound tasks
    NETWORK_INTENSIVE = "network" # Network-bound tasks

@dataclass
class ResourceRequirement:
    """Resource requirements for a task"""
    cpu_cores: float = 1.0      # Number of CPU cores needed
    memory_mb: int = 128        # Memory requirement in MB
    disk_io_mb: int = 0         # Disk I/O requirement in MB
    network_mb: int = 0         # Network bandwidth in MB
    gpu_memory_mb: int = 0      # GPU memory if needed

@dataclass
class TaskMetrics:
    """Performance metrics for task execution"""
    average_duration: float = 60.0      # Average execution time
    cpu_utilization: float = 0.5        # Average CPU utilization (0-1)
    memory_peak: int = 128              # Peak memory usage in MB
    io_operations: int = 0              # Number of I/O operations
    success_rate: float = 0.95          # Historical success rate
    last_updated: float = field(default_factory=time.time)

@dataclass
class ScheduledTask:
    """Represents a task in the scheduler queue"""
    task_id: str
    scanner_name: str
    path: str
    priority: TaskPriority
    resource_type: ResourceType
    requirements: ResourceRequirement
    metrics: TaskMetrics
    dependencies: Set[str] = field(default_factory=set)
    estimated_start_time: float = 0.0
    estimated_completion_time: float = 0.0
    
    def __lt__(self, other):
        """For priority queue ordering"""
        # Sort by priority first, then by estimated completion time
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.estimated_completion_time < other.estimated_completion_time

class SystemResourceMonitor:
    """
    Real-time system resource monitoring
    Provides O(1) resource availability checks
    """
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.last_update = 0.0
        self._cached_stats = {}
        
        # Resource thresholds for optimal performance
        self.cpu_threshold = 0.8        # 80% CPU utilization limit
        self.memory_threshold = 0.85    # 85% memory utilization limit
        self.disk_threshold = 0.9       # 90% disk utilization limit
        
    def get_current_resources(self) -> Dict[str, float]:
        """Get current system resource utilization with caching"""
        current_time = time.time()
        
        if current_time - self.last_update > self.update_interval:
            self._update_resource_cache()
            self.last_update = current_time
        
        return self._cached_stats.copy()
    
    def _update_resource_cache(self):
        """Update cached resource statistics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            
            self._cached_stats = {
                # CPU
                "cpu_utilization": cpu_percent / 100.0,
                "cpu_count": cpu_count,
                "cpu_frequency_mhz": cpu_freq.current if cpu_freq else 2000,
                "available_cpu_cores": max(1, cpu_count * (1 - cpu_percent / 100.0)),
                
                # Memory
                "memory_utilization": memory.percent / 100.0,
                "available_memory_mb": memory.available // (1024 * 1024),
                "total_memory_mb": memory.total // (1024 * 1024),
                "swap_utilization": swap.percent / 100.0,
                
                # Disk
                "disk_utilization": disk.percent / 100.0,
                "available_disk_gb": disk.free // (1024 * 1024 * 1024),
                "disk_read_mb_per_sec": getattr(disk_io, 'read_bytes', 0) // (1024 * 1024),
                "disk_write_mb_per_sec": getattr(disk_io, 'write_bytes', 0) // (1024 * 1024),
                
                # Network
                "network_sent_mb": getattr(network, 'bytes_sent', 0) // (1024 * 1024),
                "network_recv_mb": getattr(network, 'bytes_recv', 0) // (1024 * 1024),
                
                # Load average (Unix-like systems)
                "load_average": getattr(psutil, 'getloadavg', lambda: (0, 0, 0))()[0],
                
                # Performance score (0-1, higher is better)
                "performance_score": self._calculate_performance_score(cpu_percent, memory.percent, disk.percent)
            }
            
        except Exception as e:
            logger.warning(f"Resource monitoring error: {e}")
            # Fallback values
            self._cached_stats = {
                "cpu_utilization": 0.5,
                "available_cpu_cores": multiprocessing.cpu_count(),
                "available_memory_mb": 1024,
                "performance_score": 0.5
            }
    
    def _calculate_performance_score(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> float:
        """Calculate overall system performance score"""
        cpu_score = max(0, 1 - cpu_percent / 100.0)
        memory_score = max(0, 1 - memory_percent / 100.0)
        disk_score = max(0, 1 - disk_percent / 100.0)
        
        # Weighted average (CPU and memory are more important)
        return (cpu_score * 0.4 + memory_score * 0.4 + disk_score * 0.2)
    
    def can_handle_task(self, requirements: ResourceRequirement) -> bool:
        """Check if system can handle additional task"""
        resources = self.get_current_resources()
        
        # Check CPU availability
        if requirements.cpu_cores > resources.get("available_cpu_cores", 1):
            return False
        
        # Check memory availability
        if requirements.memory_mb > resources.get("available_memory_mb", 0):
            return False
        
        # Check if system is under stress
        if resources.get("performance_score", 0) < 0.3:  # System under heavy load
            return False
        
        return True
    
    def get_optimal_worker_count(self, task_type: ResourceType) -> int:
        """Get optimal number of workers for task type"""
        resources = self.get_current_resources()
        cpu_count = resources.get("cpu_count", 4)
        performance_score = resources.get("performance_score", 0.5)
        
        if task_type == ResourceType.CPU_INTENSIVE:
            # CPU-bound tasks: use physical cores with performance adjustment
            base_workers = max(1, int(cpu_count * 0.8))  # Leave some CPU for OS
            return max(1, int(base_workers * performance_score))
        
        elif task_type == ResourceType.IO_INTENSIVE:
            # I/O-bound tasks: can use more workers than CPU cores
            base_workers = min(cpu_count * 2, 16)  # Cap at 16 workers
            return max(2, int(base_workers * performance_score))
        
        elif task_type == ResourceType.MEMORY_INTENSIVE:
            # Memory-bound tasks: limited by available memory
            available_mb = resources.get("available_memory_mb", 1024)
            workers_by_memory = max(1, available_mb // 512)  # 512MB per worker
            return min(workers_by_memory, cpu_count)
        
        else:  # NETWORK_INTENSIVE
            # Network-bound tasks: moderate parallelism
            return max(1, min(cpu_count, 8))

class IntelligentTaskScheduler:
    """
    Advanced task scheduler with dependency resolution and resource optimization
    Implements priority queue with O(log n) insertion and O(1) peek
    """
    
    def __init__(self, resource_monitor: SystemResourceMonitor):
        self.resource_monitor = resource_monitor
        self.task_queue = []  # Priority queue (heapq)
        self.running_tasks = {}  # Currently executing tasks
        self.completed_tasks = {}  # Completed task metrics
        self.task_dependencies = {}  # Task dependency graph
        self.scheduler_stats = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_wait_time": 0.0,
            "average_execution_time": 0.0
        }
        
        # Scanner performance profiles (learned from historical data)
        self.scanner_profiles = {
            "secret": {
                "priority": TaskPriority.CRITICAL,
                "resource_type": ResourceType.IO_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=1, memory_mb=64),
                "metrics": TaskMetrics(average_duration=20, cpu_utilization=0.3, memory_peak=64)
            },
            "dependency": {
                "priority": TaskPriority.HIGH,
                "resource_type": ResourceType.NETWORK_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=1, memory_mb=128, network_mb=10),
                "metrics": TaskMetrics(average_duration=30, cpu_utilization=0.4, memory_peak=128)
            },
            "sast": {
                "priority": TaskPriority.HIGH,
                "resource_type": ResourceType.CPU_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=2, memory_mb=256),
                "metrics": TaskMetrics(average_duration=45, cpu_utilization=0.7, memory_peak=256)
            },
            "snyk": {
                "priority": TaskPriority.MEDIUM,
                "resource_type": ResourceType.NETWORK_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=2, memory_mb=512, network_mb=20),
                "metrics": TaskMetrics(average_duration=90, cpu_utilization=0.6, memory_peak=512)
            },
            "trivy": {
                "priority": TaskPriority.MEDIUM,
                "resource_type": ResourceType.CPU_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=2, memory_mb=384),
                "metrics": TaskMetrics(average_duration=60, cpu_utilization=0.8, memory_peak=384)
            },
            "semgrep": {
                "priority": TaskPriority.MEDIUM,
                "resource_type": ResourceType.CPU_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=2, memory_mb=320),
                "metrics": TaskMetrics(average_duration=55, cpu_utilization=0.7, memory_peak=320)
            },
            "gitleaks": {
                "priority": TaskPriority.HIGH,
                "resource_type": ResourceType.IO_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=1, memory_mb=128),
                "metrics": TaskMetrics(average_duration=25, cpu_utilization=0.4, memory_peak=128)
            },
            "safety": {
                "priority": TaskPriority.MEDIUM,
                "resource_type": ResourceType.NETWORK_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=1, memory_mb=96, network_mb=5),
                "metrics": TaskMetrics(average_duration=20, cpu_utilization=0.3, memory_peak=96)
            },
            "npm_audit": {
                "priority": TaskPriority.MEDIUM,
                "resource_type": ResourceType.NETWORK_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=1, memory_mb=128, network_mb=15),
                "metrics": TaskMetrics(average_duration=35, cpu_utilization=0.4, memory_peak=128)
            },
            "yarn_audit": {
                "priority": TaskPriority.MEDIUM,
                "resource_type": ResourceType.NETWORK_INTENSIVE,
                "requirements": ResourceRequirement(cpu_cores=1, memory_mb=128, network_mb=15),
                "metrics": TaskMetrics(average_duration=40, cpu_utilization=0.4, memory_peak=128)
            }
        }
    
    def schedule_task(self, scanner_name: str, path: str, task_id: Optional[str] = None) -> str:
        """
        Schedule a scanner task with intelligent prioritization
        Returns task ID for tracking
        """
        if task_id is None:
            task_id = f"{scanner_name}_{int(time.time() * 1000)}"
        
        # Get scanner profile or create default
        profile = self.scanner_profiles.get(scanner_name, {
            "priority": TaskPriority.MEDIUM,
            "resource_type": ResourceType.CPU_INTENSIVE,
            "requirements": ResourceRequirement(),
            "metrics": TaskMetrics()
        })
        
        # Create scheduled task
        task = ScheduledTask(
            task_id=task_id,
            scanner_name=scanner_name,
            path=path,
            priority=profile["priority"],
            resource_type=profile["resource_type"],
            requirements=profile["requirements"],
            metrics=profile["metrics"]
        )
        
        # Calculate estimated times
        current_time = time.time()
        task.estimated_start_time = current_time + self._calculate_wait_time(task)
        task.estimated_completion_time = task.estimated_start_time + task.metrics.average_duration
        
        # Add to priority queue - O(log n) insertion
        heapq.heappush(self.task_queue, task)
        self.scheduler_stats["tasks_scheduled"] += 1
        
        logger.info(f"📋 Scheduled {scanner_name} task {task_id} with priority {task.priority.name}")
        return task_id
    
    def _calculate_wait_time(self, new_task: ScheduledTask) -> float:
        """Calculate estimated wait time for new task"""
        # Simple estimation based on queue length and resource availability
        queue_length = len(self.task_queue)
        running_tasks_count = len(self.running_tasks)
        
        if queue_length == 0 and running_tasks_count == 0:
            return 0.0  # Can start immediately
        
        # Estimate based on average task duration and queue position
        average_duration = sum(task.metrics.average_duration for task in self.task_queue) / max(1, queue_length)
        
        # Factor in resource contention
        resource_factor = 1.0
        if not self.resource_monitor.can_handle_task(new_task.requirements):
            resource_factor = 2.0  # Double wait time if resources are constrained
        
        return (queue_length * average_duration * 0.5) * resource_factor
    
    def get_next_task(self) -> Optional[ScheduledTask]:
        """
        Get next task ready for execution
        O(log n) complexity for heap operations
        """
        while self.task_queue:
            # Peek at highest priority task
            next_task = self.task_queue[0]
            
            # Check if dependencies are satisfied
            if self._dependencies_satisfied(next_task):
                # Check if resources are available
                if self.resource_monitor.can_handle_task(next_task.requirements):
                    # Remove from queue and return
                    return heapq.heappop(self.task_queue)
                else:
                    # Resources not available, try next task
                    break
            else:
                # Dependencies not satisfied, wait
                break
        
        return None
    
    def _dependencies_satisfied(self, task: ScheduledTask) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def mark_task_running(self, task: ScheduledTask):
        """Mark task as currently running"""
        self.running_tasks[task.task_id] = {
            "task": task,
            "start_time": time.time()
        }
        logger.info(f"🏃 Starting {task.scanner_name} task {task.task_id}")
    
    def mark_task_completed(self, task_id: str, success: bool = True, execution_time: Optional[float] = None):
        """Mark task as completed and update metrics"""
        if task_id not in self.running_tasks:
            return
        
        running_info = self.running_tasks.pop(task_id)
        task = running_info["task"]
        
        if execution_time is None:
            execution_time = time.time() - running_info["start_time"]
        
        # Update completed tasks
        self.completed_tasks[task_id] = {
            "task": task,
            "execution_time": execution_time,
            "success": success,
            "completed_at": time.time()
        }
        
        # Update scheduler stats
        if success:
            self.scheduler_stats["tasks_completed"] += 1
        else:
            self.scheduler_stats["tasks_failed"] += 1
        
        # Update average execution time
        total_completed = self.scheduler_stats["tasks_completed"] + self.scheduler_stats["tasks_failed"]
        if total_completed > 0:
            self.scheduler_stats["average_execution_time"] = (
                self.scheduler_stats["average_execution_time"] * (total_completed - 1) + execution_time
            ) / total_completed
        
        # Update scanner profile metrics for learning
        self._update_scanner_metrics(task.scanner_name, execution_time, success)
        
        status_icon = "✅" if success else "❌"
        logger.info(f"{status_icon} Completed {task.scanner_name} task {task_id} in {execution_time:.2f}s")
    
    def _update_scanner_metrics(self, scanner_name: str, execution_time: float, success: bool):
        """Update scanner performance metrics with new data"""
        if scanner_name not in self.scanner_profiles:
            return
        
        metrics = self.scanner_profiles[scanner_name]["metrics"]
        
        # Update average duration with exponential moving average
        alpha = 0.1  # Learning rate
        metrics.average_duration = (1 - alpha) * metrics.average_duration + alpha * execution_time
        
        # Update success rate
        metrics.success_rate = (0.9 * metrics.success_rate + 0.1 * (1.0 if success else 0.0))
        
        metrics.last_updated = time.time()
    
    def get_queue_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            "queued_tasks": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "scheduler_stats": self.scheduler_stats.copy(),
            "system_resources": self.resource_monitor.get_current_resources()
        }
    
    def optimize_queue_order(self):
        """Re-optimize queue order based on current conditions"""
        if not self.task_queue:
            return
        
        # Re-heapify with updated priorities and estimates
        current_time = time.time()
        
        for task in self.task_queue:
            # Update estimated times based on current conditions
            task.estimated_start_time = current_time + self._calculate_wait_time(task)
            task.estimated_completion_time = task.estimated_start_time + task.metrics.average_duration
        
        # Re-heapify the queue
        heapq.heapify(self.task_queue)

class DynamicExecutorManager:
    """
    Manages dynamic scaling of executor pools based on workload and system resources
    Achieves optimal resource utilization with minimal overhead
    """
    
    def __init__(self, resource_monitor: SystemResourceMonitor):
        self.resource_monitor = resource_monitor
        self.executor_pools = {}
        self.pool_stats = {}
        self.last_optimization = 0.0
        self.optimization_interval = 30.0  # Optimize every 30 seconds
        
        # Initialize base executor pools
        self._initialize_executor_pools()
    
    def _initialize_executor_pools(self):
        """Initialize executor pools for different resource types"""
        resources = self.resource_monitor.get_current_resources()
        
        self.executor_pools = {
            ResourceType.CPU_INTENSIVE: ProcessPoolExecutor(
                max_workers=self.resource_monitor.get_optimal_worker_count(ResourceType.CPU_INTENSIVE)
            ),
            ResourceType.IO_INTENSIVE: ThreadPoolExecutor(
                max_workers=self.resource_monitor.get_optimal_worker_count(ResourceType.IO_INTENSIVE)
            ),
            ResourceType.MEMORY_INTENSIVE: ProcessPoolExecutor(
                max_workers=self.resource_monitor.get_optimal_worker_count(ResourceType.MEMORY_INTENSIVE)
            ),
            ResourceType.NETWORK_INTENSIVE: ThreadPoolExecutor(
                max_workers=self.resource_monitor.get_optimal_worker_count(ResourceType.NETWORK_INTENSIVE)
            )
        }
        
        # Initialize stats
        for resource_type in ResourceType:
            self.pool_stats[resource_type] = {
                "tasks_executed": 0,
                "average_execution_time": 0.0,
                "current_workers": self.executor_pools[resource_type]._max_workers,
                "utilization": 0.0
            }
        
        logger.info("🎛️ Initialized dynamic executor pools")
    
    def get_executor(self, resource_type: ResourceType):
        """Get appropriate executor for resource type"""
        self._maybe_optimize_pools()
        return self.executor_pools[resource_type]
    
    def _maybe_optimize_pools(self):
        """Optimize executor pools if needed"""
        current_time = time.time()
        
        if current_time - self.last_optimization > self.optimization_interval:
            self._optimize_executor_pools()
            self.last_optimization = current_time
    
    def _optimize_executor_pools(self):
        """Dynamically optimize executor pool sizes"""
        resources = self.resource_monitor.get_current_resources()
        performance_score = resources.get("performance_score", 0.5)
        
        for resource_type in ResourceType:
            current_workers = self.pool_stats[resource_type]["current_workers"]
            optimal_workers = self.resource_monitor.get_optimal_worker_count(resource_type)
            
            # Only resize if significant difference and system can handle it
            if abs(optimal_workers - current_workers) > 1 and performance_score > 0.4:
                try:
                    # Shutdown current executor
                    old_executor = self.executor_pools[resource_type]
                    
                    # Create new executor with optimal size
                    if resource_type in [ResourceType.CPU_INTENSIVE, ResourceType.MEMORY_INTENSIVE]:
                        new_executor = ProcessPoolExecutor(max_workers=optimal_workers)
                    else:
                        new_executor = ThreadPoolExecutor(max_workers=optimal_workers)
                    
                    self.executor_pools[resource_type] = new_executor
                    self.pool_stats[resource_type]["current_workers"] = optimal_workers
                    
                    # Shutdown old executor (gracefully)
                    old_executor.shutdown(wait=False)
                    
                    logger.info(f"🔄 Resized {resource_type.value} pool: {current_workers} → {optimal_workers} workers")
                    
                except Exception as e:
                    logger.warning(f"Failed to resize {resource_type.value} pool: {e}")
    
    def record_task_execution(self, resource_type: ResourceType, execution_time: float):
        """Record task execution metrics for pool optimization"""
        stats = self.pool_stats[resource_type]
        
        # Update average execution time
        tasks_count = stats["tasks_executed"]
        stats["average_execution_time"] = (
            stats["average_execution_time"] * tasks_count + execution_time
        ) / (tasks_count + 1)
        
        stats["tasks_executed"] += 1
        
        # Calculate utilization (simplified)
        current_workers = stats["current_workers"]
        stats["utilization"] = min(1.0, stats["tasks_executed"] / (current_workers * 10))  # Rough estimate
    
    def get_pool_statistics(self) -> Dict:
        """Get executor pool statistics"""
        return {
            "pools": {
                resource_type.value: {
                    **stats,
                    "executor_type": type(self.executor_pools[resource_type]).__name__
                }
                for resource_type, stats in self.pool_stats.items()
            },
            "system_resources": self.resource_monitor.get_current_resources()
        }
    
    def shutdown(self):
        """Shutdown all executor pools"""
        for executor in self.executor_pools.values():
            executor.shutdown(wait=True)
        logger.info("🛑 Shutdown all executor pools")


# Integration example
class OptimalScanningEngine:
    """
    Complete scanning engine with intelligent scheduling and resource management
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.resource_monitor = SystemResourceMonitor()
        self.scheduler = IntelligentTaskScheduler(self.resource_monitor)
        self.executor_manager = DynamicExecutorManager(self.resource_monitor)
        self.running = False
        
    async def start_engine(self):
        """Start the scanning engine"""
        self.running = True
        
        # Start background tasks
        asyncio.create_task(self._task_execution_loop())
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("🚀 Optimal scanning engine started")
    
    async def stop_engine(self):
        """Stop the scanning engine"""
        self.running = False
        self.executor_manager.shutdown()
        logger.info("🛑 Optimal scanning engine stopped")
    
    def schedule_scan(self, scanner_name: str, path: str) -> str:
        """Schedule a scan with optimal resource allocation"""
        return self.scheduler.schedule_task(scanner_name, path)
    
    async def _task_execution_loop(self):
        """Main task execution loop"""
        while self.running:
            # Get next task
            task = self.scheduler.get_next_task()
            
            if task:
                # Mark as running
                self.scheduler.mark_task_running(task)
                
                # Execute with appropriate executor
                executor = self.executor_manager.get_executor(task.resource_type)
                
                # Submit task for execution
                loop = asyncio.get_event_loop()
                try:
                    start_time = time.time()
                    
                    # Execute scanner (simplified - would integrate with actual scanners)
                    future = executor.submit(self._execute_scanner, task)
                    result = await loop.run_in_executor(None, future.result)
                    
                    execution_time = time.time() - start_time
                    
                    # Record metrics
                    self.executor_manager.record_task_execution(task.resource_type, execution_time)
                    self.scheduler.mark_task_completed(task.task_id, True, execution_time)
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Task {task.task_id} failed: {e}")
                    self.scheduler.mark_task_completed(task.task_id, False, execution_time)
            
            else:
                # No tasks ready, wait a bit
                await asyncio.sleep(0.1)
    
    def _execute_scanner(self, task: ScheduledTask) -> Dict:
        """Execute scanner task (simplified implementation)"""
        # This would integrate with actual scanner implementations
        time.sleep(task.metrics.average_duration * 0.1)  # Simulate work
        return {"scanner": task.scanner_name, "findings": [], "status": "success"}
    
    async def _monitoring_loop(self):
        """Background monitoring and optimization loop"""
        while self.running:
            # Optimize queue order periodically
            self.scheduler.optimize_queue_order()
            
            # Log status
            status = self.scheduler.get_queue_status()
            if status["queued_tasks"] > 0 or status["running_tasks"] > 0:
                logger.info(f"📊 Queue: {status['queued_tasks']} queued, {status['running_tasks']} running")
            
            await asyncio.sleep(10)  # Monitor every 10 seconds
    
    def get_engine_status(self) -> Dict:
        """Get comprehensive engine status"""
        return {
            "scheduler": self.scheduler.get_queue_status(),
            "executors": self.executor_manager.get_pool_statistics(),
            "system": self.resource_monitor.get_current_resources(),
            "running": self.running
        }


# Demo usage
async def demo_optimal_engine():
    """Demonstrate optimal scanning engine"""
    engine = OptimalScanningEngine()
    
    try:
        await engine.start_engine()
        
        # Schedule some scans
        task_ids = []
        scanners = ["secret", "dependency", "sast", "snyk", "trivy"]
        
        for scanner in scanners:
            task_id = engine.schedule_scan(scanner, "/path/to/project")
            task_ids.append(task_id)
            print(f"📋 Scheduled {scanner} scan: {task_id}")
        
        # Let it run for a bit
        await asyncio.sleep(30)
        
        # Check status
        status = engine.get_engine_status()
        print(f"📊 Engine Status: {status}")
        
    finally:
        await engine.stop_engine()

if __name__ == "__main__":
    asyncio.run(demo_optimal_engine())