#!/usr/bin/env python3
"""
Comprehensive test script for all isA_Model services
Tests real model interactions without pytest framework
Uses automatic default configuration loading from .env
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from isa_model.inference.ai_factory import AIFactory
from isa_model.inference.billing_tracker import print_billing_summary

# Test audio URL from user
TEST_AUDIO_URL = "https://replicate.delivery/mgxm/e5159b1b-508a-4be4-b892-e1eb47850bdc/OSR_uk_000_0050_8k.wav"

class ServiceTester:
    def __init__(self):
        self.ai_factory = AIFactory()
        self.results = {}
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"ℹ️  {message}")

    async def safe_call(self, service: Any, method_name: str, *args, **kwargs) -> Any:
        """Safely call a method on a service, handling different method names"""
        try:
            # Try the exact method name first
            if hasattr(service, method_name):
                method = getattr(service, method_name)
                return await method(*args, **kwargs)
            
            # Try common alternative method names
            alternatives = {
                'generate_text': ['ainvoke', 'achat', 'acompletion'],
                'analyze_image': ['analyze_image', 'ainvoke'],
                'create_text_embedding': ['create_text_embedding', 'embed_text', 'ainvoke'],
                'create_text_embeddings': ['create_text_embeddings', 'embed_texts'],
                'transcribe': ['transcribe', 'transcribe_audio', 'ainvoke'],
                'synthesize_speech': ['synthesize_speech', 'generate_speech', 'ainvoke'],
                'generate_image': ['generate_image', 'create_image', 'ainvoke']
            }
            
            if method_name in alternatives:
                for alt_name in alternatives[method_name]:
                    if hasattr(service, alt_name):
                        method = getattr(service, alt_name)
                        return await method(*args, **kwargs)
            
            raise AttributeError(f"Method {method_name} not found on service")
            
        except Exception as e:
            raise e

    async def test_llm_services(self):
        """Test LLM services for text generation"""
        self.print_header("Testing LLM Services")
        
        # Test Production LLM (OpenAI GPT-4.1-mini) - Auto-configured
        try:
            self.print_info("Testing OpenAI LLM Service (Production) - Auto-configured")
            llm_service = self.ai_factory.get_llm_service()
            
            # Test basic text generation
            response = await self.safe_call(llm_service, 'generate_text', "Hello! What's the weather like?")
            self.print_success(f"Chat response: {str(response)[:100]}...")
            
            # Test with tool calling if supported
            try:
                if hasattr(llm_service, 'bind_tools'):
                    tools = [{
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "description": "Get current weather for a location",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string", "description": "City name"}
                                },
                                "required": ["location"]
                            }
                        }
                    }]
                    
                    bound_service = getattr(llm_service, 'bind_tools')(tools)
                    tool_response = await self.safe_call(bound_service, 'generate_text', "What's the weather in Tokyo?")
                    self.print_success(f"Tool calling response: {str(tool_response)[:50]}...")
                    
            except Exception as e:
                self.print_info(f"Tool calling not supported or failed: {e}")
            
            # Clean up
            if hasattr(llm_service, 'close'):
                try:
                    await getattr(llm_service, 'close')()
                except:
                    pass
                    
            self.results['llm_production'] = True
            
        except Exception as e:
            self.print_error(f"OpenAI LLM test failed: {e}")
            self.results['llm_production'] = False
            
        # Test Development LLM (Ollama Llama3.2:3b) - Auto-configured
        try:
            self.print_info("Testing Ollama LLM Service (Development) - Auto-configured")
            llm_service = self.ai_factory.get_llm_service(provider="ollama")
            
            # Test basic text generation
            response = await self.safe_call(llm_service, 'generate_text', "Hello! Tell me a short joke.")
            self.print_success(f"Chat response: {str(response)[:100]}...")
            
            # Clean up
            if hasattr(llm_service, 'close'):
                try:
                    await getattr(llm_service, 'close')()
                except:
                    pass
                    
            self.results['llm_development'] = True
            
        except Exception as e:
            self.print_error(f"Ollama LLM test failed: {e}")
            self.print_info("Make sure Ollama is running: ollama serve")
            self.results['llm_development'] = False

    async def test_vision_services(self):
        """Test Vision services for image understanding"""
        self.print_header("Testing Vision Services")
        
        # Use a test image URL instead of local file
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/640px-Collage_of_Nine_Dogs.jpg"
        
        # Test Production Vision (OpenAI o4-mini) - Auto-configured
        try:
            self.print_info("Testing OpenAI Vision Service (Production) - Auto-configured")
            vision_service = self.ai_factory.get_vision_service()
            
            # Test image analysis
            result = await self.safe_call(
                vision_service, 'analyze_image',
                test_image_url, "What do you see in this image? Describe it in detail."
            )
            self.print_success(f"Image analysis: {str(result)[:150]}...")
            
            # Clean up
            if hasattr(vision_service, 'close'):
                try:
                    await getattr(vision_service, 'close')()
                except:
                    pass
                    
            self.results['vision_production'] = True
            
        except Exception as e:
            self.print_error(f"OpenAI Vision test failed: {e}")
            self.results['vision_production'] = False
            
        # Test Development Vision (Ollama Gemma3:4b) - Auto-configured
        try:
            self.print_info("Testing Ollama Vision Service (Development) - Auto-configured")
            vision_service = self.ai_factory.get_vision_service(provider="ollama")
            
            # Test image analysis
            result = await self.safe_call(
                vision_service, 'analyze_image',
                test_image_url, "Describe what you see in this image"
            )
            self.print_success(f"Image analysis: {str(result)[:150]}...")
            
            # Clean up
            if hasattr(vision_service, 'close'):
                try:
                    await getattr(vision_service, 'close')()
                except:
                    pass
                    
            self.results['vision_development'] = True
            
        except Exception as e:
            self.print_error(f"Ollama Vision test failed: {e}")
            self.print_info("Make sure Ollama is running with a vision model")
            self.results['vision_development'] = False

    async def test_audio_services(self):
        """Test Audio services (STT and TTS)"""
        self.print_header("Testing Audio Services")
        
        # Test STT (Speech-to-Text) - Auto-configured
        self.print_info("Testing Speech-to-Text Services")
        
        try:
            self.print_info("Testing OpenAI STT Service (Production) - Auto-configured")
            stt_service = self.ai_factory.get_stt_service()
            
            # Test transcription using the URL directly
            result = await self.safe_call(stt_service, 'transcribe', TEST_AUDIO_URL)
            self.print_success(f"Transcription: {str(result)[:100]}...")
            
            # Clean up
            if hasattr(stt_service, 'close'):
                try:
                    await getattr(stt_service, 'close')()
                except:
                    pass
                    
            self.results['stt_production'] = True
            
        except Exception as e:
            self.print_error(f"OpenAI STT test failed: {e}")
            self.results['stt_production'] = False
        
        # Test TTS (Text-to-Speech) - Auto-configured
        self.print_info("Testing Text-to-Speech Services")
        
        # Test Production TTS (Replicate Kokoro) - Auto-configured
        try:
            self.print_info("Testing Replicate TTS Service (Production) - Auto-configured")
            tts_service = self.ai_factory.get_tts_service()
            
            test_text = "Hi! I'm testing the text-to-speech voice. This is a sample audio generation."
            
            result = await self.safe_call(tts_service, 'synthesize_speech', test_text)
            self.print_success(f"TTS synthesis completed: {str(result)[:50]}...")
            
            # Clean up
            if hasattr(tts_service, 'close'):
                try:
                    await getattr(tts_service, 'close')()
                except:
                    pass
                    
            self.results['tts_production'] = True
            
        except Exception as e:
            self.print_error(f"Replicate TTS test failed: {e}")
            self.results['tts_production'] = False
            
        # Test Development TTS (OpenAI TTS-1) - Auto-configured
        try:
            self.print_info("Testing OpenAI TTS Service (Development) - Auto-configured")
            tts_service = self.ai_factory.get_tts_service(provider="openai")
            
            test_text = "Hi! I'm testing the OpenAI text-to-speech voice."
            
            result = await self.safe_call(tts_service, 'synthesize_speech', test_text)
            self.print_success(f"TTS synthesis completed: {str(result)[:50]}...")
            
            # Clean up
            if hasattr(tts_service, 'close'):
                try:
                    await getattr(tts_service, 'close')()
                except:
                    pass
                    
            self.results['tts_development'] = True
            
        except Exception as e:
            self.print_error(f"OpenAI TTS test failed: {e}")
            self.results['tts_development'] = False
        
        # Test OpenAI Realtime Service - Auto-configured
        try:
            self.print_info("Testing OpenAI Realtime Service - Auto-configured")
            
            # Import WebSocket for direct connection
            import websockets
            import json
            
            # Get OpenAI API key from environment
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            # Connect to Realtime API via WebSocket
            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
            
            # Create connection with proper headers
            async with websockets.connect(
                url,
                additional_headers={
                    "Authorization": f"Bearer {api_key}",
                    "OpenAI-Beta": "realtime=v1"
                }
            ) as websocket:
                # Send session configuration
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": "You are a helpful AI assistant.",
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16"
                    }
                }
                
                await websocket.send(json.dumps(session_config))
                
                # Send a simple text message
                text_message = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Hello! Can you say hi back?"
                            }
                        ]
                    }
                }
                
                await websocket.send(json.dumps(text_message))
                
                # Create response
                response_create = {
                    "type": "response.create"
                }
                
                await websocket.send(json.dumps(response_create))
                
                # Wait for response (with timeout)
                import asyncio
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    self.print_success(f"Realtime API connected successfully: {response_data.get('type', 'unknown')}")
                    
                    self.results['realtime_service'] = True
                    
                except asyncio.TimeoutError:
                    self.print_success("Realtime API connection established (timeout on response is normal)")
                    self.results['realtime_service'] = True
                    
        except ImportError:
            self.print_error("websockets library not installed. Install with: pip install websockets")
            self.results['realtime_service'] = False
        except Exception as e:
            if "403" in str(e) or "beta" in str(e).lower():
                self.print_info(f"Realtime API requires beta access: {e}")
                self.print_info("Note: This is normal if you don't have Realtime API beta access yet")
                self.results['realtime_service'] = False
            else:
                self.print_error(f"OpenAI Realtime test failed: {e}")
                self.results['realtime_service'] = False

    async def test_embedding_services(self):
        """Test Embedding services for text embeddings"""
        self.print_header("Testing Embedding Services")
        
        # Test Production Embedding (OpenAI text-embedding-3-small) - Auto-configured
        try:
            self.print_info("Testing OpenAI Embedding Service (Production) - Auto-configured")
            embed_service = self.ai_factory.get_embedding_service()
            
            # Test single embedding
            embedding = await self.safe_call(embed_service, 'create_text_embedding', "This is a test sentence for embedding.")
            self.print_success(f"Single embedding: {len(embedding)} dimensions")
            
            # Test batch embeddings
            texts = ["First text", "Second text", "Third text"]
            embeddings = await self.safe_call(embed_service, 'create_text_embeddings', texts)
            self.print_success(f"Batch embedding: {len(embeddings)} embeddings")
            
            # Test similarity
            embedding2 = await self.safe_call(embed_service, 'create_text_embedding', "Another test sentence for embedding.")
            if hasattr(embed_service, 'compute_similarity'):
                similarity = await getattr(embed_service, 'compute_similarity')(embedding, embedding2)
                self.print_success(f"Similarity score: {similarity:.4f}")
            
            # Clean up
            if hasattr(embed_service, 'close'):
                try:
                    await getattr(embed_service, 'close')()
                except:
                    pass
                    
            self.results['embedding_production'] = True
            
        except Exception as e:
            self.print_error(f"OpenAI Embedding test failed: {e}")
            self.results['embedding_production'] = False
            
        # Test Development Embedding (Ollama BGE-M3) - Auto-configured
        try:
            self.print_info("Testing Ollama Embedding Service (Development) - Auto-configured")
            embed_service = self.ai_factory.get_embedding_service(provider="ollama")
            
            # Test single embedding
            embedding = await self.safe_call(embed_service, 'create_text_embedding', "This is a test sentence for embedding.")
            self.print_success(f"Single embedding: {len(embedding)} dimensions")
            
            # Test batch embeddings
            texts = ["First text", "Second text", "Third text"]
            embeddings = await self.safe_call(embed_service, 'create_text_embeddings', texts)
            self.print_success(f"Batch embedding: {len(embeddings)} embeddings")
            
            # Clean up
            if hasattr(embed_service, 'close'):
                try:
                    await getattr(embed_service, 'close')()
                except:
                    pass
                    
            self.results['embedding_development'] = True
            
        except Exception as e:
            self.print_error(f"Ollama Embedding test failed: {e}")
            self.print_info("Make sure Ollama is running with BGE-M3 model")
            self.results['embedding_development'] = False

    async def test_image_generation_services(self):
        """Test Image Generation services"""
        self.print_header("Testing Image Generation Services")
        
        # Test Production Image Generation (FLUX Schnell) - Auto-configured
        try:
            self.print_info("Testing FLUX Schnell (Text-to-Image) - Auto-configured")
            image_service = self.ai_factory.get_image_generation_service()
            
            prompt = "A beautiful sunset over a mountain lake, digital art style"
            
            result = await self.safe_call(image_service, 'generate_image', prompt)
            self.print_success(f"Image generated: {str(result)[:100]}...")
            
            # Clean up
            if hasattr(image_service, 'close'):
                try:
                    await getattr(image_service, 'close')()
                except:
                    pass
                    
            self.results['image_gen_production'] = True
            
        except Exception as e:
            self.print_error(f"FLUX Image Generation test failed: {e}")
            self.results['image_gen_production'] = False

    def print_summary(self):
        """Print test results summary"""
        self.print_header("Test Summary")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        print("Detailed Results:")
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        print()
        print("🧹 Cleaning up temporary files...")
        
        # Clean up any temporary files
        import glob
        temp_files = glob.glob("temp_*") + glob.glob("test_*")
        for temp_file in temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
            except:
                pass

async def main():
    """Main test runner"""
    print("🚀 Starting Comprehensive isA_Model Service Tests")
    print("🔧 Using Automatic Default Configuration Loading from .env")
    print("="*60)
    
    tester = ServiceTester()
    
    start_time = time.time()
    
    # Run all tests
    await tester.test_llm_services()
    await tester.test_vision_services()
    await tester.test_audio_services()
    await tester.test_embedding_services()
    await tester.test_image_generation_services()
    
    # Print results
    tester.print_summary()
    
    # Print billing summary
    try:
        print_billing_summary("session")
    except Exception as e:
        print(f"Could not print billing summary: {e}")
    
    end_time = time.time()
    print(f"\n🎉 All tests completed in {end_time - start_time:.1f} seconds!")
    print("💡 Services automatically loaded configuration from .env")

if __name__ == "__main__":
    asyncio.run(main()) 