import asyncio
import os

import httpx
_original_request_init = httpx.Request.__init__

def _patched_request_init(self, *args, **kwargs):
    _original_request_init(self, *args, **kwargs)
    
    # Find and modify problematic headers
    headers_to_remove = []
    headers_to_modify = {}
    
    for name in self.headers.keys():
        name_lower = name.lower()
        # Remove all X-Stainless-* headers (OpenAI SDK identifiers)
        if 'stainless' in name_lower:
            headers_to_remove.append(name)
        # Replace OpenAI User-Agent with a generic one
        elif name_lower == 'user-agent' and 'openai' in self.headers[name].lower():
            headers_to_modify[name] = 'python-requests/2.32.5'
    
    # Apply modifications
    for name in headers_to_remove:
        del self.headers[name]
    for name, value in headers_to_modify.items():
        self.headers[name] = value

httpx.Request.__init__ = _patched_request_init

# Now import everything else
from dotenv import load_dotenv
from spoon_ai.llm import LLMManager, ConfigurationManager
from spoon_ai.schema import Message

# 1. Load your API keys from .env
load_dotenv("agent/.env")

async def main():
    print("🚀 Starting SpoonOS Hello World...")

    # 2. Configuration Manager
    # This automatically reads OPENAI_API_KEY and OPENAI_BASE_URL from your environment
    config = ConfigurationManager()

    # 3. Initialize the Brain (LLMManager)
    # This is the simplest way to talk to the AI without defining complex tools yet
    agent_brain = LLMManager(config)

    # 4. Define the conversation history
    messages = [
        Message(role="system", content="You are a helpful AI assistant."),
        Message(role="user", content="Say 'Hello World' and tell me what you can help with.")
    ]

    try:
        # 5. Send the prompt to Sudo/OpenAI via SpoonOS
        print("⏳ Sending request to Sudo AI via SpoonOS...")
        response = await agent_brain.chat(messages, model="gpt-4")

        # 6. Print the result
        print("\n🤖 Agent Reply:")
        print(f"\"{response.content}\"")
        print("\n✅ Connection Successful!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Tip: Check your OPENAI_BASE_URL and API Key in .env")

if __name__ == "__main__":
    asyncio.run(main())
