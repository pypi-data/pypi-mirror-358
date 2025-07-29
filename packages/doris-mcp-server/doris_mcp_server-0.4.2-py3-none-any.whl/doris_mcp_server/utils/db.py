#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Apache Doris Database Connection Management Module

Provides high-performance database connection pool management, automatic reconnection mechanism and connection health check functionality
Supports asynchronous operations and concurrent connection management, ensuring stability and performance for enterprise applications
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import aiomysql
from aiomysql import Connection, Pool




@dataclass
class ConnectionMetrics:
    """Connection pool performance metrics"""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    connection_errors: int = 0
    avg_connection_time: float = 0.0
    last_health_check: datetime | None = None


@dataclass
class QueryResult:
    """Query result wrapper"""

    data: list[dict[str, Any]]
    metadata: dict[str, Any]
    execution_time: float
    row_count: int


class DorisConnection:
    """Doris database connection wrapper class"""

    def __init__(self, connection: Connection, session_id: str, security_manager=None):
        self.connection = connection
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.query_count = 0
        self.is_healthy = True
        self.security_manager = security_manager

    async def execute(self, sql: str, params: tuple | None = None, auth_context=None) -> QueryResult:
        """Execute SQL query"""
        start_time = time.time()

        try:
            # If security manager exists, perform SQL security check
            security_result = None
            if self.security_manager and auth_context:
                validation_result = await self.security_manager.validate_sql_security(sql, auth_context)
                if not validation_result.is_valid:
                    raise ValueError(f"SQL security validation failed: {validation_result.error_message}")
                security_result = {
                    "is_valid": validation_result.is_valid,
                    "risk_level": validation_result.risk_level,
                    "blocked_operations": validation_result.blocked_operations
                }

            async with self.connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, params)

                # Check if it's a query statement (statement that returns result set)
                sql_upper = sql.strip().upper()
                if (sql_upper.startswith("SELECT") or 
                    sql_upper.startswith("SHOW") or 
                    sql_upper.startswith("DESCRIBE") or 
                    sql_upper.startswith("DESC") or 
                    sql_upper.startswith("EXPLAIN")):
                    data = await cursor.fetchall()
                    row_count = len(data)
                else:
                    data = []
                    row_count = cursor.rowcount

                execution_time = time.time() - start_time
                self.last_used = datetime.utcnow()
                self.query_count += 1

                # Get column information
                columns = []
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]

                # If security manager exists and has auth context, apply data masking
                final_data = list(data) if data else []
                if self.security_manager and auth_context and final_data:
                    final_data = await self.security_manager.apply_data_masking(final_data, auth_context)

                metadata = {"columns": columns, "query": sql, "params": params}
                if security_result:
                    metadata["security_check"] = security_result

                return QueryResult(
                    data=final_data,
                    metadata=metadata,
                    execution_time=execution_time,
                    row_count=row_count,
                )

        except Exception as e:
            self.is_healthy = False
            logging.error(f"Query execution failed: {e}")
            raise

    async def ping(self) -> bool:
        """Check connection health status"""
        try:
            # Check if connection exists and is not closed
            if not self.connection or self.connection.closed:
                self.is_healthy = False
                return False
            
            # Check if connection has _reader (aiomysql internal state)
            # This prevents the 'NoneType' object has no attribute 'at_eof' error
            if not hasattr(self.connection, '_reader') or self.connection._reader is None:
                self.is_healthy = False
                return False
            
            # Additional check for reader's state
            if hasattr(self.connection._reader, '_transport') and self.connection._reader._transport is None:
                self.is_healthy = False
                return False
            
            # Try to ping the connection
            await self.connection.ping()
            self.is_healthy = True
            return True
        except (AttributeError, OSError, ConnectionError, Exception) as e:
            # Log the specific error for debugging
            logging.debug(f"Connection ping failed for session {self.session_id}: {e}")
            self.is_healthy = False
            return False

    async def close(self):
        """Close connection"""
        try:
            if self.connection and not self.connection.closed:
                await self.connection.ensure_closed()
        except Exception as e:
            logging.error(f"Error occurred while closing connection: {e}")


class DorisConnectionManager:
    """Doris database connection manager

    Provides connection pool management, connection health monitoring, fault recovery and other functions
    Supports session-level connection reuse and intelligent load balancing
    Integrates security manager to provide unified security validation and data masking
    """

    def __init__(self, config, security_manager=None):
        self.config = config
        self.pool: Pool | None = None
        self.session_connections: dict[str, DorisConnection] = {}
        self.metrics = ConnectionMetrics()
        self.logger = logging.getLogger(__name__)
        self.security_manager = security_manager

        # Health check configuration
        self.health_check_interval = config.database.health_check_interval or 60
        self.max_connection_age = config.database.max_connection_age or 3600
        self.connection_timeout = config.database.connection_timeout or 30

        # Start background tasks
        self._health_check_task = None
        self._cleanup_task = None

    async def initialize(self):
        """Initialize connection manager"""
        try:
            self.logger.info(f"Initializing connection pool to {self.config.database.host}:{self.config.database.port}")
            
            # Validate configuration
            if not self.config.database.host:
                raise ValueError("Database host is required")
            if not self.config.database.user:
                raise ValueError("Database user is required")
            if not self.config.database.password:
                self.logger.warning("Database password is empty, this may cause connection issues")
            
            # Create connection pool with additional parameters for stability
            self.pool = await aiomysql.create_pool(
                host=self.config.database.host,
                port=self.config.database.port,
                user=self.config.database.user,
                password=self.config.database.password,
                db=self.config.database.database,
                charset="utf8",
                minsize=self.config.database.min_connections or 5,
                maxsize=self.config.database.max_connections or 20,
                autocommit=True,
                connect_timeout=self.connection_timeout,
                # Additional parameters for stability
                pool_recycle=3600,  # Recycle connections every hour
                echo=False,  # Don't echo SQL statements
            )

            # Test the connection pool
            if not await self.test_connection():
                raise RuntimeError("Connection pool test failed")

            self.logger.info(
                f"Connection pool initialized successfully, min connections: {self.config.database.min_connections}, "
                f"max connections: {self.config.database.max_connections}"
            )

            # Start background monitoring tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        except Exception as e:
            self.logger.error(f"Connection pool initialization failed: {e}")
            # Clean up partial initialization
            if self.pool:
                try:
                    self.pool.close()
                    await self.pool.wait_closed()
                except Exception:
                    pass
                self.pool = None
            raise

    async def get_connection(self, session_id: str) -> DorisConnection:
        """Get database connection

        Supports session-level connection reuse to improve performance and consistency
        """
        # Check if there's an existing session connection
        if session_id in self.session_connections:
            conn = self.session_connections[session_id]
            # Check connection health
            if await conn.ping():
                return conn
            else:
                # Connection is unhealthy, clean up and create new one
                await self._cleanup_session_connection(session_id)

        # Create new connection
        return await self._create_new_connection(session_id)

    async def _create_new_connection(self, session_id: str) -> DorisConnection:
        """Create new database connection"""
        try:
            if not self.pool:
                raise RuntimeError("Connection pool not initialized")

            # Get connection from pool
            raw_connection = await self.pool.acquire()
            
            # Validate the raw connection
            if not raw_connection:
                raise RuntimeError(f"Failed to acquire connection from pool for session {session_id}")
            
            # Verify the connection is not closed
            if raw_connection.closed:
                raise RuntimeError(f"Acquired connection is already closed for session {session_id}")
            
            # Create wrapped connection
            doris_conn = DorisConnection(raw_connection, session_id, self.security_manager)
            
            # Test the connection before storing it
            if not await doris_conn.ping():
                # If ping fails, release the connection and raise error
                if self.pool and raw_connection and not raw_connection.closed:
                    self.pool.release(raw_connection)
                raise RuntimeError(f"New connection failed ping test for session {session_id}")
            
            # Store in session connections
            self.session_connections[session_id] = doris_conn
            
            self.metrics.total_connections += 1
            self.logger.debug(f"Created new connection for session: {session_id}")
            
            return doris_conn

        except Exception as e:
            self.metrics.connection_errors += 1
            self.logger.error(f"Failed to create connection for session {session_id}: {e}")
            raise

    async def release_connection(self, session_id: str):
        """Release session connection"""
        if session_id in self.session_connections:
            await self._cleanup_session_connection(session_id)

    async def _cleanup_session_connection(self, session_id: str):
        """Clean up session connection"""
        if session_id in self.session_connections:
            conn = self.session_connections[session_id]
            try:
                # Return connection to pool only if it's valid and not closed
                if (self.pool and 
                    conn.connection and 
                    not conn.connection.closed and
                    hasattr(conn.connection, '_reader') and 
                    conn.connection._reader is not None):
                    try:
                        # Try to gracefully return to pool
                        self.pool.release(conn.connection)
                    except Exception as pool_error:
                        self.logger.debug(f"Failed to return connection to pool for session {session_id}: {pool_error}")
                        # If pool release fails, try to close the connection directly
                        try:
                            await conn.connection.ensure_closed()
                        except Exception:
                            pass  # Ignore errors during forced close
                
                # Close connection wrapper
                await conn.close()
                
            except Exception as e:
                self.logger.error(f"Error cleaning up connection for session {session_id}: {e}")
                # Force close if normal cleanup fails
                try:
                    if conn.connection and not conn.connection.closed:
                        await conn.connection.ensure_closed()
                except Exception:
                    pass  # Ignore errors during forced close
            finally:
                # Remove from session connections
                del self.session_connections[session_id]
                self.logger.debug(f"Cleaned up connection for session: {session_id}")

    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")

    async def _perform_health_check(self):
        """Perform health check"""
        try:
            unhealthy_sessions = []
            
            # First pass: check basic connectivity
            for session_id, conn in self.session_connections.items():
                if not await conn.ping():
                    unhealthy_sessions.append(session_id)
            
            # Second pass: check for stale connections (over 30 minutes old)
            current_time = datetime.utcnow()
            stale_sessions = []
            for session_id, conn in self.session_connections.items():
                if session_id not in unhealthy_sessions:  # Don't double-check
                    last_used_delta = (current_time - conn.last_used).total_seconds()
                    if last_used_delta > 1800:  # 30 minutes
                        # Force a ping check for stale connections
                        if not await conn.ping():
                            stale_sessions.append(session_id)
            
            all_problematic_sessions = list(set(unhealthy_sessions + stale_sessions))
            
            # Clean up problematic connections
            for session_id in all_problematic_sessions:
                await self._cleanup_session_connection(session_id)
                self.metrics.failed_connections += 1
            
            # Update metrics
            await self._update_connection_metrics()
            self.metrics.last_health_check = datetime.utcnow()
            
            if all_problematic_sessions:
                self.logger.warning(f"Health check: cleaned up {len(unhealthy_sessions)} unhealthy and {len(stale_sessions)} stale connections")
            else:
                self.logger.debug(f"Health check: all {len(self.session_connections)} connections healthy")

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            # If health check fails, try to diagnose the issue
            try:
                diagnosis = await self.diagnose_connection_health()
                self.logger.error(f"Connection diagnosis: {diagnosis}")
            except Exception:
                pass  # Don't let diagnosis failure crash health check

    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._cleanup_idle_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")

    async def _cleanup_idle_connections(self):
        """Clean up idle connections"""
        current_time = datetime.utcnow()
        idle_sessions = []
        
        for session_id, conn in self.session_connections.items():
            # Check if connection has exceeded maximum age
            age = (current_time - conn.created_at).total_seconds()
            if age > self.max_connection_age:
                idle_sessions.append(session_id)
        
        # Clean up idle connections
        for session_id in idle_sessions:
            await self._cleanup_session_connection(session_id)
        
        if idle_sessions:
            self.logger.info(f"Cleaned up {len(idle_sessions)} idle connections")

    async def _update_connection_metrics(self):
        """Update connection metrics"""
        self.metrics.active_connections = len(self.session_connections)
        if self.pool:
            self.metrics.idle_connections = self.pool.freesize

    async def get_metrics(self) -> ConnectionMetrics:
        """Get connection metrics"""
        await self._update_connection_metrics()
        return self.metrics

    async def execute_query(
        self, session_id: str, sql: str, params: tuple | None = None, auth_context=None
    ) -> QueryResult:
        """Execute query"""
        conn = await self.get_connection(session_id)
        return await conn.execute(sql, params, auth_context)

    @asynccontextmanager
    async def get_connection_context(self, session_id: str):
        """Get connection context manager"""
        conn = await self.get_connection(session_id)
        try:
            yield conn
        finally:
            # Connection will be reused, no need to close here
            pass

    async def close(self):
        """Close connection manager"""
        try:
            # Cancel background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass

            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # Clean up all session connections
            for session_id in list(self.session_connections.keys()):
                await self._cleanup_session_connection(session_id)

            # Close connection pool
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()

            self.logger.info("Connection manager closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing connection manager: {e}")

    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if not self.pool:
                return False

            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    result = await cursor.fetchone()
                    return result is not None

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def diagnose_connection_health(self) -> Dict[str, Any]:
        """Diagnose connection pool and session health"""
        diagnosis = {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_status": "unknown",
            "session_connections": {},
            "problematic_connections": [],
            "recommendations": []
        }
        
        try:
            # Check pool status
            if not self.pool:
                diagnosis["pool_status"] = "not_initialized"
                diagnosis["recommendations"].append("Initialize connection pool")
                return diagnosis
            
            if self.pool.closed:
                diagnosis["pool_status"] = "closed"
                diagnosis["recommendations"].append("Recreate connection pool")
                return diagnosis
            
            diagnosis["pool_status"] = "healthy"
            diagnosis["pool_info"] = {
                "size": self.pool.size,
                "free_size": self.pool.freesize,
                "min_size": self.pool.minsize,
                "max_size": self.pool.maxsize
            }
            
            # Check session connections
            problematic_sessions = []
            for session_id, conn in self.session_connections.items():
                conn_status = {
                    "session_id": session_id,
                    "created_at": conn.created_at.isoformat(),
                    "last_used": conn.last_used.isoformat(),
                    "query_count": conn.query_count,
                    "is_healthy": conn.is_healthy
                }
                
                # Detailed connection checks
                if conn.connection:
                    conn_status["connection_closed"] = conn.connection.closed
                    conn_status["has_reader"] = hasattr(conn.connection, '_reader') and conn.connection._reader is not None
                    
                    if hasattr(conn.connection, '_reader') and conn.connection._reader:
                        conn_status["reader_transport"] = conn.connection._reader._transport is not None
                    else:
                        conn_status["reader_transport"] = False
                else:
                    conn_status["connection_closed"] = True
                    conn_status["has_reader"] = False
                    conn_status["reader_transport"] = False
                
                # Check if connection is problematic
                if (not conn.is_healthy or 
                    conn_status["connection_closed"] or 
                    not conn_status["has_reader"] or 
                    not conn_status["reader_transport"]):
                    problematic_sessions.append(session_id)
                    diagnosis["problematic_connections"].append(conn_status)
                
                diagnosis["session_connections"][session_id] = conn_status
            
            # Generate recommendations
            if problematic_sessions:
                diagnosis["recommendations"].append(f"Clean up {len(problematic_sessions)} problematic connections")
            
            if self.pool.freesize == 0 and self.pool.size >= self.pool.maxsize:
                diagnosis["recommendations"].append("Connection pool exhausted - consider increasing max_connections")
            
            # Auto-cleanup problematic connections
            for session_id in problematic_sessions:
                try:
                    await self._cleanup_session_connection(session_id)
                    self.logger.info(f"Auto-cleaned problematic connection for session: {session_id}")
                except Exception as e:
                    self.logger.error(f"Failed to auto-clean session {session_id}: {e}")
            
            return diagnosis
            
        except Exception as e:
            diagnosis["error"] = str(e)
            diagnosis["recommendations"].append("Manual intervention required")
            return diagnosis


class ConnectionPoolMonitor:
    """Connection pool monitor

    Provides detailed monitoring and reporting capabilities for connection pool status
    """

    def __init__(self, connection_manager: DorisConnectionManager):
        self.connection_manager = connection_manager
        self.logger = logging.getLogger(__name__)

    async def get_pool_status(self) -> dict[str, Any]:
        """Get connection pool status"""
        metrics = await self.connection_manager.get_metrics()
        
        status = {
            "pool_size": self.connection_manager.pool.size if self.connection_manager.pool else 0,
            "free_connections": self.connection_manager.pool.freesize if self.connection_manager.pool else 0,
            "active_sessions": len(self.connection_manager.session_connections),
            "total_connections": metrics.total_connections,
            "failed_connections": metrics.failed_connections,
            "connection_errors": metrics.connection_errors,
            "avg_connection_time": metrics.avg_connection_time,
            "last_health_check": metrics.last_health_check.isoformat() if metrics.last_health_check else None,
        }
        
        return status

    async def get_session_details(self) -> list[dict[str, Any]]:
        """Get session connection details"""
        sessions = []
        
        for session_id, conn in self.connection_manager.session_connections.items():
            session_info = {
                "session_id": session_id,
                "created_at": conn.created_at.isoformat(),
                "last_used": conn.last_used.isoformat(),
                "query_count": conn.query_count,
                "is_healthy": conn.is_healthy,
                "connection_age": (datetime.utcnow() - conn.created_at).total_seconds(),
            }
            sessions.append(session_info)
        
        return sessions

    async def generate_health_report(self) -> dict[str, Any]:
        """Generate connection health report"""
        pool_status = await self.get_pool_status()
        session_details = await self.get_session_details()
        
        # Calculate health statistics
        healthy_sessions = sum(1 for s in session_details if s["is_healthy"])
        total_sessions = len(session_details)
        health_ratio = healthy_sessions / total_sessions if total_sessions > 0 else 1.0
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_status": pool_status,
            "session_summary": {
                "total_sessions": total_sessions,
                "healthy_sessions": healthy_sessions,
                "health_ratio": health_ratio,
            },
            "session_details": session_details,
            "recommendations": [],
        }
        
        # Add recommendations based on health status
        if health_ratio < 0.8:
            report["recommendations"].append("Consider checking database connectivity and network stability")
        
        if pool_status["connection_errors"] > 10:
            report["recommendations"].append("High connection error rate detected, review connection configuration")
        
        if pool_status["active_sessions"] > pool_status["pool_size"] * 0.9:
            report["recommendations"].append("Connection pool utilization is high, consider increasing pool size")
        
        return report
