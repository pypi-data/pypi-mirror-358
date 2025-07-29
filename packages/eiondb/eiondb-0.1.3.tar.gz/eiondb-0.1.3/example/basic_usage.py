#!/usr/bin/env python3
"""
Basic usage example for Eion Python SDK

This example demonstrates how to use the Eion SDK for cluster management
and agent coordination.

IMPORTANT: Make sure your Eion server is running first!

Quick setup with Docker:
    docker-compose up -d

Or see: https://pypi.org/project/eiondb/ for full setup instructions.
"""

import os
from eiondb import EionClient, EionError

def main():
    """Main example function"""
    
    print("🚀 Eion Python SDK - Basic Usage Example")
    print("=" * 50)
    
    # Initialize client with clear example API key
    # NOTE: Use the SAME key you set in your server's CLUSTER_API_KEY
    client = EionClient(
        base_url="http://localhost:8080",
        cluster_api_key=os.getenv("EION_CLUSTER_API_KEY", "my-secret-api-key-123")
    )
    
    try:
        # Check server health
        print("🔍 Checking server health...")
        health = client.health_check()
        print(f"   Status: {health.get('status')}")
        
        # Create a user
        print("\n👤 Creating user...")
        user = client.create_user(
            user_id="demo_user_001",
            name="Demo User"
        )
        print(f"   Created user: {user.get('user_id')}")
        
        # Register an agent with correct permissions
        print("\n🤖 Registering agent...")
        agent = client.register_agent(
            agent_id="assistant_001",
            name="Demo Assistant",
            permission="crud",  # Use 'crud', 'cr', or 'r' (not 'rw')
            description="A demo assistant agent with full permissions"
        )
        print(f"   Registered agent: {agent.get('agent_id')} with permission: {agent.get('permission')}")
        
        # Create a session
        print("\n💬 Creating session...")
        session = client.create_session(
            session_id="demo_session_001",
            user_id="demo_user_001",
            session_name="Demo Conversation"
        )
        print(f"   Created session: {session.get('session_id')}")
        
        # List agents
        print("\n📋 Listing all agents...")
        agents = client.list_agents()
        print(f"   Found {len(agents)} agents:")
        for agent in agents:
            print(f"     - {agent.get('agent_id')}: {agent.get('name')} ({agent.get('permission')})")
        
        # Monitor agent (if you have time range data)
        print("\n📊 Getting agent analytics...")
        try:
            analytics = client.monitor_agent("assistant_001", {
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-12-31T23:59:59Z"
            })
            print(f"   Agent interactions: {analytics.get('total_interactions', 0)}")
        except EionError as e:
            print(f"   Analytics not available: {e.message}")
        
        print("\n✅ All operations completed successfully!")
        
        # Cleanup (optional)
        print("\n🧹 Cleaning up...")
        client.delete_session("demo_session_001")
        client.delete_agent("assistant_001")
        client.delete_user("demo_user_001")
        print("   Cleanup completed!")
        
    except EionError as e:
        print(f"\n❌ Eion API Error: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        if e.status_code == 403:
            print("   💡 Hint: Make sure your cluster_api_key matches your server configuration")
        if e.response_data.get("hint"):
            print(f"   Hint: {e.response_data['hint']}")
    except Exception as e:
        print(f"\n💥 Unexpected Error: {e}")
        print("   💡 Make sure your Eion server is running: docker-compose up -d")

if __name__ == "__main__":
    print("📦 Install: pip install eiondb")
    print("🔧 Setup:   https://pypi.org/project/eiondb/")
    print()
    main() 