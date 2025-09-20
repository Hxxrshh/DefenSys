"""
Real-Time Monitoring System with RabbitMQ
==========================================

This module provides real-time status updates for DefenSys security scans
using RabbitMQ message broker and WebSockets for live frontend updates.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

import pika
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScanStatus(Enum):
    """Scan status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MessageType(Enum):
    """Message type enumeration"""
    SCAN_STARTED = "scan_started"
    SCAN_PROGRESS = "scan_progress"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    VULNERABILITY_FOUND = "vulnerability_found"
    SYSTEM_STATUS = "system_status"

@dataclass
class ScanMessage:
    """Real-time scan message"""
    message_type: MessageType
    scan_id: int
    project_id: int
    status: ScanStatus
    progress: float  # 0.0 to 1.0
    current_scanner: Optional[str] = None
    vulnerabilities_found: int = 0
    estimated_time_remaining: Optional[int] = None  # seconds
    message: Optional[str] = None
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

class RabbitMQManager:
    """
    RabbitMQ connection and message management
    """
    
    def __init__(self, rabbitmq_url: str = None):
        self.rabbitmq_url = rabbitmq_url or os.getenv(
            'RABBITMQ_URL', 
            'amqp://defensys_user:defensys_password@localhost:5672'
        )
        self.connection = None
        self.channel = None
        self.exchange_name = 'defensys_monitoring'
        self.queue_name = 'scan_updates'
        
    def connect(self):
        """Establish RabbitMQ connection"""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            
            # Declare exchange and queue
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key='scan.*'
            )
            
            logger.info("✅ Connected to RabbitMQ")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            return False
    
    def publish_message(self, message: ScanMessage, routing_key: str = "scan.update"):
        """Publish scan update message"""
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            message_body = json.dumps(asdict(message), default=str)
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    timestamp=int(datetime.utcnow().timestamp())
                )
            )
            
            logger.debug(f"📤 Published message: {message.message_type.value} for scan {message.scan_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish message: {e}")
            return False
    
    def consume_messages(self, callback):
        """Consume messages from queue"""
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=callback,
                auto_ack=True
            )
            
            logger.info("🔄 Starting message consumption...")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"❌ Failed to consume messages: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            logger.info("🔌 Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"❌ Error closing RabbitMQ connection: {e}")

class WebSocketManager:
    """
    WebSocket connection manager for real-time frontend updates
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.rabbitmq = RabbitMQManager()
        self.running = False
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"🔌 New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"❌ Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: ScanMessage):
        """Broadcast message to all connected WebSockets"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(asdict(message), default=str)
        
        # Send to all connections, remove failed ones
        failed_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"❌ Failed to send broadcast message: {e}")
                failed_connections.append(connection)
        
        # Remove failed connections
        for connection in failed_connections:
            self.disconnect(connection)
        
        if self.active_connections:
            logger.debug(f"📤 Broadcasted to {len(self.active_connections)} connections")
    
    async def start_rabbitmq_consumer(self):
        """Start consuming RabbitMQ messages in background"""
        self.running = True
        
        def message_callback(ch, method, properties, body):
            """Callback for RabbitMQ messages"""
            try:
                message_data = json.loads(body)
                message = ScanMessage(**message_data)
                
                # Schedule broadcast to WebSocket clients
                asyncio.create_task(self.broadcast(message))
                
            except Exception as e:
                logger.error(f"❌ Error processing RabbitMQ message: {e}")
        
        # Run RabbitMQ consumer in thread
        import threading
        
        def consume_in_thread():
            if self.rabbitmq.connect():
                self.rabbitmq.consume_messages(message_callback)
        
        consumer_thread = threading.Thread(target=consume_in_thread)
        consumer_thread.daemon = True
        consumer_thread.start()
        
        logger.info("🚀 Started RabbitMQ consumer for WebSocket broadcasting")

class RealTimeMonitor:
    """
    Main real-time monitoring class
    """
    
    def __init__(self):
        self.rabbitmq = RabbitMQManager()
        self.websocket_manager = WebSocketManager()
    
    def publish_scan_started(self, scan_id: int, project_id: int, scanners: List[str]):
        """Publish scan started event"""
        message = ScanMessage(
            message_type=MessageType.SCAN_STARTED,
            scan_id=scan_id,
            project_id=project_id,
            status=ScanStatus.RUNNING,
            progress=0.0,
            message=f"Started security scan with {len(scanners)} scanners",
            details={"scanners": scanners}
        )
        self.rabbitmq.publish_message(message, "scan.started")
    
    def publish_scan_progress(self, scan_id: int, project_id: int, progress: float, 
                            current_scanner: str, vulnerabilities_found: int = 0,
                            estimated_time_remaining: int = None):
        """Publish scan progress update"""
        message = ScanMessage(
            message_type=MessageType.SCAN_PROGRESS,
            scan_id=scan_id,
            project_id=project_id,
            status=ScanStatus.RUNNING,
            progress=progress,
            current_scanner=current_scanner,
            vulnerabilities_found=vulnerabilities_found,
            estimated_time_remaining=estimated_time_remaining,
            message=f"Scanning with {current_scanner}... {progress*100:.1f}% complete"
        )
        self.rabbitmq.publish_message(message, "scan.progress")
    
    def publish_vulnerability_found(self, scan_id: int, project_id: int, 
                                  vulnerability: Dict[str, Any]):
        """Publish vulnerability found event"""
        message = ScanMessage(
            message_type=MessageType.VULNERABILITY_FOUND,
            scan_id=scan_id,
            project_id=project_id,
            status=ScanStatus.RUNNING,
            progress=0.0,  # Will be updated by progress messages
            message=f"Found {vulnerability.get('severity', 'unknown')} vulnerability",
            details=vulnerability
        )
        self.rabbitmq.publish_message(message, "scan.vulnerability")
    
    def publish_scan_completed(self, scan_id: int, project_id: int, 
                             total_vulnerabilities: int, execution_time: float):
        """Publish scan completed event"""
        message = ScanMessage(
            message_type=MessageType.SCAN_COMPLETED,
            scan_id=scan_id,
            project_id=project_id,
            status=ScanStatus.COMPLETED,
            progress=1.0,
            vulnerabilities_found=total_vulnerabilities,
            message=f"Scan completed! Found {total_vulnerabilities} issues in {execution_time:.1f}s",
            details={"execution_time": execution_time}
        )
        self.rabbitmq.publish_message(message, "scan.completed")
    
    def publish_scan_failed(self, scan_id: int, project_id: int, error_message: str):
        """Publish scan failed event"""
        message = ScanMessage(
            message_type=MessageType.SCAN_FAILED,
            scan_id=scan_id,
            project_id=project_id,
            status=ScanStatus.FAILED,
            progress=0.0,
            message=f"Scan failed: {error_message}",
            details={"error": error_message}
        )
        self.rabbitmq.publish_message(message, "scan.failed")
    
    def publish_system_status(self, status: Dict[str, Any]):
        """Publish system status update"""
        message = ScanMessage(
            message_type=MessageType.SYSTEM_STATUS,
            scan_id=0,  # System-wide message
            project_id=0,
            status=ScanStatus.RUNNING,
            progress=0.0,
            message="System status update",
            details=status
        )
        self.rabbitmq.publish_message(message, "system.status")

# Global instance
real_time_monitor = RealTimeMonitor()
websocket_manager = WebSocketManager()

# FastAPI WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            
            # Handle client requests (e.g., subscribe to specific scans)
            try:
                request = json.loads(data)
                if request.get("type") == "subscribe":
                    scan_id = request.get("scan_id")
                    await websocket_manager.send_personal_message(
                        json.dumps({"type": "subscribed", "scan_id": scan_id}),
                        websocket
                    )
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Initialize function
async def initialize_real_time_monitoring():
    """Initialize real-time monitoring system"""
    logger.info("🚀 Initializing real-time monitoring system...")
    
    # Connect to RabbitMQ
    if real_time_monitor.rabbitmq.connect():
        logger.info("✅ RabbitMQ connected successfully")
    else:
        logger.error("❌ Failed to connect to RabbitMQ")
        return False
    
    # Start WebSocket consumer
    await websocket_manager.start_rabbitmq_consumer()
    
    logger.info("✅ Real-time monitoring system initialized")
    return True

if __name__ == "__main__":
    # Test the real-time monitoring system
    async def test_monitoring():
        await initialize_real_time_monitoring()
        
        # Simulate scan events
        real_time_monitor.publish_scan_started(1, 1, ["bandit", "semgrep", "trivy"])
        
        await asyncio.sleep(1)
        real_time_monitor.publish_scan_progress(1, 1, 0.3, "bandit", 5, 120)
        
        await asyncio.sleep(1)
        real_time_monitor.publish_vulnerability_found(1, 1, {
            "type": "SQL Injection",
            "severity": "HIGH",
            "file": "app.py",
            "line": 42
        })
        
        await asyncio.sleep(1)
        real_time_monitor.publish_scan_completed(1, 1, 15, 180.5)
    
    asyncio.run(test_monitoring())