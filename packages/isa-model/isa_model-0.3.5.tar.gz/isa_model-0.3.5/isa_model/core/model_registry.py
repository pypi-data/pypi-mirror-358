from typing import Dict, List, Optional, Any
from enum import Enum
import logging
from pathlib import Path
import json
import sqlite3
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class ModelCapability(str, Enum):
    """Model capabilities"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANKING = "reranking"
    REASONING = "reasoning"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    IMAGE_UNDERSTANDING = "image_understanding"
    UI_DETECTION = "ui_detection"
    OCR = "ocr"
    TABLE_DETECTION = "table_detection"
    TABLE_STRUCTURE_RECOGNITION = "table_structure_recognition"

class ModelType(str, Enum):
    """Model types"""
    LLM = "llm"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    VISION = "vision"

class ModelRegistry:
    """Model registry with SQLite or Supabase backend"""
    
    def __init__(self, db_path: str = "./models/model_registry.db", use_supabase: bool = None):
        # Auto-detect Supabase if environment variables are set
        if use_supabase is None:
            import os
            use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))
        
        self.use_supabase = use_supabase
        
        if self.use_supabase:
            try:
                from .storage.supabase_storage import SupabaseModelRegistry
                self.backend = SupabaseModelRegistry()
                logger.info("Using Supabase backend for model registry")
            except ImportError as e:
                logger.warning(f"Supabase not available, falling back to SQLite: {e}")
                self.use_supabase = False
        
        if not self.use_supabase:
            # Use SQLite backend
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._lock = threading.Lock()
            self._initialize_database()
            self.backend = None
            logger.info("Using SQLite backend for model registry")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    model_id TEXT PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS model_capabilities (
                    model_id TEXT,
                    capability TEXT,
                    PRIMARY KEY (model_id, capability),
                    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_model_type ON models(model_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capability ON model_capabilities(capability)
            """)
            
            conn.commit()
    
    def register_model(self, 
                      model_id: str,
                      model_type: ModelType,
                      capabilities: List[ModelCapability],
                      metadata: Dict[str, Any]) -> bool:
        """Register a model with its capabilities and metadata"""
        if self.use_supabase:
            return self.backend.register_model(
                model_id=model_id,
                model_type=model_type.value,
                capabilities=[cap.value for cap in capabilities],
                metadata=metadata
            )
        
        # SQLite implementation
        try:
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    # Insert or update model
                    conn.execute("""
                        INSERT OR REPLACE INTO models 
                        (model_id, model_type, metadata, updated_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (model_id, model_type.value, json.dumps(metadata)))
                    
                    # Clear existing capabilities
                    conn.execute("DELETE FROM model_capabilities WHERE model_id = ?", (model_id,))
                    
                    # Insert new capabilities
                    for capability in capabilities:
                        conn.execute("""
                            INSERT INTO model_capabilities (model_id, capability)
                            VALUES (?, ?)
                        """, (model_id, capability.value))
                    
                    conn.commit()
                    
            logger.info(f"Registered model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
            return False
    
    def unregister_model(self, model_id: str) -> bool:
        """Unregister a model"""
        try:
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("DELETE FROM models WHERE model_id = ?", (model_id,))
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Unregistered model {model_id}")
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to unregister model {model_id}: {e}")
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get model info
                model_row = conn.execute("""
                    SELECT model_id, model_type, metadata, created_at, updated_at
                    FROM models WHERE model_id = ?
                """, (model_id,)).fetchone()
                
                if not model_row:
                    return None
                
                # Get capabilities
                capabilities = conn.execute("""
                    SELECT capability FROM model_capabilities WHERE model_id = ?
                """, (model_id,)).fetchall()
                
                model_info = {
                    "model_id": model_row["model_id"],
                    "type": model_row["model_type"],
                    "capabilities": [cap["capability"] for cap in capabilities],
                    "metadata": json.loads(model_row["metadata"]) if model_row["metadata"] else {},
                    "created_at": model_row["created_at"],
                    "updated_at": model_row["updated_at"]
                }
                
                return model_info
                
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {e}")
            return None
    
    def get_models_by_type(self, model_type: ModelType) -> Dict[str, Dict[str, Any]]:
        """Get all models of a specific type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                models = conn.execute("""
                    SELECT model_id, model_type, metadata, created_at, updated_at
                    FROM models WHERE model_type = ?
                """, (model_type.value,)).fetchall()
                
                result = {}
                for model in models:
                    model_id = model["model_id"]
                    
                    # Get capabilities for this model
                    capabilities = conn.execute("""
                        SELECT capability FROM model_capabilities WHERE model_id = ?
                    """, (model_id,)).fetchall()
                    
                    result[model_id] = {
                        "type": model["model_type"],
                        "capabilities": [cap["capability"] for cap in capabilities],
                        "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                        "created_at": model["created_at"],
                        "updated_at": model["updated_at"]
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get models by type {model_type}: {e}")
            return {}
    
    def get_models_by_capability(self, capability: ModelCapability) -> Dict[str, Dict[str, Any]]:
        """Get all models with a specific capability"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                models = conn.execute("""
                    SELECT DISTINCT m.model_id, m.model_type, m.metadata, m.created_at, m.updated_at
                    FROM models m
                    JOIN model_capabilities mc ON m.model_id = mc.model_id
                    WHERE mc.capability = ?
                """, (capability.value,)).fetchall()
                
                result = {}
                for model in models:
                    model_id = model["model_id"]
                    
                    # Get all capabilities for this model
                    capabilities = conn.execute("""
                        SELECT capability FROM model_capabilities WHERE model_id = ?
                    """, (model_id,)).fetchall()
                    
                    result[model_id] = {
                        "type": model["model_type"],
                        "capabilities": [cap["capability"] for cap in capabilities],
                        "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                        "created_at": model["created_at"],
                        "updated_at": model["updated_at"]
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get models by capability {capability}: {e}")
            return {}
    
    def has_capability(self, model_id: str, capability: ModelCapability) -> bool:
        """Check if a model has a specific capability"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("""
                    SELECT 1 FROM model_capabilities 
                    WHERE model_id = ? AND capability = ?
                """, (model_id, capability.value)).fetchone()
                
                return result is not None
                
        except Exception as e:
            logger.error(f"Failed to check capability for {model_id}: {e}")
            return False
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all registered models"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                models = conn.execute("""
                    SELECT model_id, model_type, metadata, created_at, updated_at
                    FROM models ORDER BY created_at DESC
                """).fetchall()
                
                result = {}
                for model in models:
                    model_id = model["model_id"]
                    
                    # Get capabilities for this model
                    capabilities = conn.execute("""
                        SELECT capability FROM model_capabilities WHERE model_id = ?
                    """, (model_id,)).fetchall()
                    
                    result[model_id] = {
                        "type": model["model_type"],
                        "capabilities": [cap["capability"] for cap in capabilities],
                        "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                        "created_at": model["created_at"],
                        "updated_at": model["updated_at"]
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Count total models
                total_models = conn.execute("SELECT COUNT(*) FROM models").fetchone()[0]
                
                # Count by type
                type_counts = dict(conn.execute("""
                    SELECT model_type, COUNT(*) FROM models GROUP BY model_type
                """).fetchall())
                
                # Count by capability
                capability_counts = dict(conn.execute("""
                    SELECT capability, COUNT(*) FROM model_capabilities GROUP BY capability
                """).fetchall())
                
                return {
                    "total_models": total_models,
                    "models_by_type": type_counts,
                    "models_by_capability": capability_counts
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def search_models(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search models by name or metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                models = conn.execute("""
                    SELECT model_id, model_type, metadata, created_at, updated_at
                    FROM models 
                    WHERE model_id LIKE ? OR metadata LIKE ?
                    ORDER BY created_at DESC
                """, (f"%{query}%", f"%{query}%")).fetchall()
                
                result = {}
                for model in models:
                    model_id = model["model_id"]
                    
                    # Get capabilities for this model
                    capabilities = conn.execute("""
                        SELECT capability FROM model_capabilities WHERE model_id = ?
                    """, (model_id,)).fetchall()
                    
                    result[model_id] = {
                        "type": model["model_type"],
                        "capabilities": [cap["capability"] for cap in capabilities],
                        "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                        "created_at": model["created_at"],
                        "updated_at": model["updated_at"]
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to search models with query '{query}': {e}")
            return {} 