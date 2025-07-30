"""
Simple test for async Ollama integration with qwen2.5:3b model.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ollama import AsyncClient
    OLLAMA_AVAILABLE = True
except ImportError:
    print("❌ Ollama not available. Install with: pip install ollama")
    OLLAMA_AVAILABLE = False
    AsyncClient = None


async def test_simple_async_ollama():
    """Test simple async Ollama chat."""
    if not OLLAMA_AVAILABLE or AsyncClient is None:
        print("❌ AsyncClient not available")
        return
    
    print("🧪 Testing Async Ollama with qwen2.5:3b")
    print("-" * 40)
    
    try:
        client = AsyncClient()
        
        # Simple test message
        message = {'role': 'user', 'content': 'Write a simple Python function that adds two numbers. Return only the code.'}
        
        print("📤 Sending request to qwen2.5:3b...")
        response = await client.chat(model='qwen2.5:3b', messages=[message])
        
        print("✅ Response received:")
        print(response.message.content)
        
        # Save to file
        with open('simple_add_function.py', 'w', encoding='utf-8') as f:
            f.write(response.message.content)
        print("\n💾 Saved to: simple_add_function.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running and qwen2.5:3b model is available")


async def test_system_prompt():
    """Test with system prompt."""
    if not OLLAMA_AVAILABLE or AsyncClient is None:
        print("❌ AsyncClient not available")
        return
    
    print("\n🧪 Testing with System Prompt")
    print("-" * 40)
    
    try:
        client = AsyncClient()
        
        messages = [
            {
                'role': 'system',
                'content': 'You are a Python expert. Write clean, documented code.'
            },
            {
                'role': 'user',
                'content': 'Create a function to calculate factorial. Include docstring and example.'
            }
        ]
        
        print("📤 Sending request with system prompt...")
        response = await client.chat(model='qwen2.5:3b', messages=messages)
        
        print("✅ Response received:")
        print(response.message.content)
        
        # Save to file
        with open('factorial_function.py', 'w', encoding='utf-8') as f:
            f.write(response.message.content)
        print("\n💾 Saved to: factorial_function.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all tests."""
    print("🚀 Testing Async Ollama Integration")
    print("=" * 50)
    
    await test_simple_async_ollama()
    await test_system_prompt()
    
    print("\n✅ Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
