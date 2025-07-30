"""
Supabase Storage Implementation for Model Registry

Uses Supabase as the backend database for model metadata and capabilities
Supports the full model lifecycle with cloud-based storage
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from ..model_storage import ModelStorage

logger = logging.getLogger(__name__)

class SupabaseModelRegistry:
    """
    Supabase-based model registry for metadata and capabilities
    
    Replaces SQLite with cloud-based Supabase database
    """
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py is required. Install with: pip install supabase")
        
        # Load environment variables
        load_dotenv()
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        
        # Initialize Supabase client
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize tables if needed
        self._ensure_tables()
        
        logger.info("Supabase model registry initialized")
    
    def _ensure_tables(self):
        """Ensure required tables exist in Supabase"""
        # Note: In production, these tables should be created via Supabase migrations
        # This is just for development/initialization
        try:
            # Check if models table exists by trying to query it
            result = self.supabase.table('models').select('model_id').limit(1).execute()
        except Exception as e:
            logger.warning(f"Models table might not exist: {e}")
            # In production, you would run proper migrations here
    
    def register_model(self, 
                      model_id: str,
                      model_type: str,
                      capabilities: List[str],
                      metadata: Dict[str, Any]) -> bool:
        """Register a model with its capabilities and metadata"""
        try:
            current_time = datetime.now().isoformat()
            
            # Prepare model data
            model_data = {
                'model_id': model_id,
                'model_type': model_type,
                'metadata': json.dumps(metadata),
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # Insert or update model
            result = self.supabase.table('models').upsert(model_data).execute()
            
            if not result.data:
                logger.error(f"Failed to insert model {model_id}")
                return False
            
            # Delete existing capabilities
            self.supabase.table('model_capabilities').delete().eq('model_id', model_id).execute()
            
            # Insert new capabilities
            if capabilities:
                capability_data = [
                    {
                        'model_id': model_id,
                        'capability': capability,
                        'created_at': current_time
                    }
                    for capability in capabilities
                ]
                
                cap_result = self.supabase.table('model_capabilities').insert(capability_data).execute()
                
                if not cap_result.data:
                    logger.error(f"Failed to insert capabilities for {model_id}")
                    return False
            
            logger.info(f"Successfully registered model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
            return False
    
    def unregister_model(self, model_id: str) -> bool:
        """Unregister a model"""
        try:
            # Delete model (capabilities will be cascade deleted)
            result = self.supabase.table('models').delete().eq('model_id', model_id).execute()
            
            if result.data:
                logger.info(f"Unregistered model {model_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister model {model_id}: {e}")
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        try:
            # Get model info
            model_result = self.supabase.table('models').select('*').eq('model_id', model_id).execute()
            
            if not model_result.data:
                return None
            
            model_row = model_result.data[0]
            
            # Get capabilities
            cap_result = self.supabase.table('model_capabilities').select('capability').eq('model_id', model_id).execute()
            capabilities = [cap['capability'] for cap in cap_result.data]
            
            model_info = {
                "model_id": model_row["model_id"],
                "type": model_row["model_type"],
                "capabilities": capabilities,
                "metadata": json.loads(model_row["metadata"]) if model_row["metadata"] else {},
                "created_at": model_row["created_at"],
                "updated_at": model_row["updated_at"]
            }
            
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to get model info for {model_id}: {e}")
            return None
    
    def get_models_by_type(self, model_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all models of a specific type"""
        try:
            models_result = self.supabase.table('models').select('*').eq('model_type', model_type).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get capabilities for this model
                cap_result = self.supabase.table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in cap_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get models by type {model_type}: {e}")
            return {}
    
    def get_models_by_capability(self, capability: str) -> Dict[str, Dict[str, Any]]:
        """Get all models with a specific capability"""
        try:
            # Join query to get models with specific capability
            query = """
            SELECT DISTINCT m.*, mc.capability
            FROM models m
            INNER JOIN model_capabilities mc ON m.model_id = mc.model_id
            WHERE mc.capability = %s
            """
            
            # Use RPC for complex queries
            result = self.supabase.rpc('get_models_by_capability', {'capability_name': capability}).execute()
            
            if result.data:
                models_dict = {}
                for row in result.data:
                    model_id = row['model_id']
                    if model_id not in models_dict:
                        # Get all capabilities for this model
                        cap_result = self.supabase.table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                        capabilities = [cap['capability'] for cap in cap_result.data]
                        
                        models_dict[model_id] = {
                            "type": row["model_type"],
                            "capabilities": capabilities,
                            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"]
                        }
                
                return models_dict
            
            # Fallback: manual join if RPC not available
            cap_result = self.supabase.table('model_capabilities').select('model_id').eq('capability', capability).execute()
            model_ids = [row['model_id'] for row in cap_result.data]
            
            if not model_ids:
                return {}
            
            models_result = self.supabase.table('models').select('*').in_('model_id', model_ids).execute()
            
            result_dict = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get all capabilities for this model
                all_caps_result = self.supabase.table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in all_caps_result.data]
                
                result_dict[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result_dict
            
        except Exception as e:
            logger.error(f"Failed to get models by capability {capability}: {e}")
            return {}
    
    def has_capability(self, model_id: str, capability: str) -> bool:
        """Check if a model has a specific capability"""
        try:
            result = self.supabase.table('model_capabilities').select('model_id').eq('model_id', model_id).eq('capability', capability).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check capability for {model_id}: {e}")
            return False
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all registered models"""
        try:
            models_result = self.supabase.table('models').select('*').order('created_at', desc=True).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get capabilities for this model
                cap_result = self.supabase.table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in cap_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
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
            # Count total models
            total_result = self.supabase.table('models').select('model_id', count='exact').execute()
            total_models = total_result.count if total_result.count is not None else 0
            
            # Count by type
            type_result = self.supabase.rpc('get_model_type_counts').execute()
            type_counts = {row['model_type']: row['count'] for row in type_result.data} if type_result.data else {}
            
            # Count by capability
            cap_result = self.supabase.rpc('get_capability_counts').execute()
            capability_counts = {row['capability']: row['count'] for row in cap_result.data} if cap_result.data else {}
            
            return {
                "total_models": total_models,
                "models_by_type": type_counts,
                "models_by_capability": capability_counts
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total_models": 0, "models_by_type": {}, "models_by_capability": {}}
    
    def search_models(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search models by name or metadata"""
        try:
            # Search in model_id and metadata
            models_result = self.supabase.table('models').select('*').or_(
                f'model_id.ilike.%{query}%,metadata.ilike.%{query}%'
            ).order('created_at', desc=True).execute()
            
            result = {}
            for model in models_result.data:
                model_id = model["model_id"]
                
                # Get capabilities for this model
                cap_result = self.supabase.table('model_capabilities').select('capability').eq('model_id', model_id).execute()
                capabilities = [cap['capability'] for cap in cap_result.data]
                
                result[model_id] = {
                    "type": model["model_type"],
                    "capabilities": capabilities,
                    "metadata": json.loads(model["metadata"]) if model["metadata"] else {},
                    "created_at": model["created_at"],
                    "updated_at": model["updated_at"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to search models with query '{query}': {e}")
            return {}