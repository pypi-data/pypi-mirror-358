#!/usr/bin/env python3
"""
Test script to verify the ISA Model training setup.

This script tests:
1. Import functionality
2. Configuration creation
3. Training factory initialization
4. Basic functionality without actual training
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all components can be imported."""
    logger.info("Testing imports...")
    
    try:
        # Test main factory import
        from isa_model.training import TrainingFactory, train_gemma
        logger.info("✅ Main factory imports successful")
        
        # Test core imports
        from isa_model.training import (
            TrainingConfig, LoRAConfig, DatasetConfig,
            BaseTrainer, SFTTrainer, TrainingUtils, DatasetManager
        )
        logger.info("✅ Core component imports successful")
        
        # Test cloud imports
        from isa_model.training import (
            RunPodConfig, StorageConfig, JobConfig, TrainingJobOrchestrator
        )
        logger.info("✅ Cloud component imports successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration creation."""
    logger.info("Testing configuration creation...")
    
    try:
        from isa_model.training import TrainingConfig, LoRAConfig, DatasetConfig
        
        # Test LoRA config
        lora_config = LoRAConfig(
            use_lora=True,
            lora_rank=8,
            lora_alpha=16
        )
        logger.info("✅ LoRA config created successfully")
        
        # Test dataset config
        dataset_config = DatasetConfig(
            dataset_path="tatsu-lab/alpaca",
            dataset_format="alpaca",
            max_length=1024
        )
        logger.info("✅ Dataset config created successfully")
        
        # Test training config
        training_config = TrainingConfig(
            model_name="google/gemma-2-4b-it",
            output_dir="./test_output",
            lora_config=lora_config,
            dataset_config=dataset_config
        )
        logger.info("✅ Training config created successfully")
        
        # Test config serialization
        config_dict = training_config.to_dict()
        logger.info("✅ Config serialization successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_factory_initialization():
    """Test training factory initialization."""
    logger.info("Testing factory initialization...")
    
    try:
        from isa_model.training import TrainingFactory
        
        # Initialize factory
        factory = TrainingFactory()
        logger.info("✅ TrainingFactory initialized successfully")
        
        # Test utility functions
        from isa_model.training import TrainingUtils
        
        model_info = TrainingUtils.get_model_info("google/gemma-2-4b-it")
        logger.info(f"✅ Model info retrieved: {model_info.get('model_type', 'unknown')}")
        
        memory_estimate = TrainingUtils.estimate_memory_usage(
            "google/gemma-2-4b-it", batch_size=4, use_lora=True
        )
        logger.info(f"✅ Memory estimate: ~{memory_estimate.get('total_training_memory_gb', 0):.1f}GB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Factory initialization failed: {e}")
        return False

def test_convenience_functions():
    """Test convenience functions."""
    logger.info("Testing convenience functions...")
    
    try:
        from isa_model.training import train_gemma
        
        # This should not actually train, just validate the function exists
        logger.info("✅ train_gemma function available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Convenience function test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("ISA MODEL TRAINING SETUP TEST")
    logger.info("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Factory Initialization Test", test_factory_initialization),
        ("Convenience Functions Test", test_convenience_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name}...")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info("=" * 60)
    logger.info(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Training setup is working correctly.")
        logger.info("\n📋 NEXT STEPS:")
        logger.info("1. Run: python examples/gemma_training_example.py --quick")
        logger.info("2. Set up your .env.local file with API keys")
        logger.info("3. Try local training with a small dataset")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 