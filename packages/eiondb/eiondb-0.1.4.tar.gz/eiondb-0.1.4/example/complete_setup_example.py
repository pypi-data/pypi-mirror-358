#!/usr/bin/env python3
"""
Complete Eion Setup and Usage Example

This example demonstrates the full Eion workflow:
1. Setup server infrastructure 
2. Run the server
3. Use cluster management features
4. Clean up

IMPORTANT: This will download ~3GB of dependencies on first run!
"""

import os
import time
from eiondb import EionClient, EionError

def main():
    """Complete Eion example"""
    
    print("🚀 Eion Complete Setup and Usage Example")
    print("=" * 50)
    
    client = EionClient(
        cluster_api_key=os.getenv("EION_CLUSTER_API_KEY", "my-secret-api-key-123")
    )
    
    try:
        # Step 1: Setup infrastructure (one-time, downloads ~3GB)
        print("\n📦 Setting up Eion infrastructure...")
        print("   This will download Docker images, Python packages, and AI models")
        print("   (This may take several minutes on first run)")
        
        client.setup()
        
        # Step 2: Run server in background
        print("\n🚀 Starting Eion server in background...")
        client.run(detached=True)
        
        # Wait a moment for server to be ready
        print("   Waiting for server to be ready...")
        time.sleep(5)
        
        # Step 3: Verify server is healthy
        if client.server_health():
            print("✅ Server is healthy and ready!")
        else:
            print("❌ Server not responding - check setup")
            return 1
        
        # Step 4: Use cluster management features
        print("\n🏢 Demonstrating cluster management...")
        
        # Create a user
        print("   Creating user...")
        user = client.create_user(
            user_id="demo_user",
            name="Demo User"
        )
        print(f"   ✅ Created user: {user['user_id']}")
        
        # Register an agent
        print("   Registering agent...")
        agent = client.register_agent(
            agent_id="demo_agent",
            name="Demo Assistant Agent",
            permission="crud",
            description="A demo agent for testing multi-agent memory"
        )
        print(f"   ✅ Registered agent: {agent['agent_id']}")
        
        # Create a session  
        print("   Creating session...")
        session = client.create_session(
            session_id="demo_session",
            user_id="demo_user"
        )
        print(f"   ✅ Created session: {session['session_id']}")
        
        # Show how agents would use HTTP directly for memory operations
        print("\n🤖 Agent memory operations (via HTTP):")
        print("   Agents can now use these endpoints:")
        print("   POST http://localhost:8080/sessions/v1/demo_session/memories?agent_id=demo_agent&user_id=demo_user")
        print("   GET  http://localhost:8080/sessions/v1/demo_session/memories?agent_id=demo_agent&user_id=demo_user") 
        print("   GET  http://localhost:8080/sessions/v1/demo_session/memories/search?agent_id=demo_agent&user_id=demo_user&query=pizza")
        
        print("\n✅ Example completed successfully!")
        print("\n🔄 Server is running in background")
        print("   - Use client.stop() to stop the server")
        print("   - Use client.reset() to clean everything") 
        print("   - Server URL: http://localhost:8080")
        
        return 0
        
    except EionError as e:
        print(f"\n❌ Example failed: {e}")
        return 1


def cleanup_example():
    """Example of how to clean up Eion"""
    print("\n🧹 Cleanup Example")
    print("=" * 20)
    
    client = EionClient()
    
    try:
        # Stop the server
        print("🛑 Stopping server...")
        client.stop()
        
        # Reset everything to clean state
        print("🔄 Resetting to clean state...")
        client.reset()
        
        print("✅ Cleanup complete!")
        
    except EionError as e:
        print(f"❌ Cleanup failed: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_example()
    else:
        exit_code = main()
        
        if exit_code == 0:
            print("\n" + "=" * 50)
            print("💡 To clean up, run: python complete_setup_example.py cleanup")
        
        sys.exit(exit_code) 