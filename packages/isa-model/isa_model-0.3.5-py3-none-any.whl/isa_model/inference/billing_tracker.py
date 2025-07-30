#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Billing Tracker for isA_Model Services
Tracks usage and costs across all AI providers
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path
from enum import Enum
import os

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types of AI services"""
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"
    IMAGE_GENERATION = "image_generation"
    AUDIO_STT = "audio_stt"
    AUDIO_TTS = "audio_tts"

class Provider(Enum):
    """AI service providers"""
    OPENAI = "openai"
    REPLICATE = "replicate"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

@dataclass
class UsageRecord:
    """Record of a single API usage"""
    timestamp: str
    provider: str
    service_type: str
    model_name: str
    operation: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    input_units: Optional[float] = None  # For non-token based services (images, audio)
    output_units: Optional[float] = None
    cost_usd: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageRecord':
        """Create from dictionary"""
        return cls(**data)

class BillingTracker:
    """
    Tracks billing and usage across all AI services
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize billing tracker
        
        Args:
            storage_path: Path to store billing data (defaults to project root)
        """
        if storage_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.storage_path = project_root / "billing_data.json"
        else:
            self.storage_path = Path(storage_path)
        self.usage_records: List[UsageRecord] = []
        self.session_start = datetime.now(timezone.utc).isoformat()
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing billing data"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.usage_records = [
                        UsageRecord.from_dict(record) 
                        for record in data.get('usage_records', [])
                    ]
                logger.info(f"Loaded {len(self.usage_records)} billing records")
        except Exception as e:
            logger.warning(f"Could not load billing data: {e}")
            self.usage_records = []
    
    def _save_data(self):
        """Save billing data to storage"""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "session_start": self.session_start,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "usage_records": [record.to_dict() for record in self.usage_records]
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save billing data: {e}")
    
    def track_usage(
        self,
        provider: Union[str, Provider],
        service_type: Union[str, ServiceType],
        model_name: str,
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UsageRecord:
        """
        Track a usage event
        
        Args:
            provider: AI provider name
            service_type: Type of service used
            model_name: Name of the model
            operation: Operation performed (e.g., 'chat', 'embedding', 'image_generation')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_units: Input units for non-token services (e.g., audio seconds, image count)
            output_units: Output units for non-token services
            metadata: Additional metadata
            
        Returns:
            UsageRecord object
        """
        # Convert enums to strings
        if isinstance(provider, Provider):
            provider = provider.value
        if isinstance(service_type, ServiceType):
            service_type = service_type.value
        
        # Calculate total tokens
        total_tokens = None
        if input_tokens is not None or output_tokens is not None:
            total_tokens = (input_tokens or 0) + (output_tokens or 0)
        
        # Calculate cost
        cost_usd = self._calculate_cost(
            provider, model_name, operation,
            input_tokens, output_tokens, input_units, output_units
        )
        
        # Create usage record
        record = UsageRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider=provider,
            service_type=service_type,
            model_name=model_name,
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_units=input_units,
            output_units=output_units,
            cost_usd=cost_usd,
            metadata=metadata or {}
        )
        
        # Add to records and save
        self.usage_records.append(record)
        self._save_data()
        
        logger.info(f"Tracked usage: {provider}/{model_name} - ${cost_usd:.6f}")
        return record
    
    def _get_model_pricing(self, provider: str, model_name: str) -> Optional[Dict[str, float]]:
        """Get pricing information from ModelManager"""
        try:
            from isa_model.core.model_manager import ModelManager
            pricing = ModelManager.MODEL_PRICING.get(provider, {}).get(model_name)
            if pricing:
                return pricing
            
            # Fallback to legacy pricing for backward compatibility
            legacy_pricing = self._get_legacy_pricing(provider, model_name)
            if legacy_pricing:
                return legacy_pricing
                
            return None
        except ImportError:
            # Fallback to legacy pricing if ModelManager is not available
            return self._get_legacy_pricing(provider, model_name)

    def _get_legacy_pricing(self, provider: str, model_name: str) -> Optional[Dict[str, float]]:
        """Legacy pricing information for backward compatibility"""
        LEGACY_PRICING = {
            "openai": {
                "gpt-4.1-mini": {"input": 0.4, "output": 1.6},
                "gpt-4o": {"input": 5.0, "output": 15.0},
                "gpt-4o-mini": {"input": 0.15, "output": 0.6},
                "text-embedding-3-small": {"input": 0.02, "output": 0.0},
                "text-embedding-3-large": {"input": 0.13, "output": 0.0},
                "whisper-1": {"input": 6.0, "output": 0.0},
                "tts-1": {"input": 15.0, "output": 0.0},
                "tts-1-hd": {"input": 30.0, "output": 0.0},
            },
            "ollama": {
                "default": {"input": 0.0, "output": 0.0}
            },
            "replicate": {
                "black-forest-labs/flux-schnell": {"input": 0.003, "output": 0.0},
                "meta/meta-llama-3-8b-instruct": {"input": 0.05, "output": 0.25},
            }
        }
        
        provider_pricing = LEGACY_PRICING.get(provider, {})
        return provider_pricing.get(model_name) or provider_pricing.get("default")

    def _calculate_cost(
        self,
        provider: str,
        model_name: str,
        operation: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        input_units: Optional[float] = None,
        output_units: Optional[float] = None
    ) -> float:
        """Calculate cost for a usage event"""
        try:
            # Get pricing using unified model manager
            model_pricing = self._get_model_pricing(provider, model_name)
            
            if not model_pricing:
                logger.warning(f"No pricing found for {provider}/{model_name}")
                return 0.0
            
            cost = 0.0
            
            # Token-based pricing (per 1M tokens)
            if input_tokens is not None and "input" in model_pricing:
                cost += (input_tokens / 1000000) * model_pricing["input"]
            
            if output_tokens is not None and "output" in model_pricing:
                cost += (output_tokens / 1000000) * model_pricing["output"]
            
            return cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.0
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get billing summary for current session"""
        session_records = [
            record for record in self.usage_records
            if record.timestamp >= self.session_start
        ]
        
        return self._generate_summary(session_records, "Current Session")
    
    def get_total_summary(self) -> Dict[str, Any]:
        """Get total billing summary"""
        return self._generate_summary(self.usage_records, "Total Usage")
    
    def get_provider_summary(self, provider: Union[str, Provider]) -> Dict[str, Any]:
        """Get billing summary for a specific provider"""
        if isinstance(provider, Provider):
            provider = provider.value
            
        provider_records = [
            record for record in self.usage_records
            if record.provider == provider
        ]
        
        return self._generate_summary(provider_records, f"{provider.title()} Usage")
    
    def _generate_summary(self, records: List[UsageRecord], title: str) -> Dict[str, Any]:
        """Generate billing summary from records"""
        if not records:
            return {
                "title": title,
                "total_cost": 0.0,
                "total_requests": 0,
                "providers": {},
                "services": {},
                "models": {}
            }
        
        total_cost = sum(record.cost_usd or 0 for record in records)
        total_requests = len(records)
        
        # Group by provider
        providers = {}
        for record in records:
            if record.provider not in providers:
                providers[record.provider] = {
                    "cost": 0.0,
                    "requests": 0,
                    "models": set()
                }
            providers[record.provider]["cost"] += record.cost_usd or 0
            providers[record.provider]["requests"] += 1
            providers[record.provider]["models"].add(record.model_name)
        
        # Convert sets to lists for JSON serialization
        for provider_data in providers.values():
            provider_data["models"] = list(provider_data["models"])
        
        # Group by service type
        services = {}
        for record in records:
            if record.service_type not in services:
                services[record.service_type] = {
                    "cost": 0.0,
                    "requests": 0
                }
            services[record.service_type]["cost"] += record.cost_usd or 0
            services[record.service_type]["requests"] += 1
        
        # Group by model
        models = {}
        for record in records:
            model_key = f"{record.provider}/{record.model_name}"
            if model_key not in models:
                models[model_key] = {
                    "cost": 0.0,
                    "requests": 0,
                    "total_tokens": 0
                }
            models[model_key]["cost"] += record.cost_usd or 0
            models[model_key]["requests"] += 1
            if record.total_tokens:
                models[model_key]["total_tokens"] += record.total_tokens
        
        return {
            "title": title,
            "total_cost": round(total_cost, 6),
            "total_requests": total_requests,
            "providers": providers,
            "services": services,
            "models": models,
            "period": {
                "start": records[0].timestamp if records else None,
                "end": records[-1].timestamp if records else None
            }
        }
    
    def print_summary(self, summary_type: str = "session"):
        """Print billing summary to console"""
        if summary_type == "session":
            summary = self.get_session_summary()
        elif summary_type == "total":
            summary = self.get_total_summary()
        else:
            raise ValueError("summary_type must be 'session' or 'total'")
        
        print(f"\n💰 {summary['title']} Billing Summary")
        print("=" * 50)
        print(f"💵 Total Cost: ${summary['total_cost']:.6f}")
        print(f"📊 Total Requests: {summary['total_requests']}")
        
        if summary['providers']:
            print("\n📈 By Provider:")
            for provider, data in summary['providers'].items():
                print(f"  {provider}: ${data['cost']:.6f} ({data['requests']} requests)")
        
        if summary['services']:
            print("\n🔧 By Service:")
            for service, data in summary['services'].items():
                print(f"  {service}: ${data['cost']:.6f} ({data['requests']} requests)")
        
        if summary['models']:
            print("\n🤖 By Model:")
            for model, data in summary['models'].items():
                tokens_info = f" ({data['total_tokens']} tokens)" if data['total_tokens'] > 0 else ""
                print(f"  {model}: ${data['cost']:.6f} ({data['requests']} requests){tokens_info}")

# Global billing tracker instance
_global_tracker: Optional[BillingTracker] = None

def get_billing_tracker() -> BillingTracker:
    """Get the global billing tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = BillingTracker()
    return _global_tracker

def track_usage(**kwargs) -> UsageRecord:
    """Convenience function to track usage"""
    return get_billing_tracker().track_usage(**kwargs)

def print_billing_summary(summary_type: str = "session"):
    """Convenience function to print billing summary"""
    get_billing_tracker().print_summary(summary_type) 