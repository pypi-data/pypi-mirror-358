"""
AgentMeter CLI

Command-line interface for AgentMeter SDK.
"""

import argparse
import json
import sys
from typing import Optional

from .client import AgentMeterClient
from .utils import get_env_config, create_client_from_env
from .exceptions import AgentMeterError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AgentMeter CLI - Track and monitor AI agent usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentmeter health                          # Check API health
  agentmeter events --project proj123        # List events
  agentmeter config                          # Show configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check API health')
    health_parser.add_argument('--url', help='API base URL')
    
    # Events command
    events_parser = subparsers.add_parser('events', help='List events')
    events_parser.add_argument('--project', required=True, help='Project ID')
    events_parser.add_argument('--agent', help='Agent ID')
    events_parser.add_argument('--user', help='User ID')
    events_parser.add_argument('--limit', type=int, default=10, help='Number of events to fetch')
    events_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    events_parser.add_argument('--format', choices=['json', 'table'], default='table', help='Output format')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.add_argument('--env', action='store_true', help='Show environment variables')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test connection and record a sample event')
    test_parser.add_argument('--project', required=True, help='Project ID')
    test_parser.add_argument('--agent', required=True, help='Agent ID')
    test_parser.add_argument('--user', help='User ID (default: test-user)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'health':
            handle_health(args)
        elif args.command == 'events':
            handle_events(args)
        elif args.command == 'config':
            handle_config(args)
        elif args.command == 'test':
            handle_test(args)
    except AgentMeterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(1)


def handle_health(args):
    """Handle health check command."""
    try:
        if args.url:
            client = AgentMeterClient(base_url=args.url)
        else:
            client = create_client_from_env()
        
        health = client.health_check()
        
        print("AgentMeter API Health Check:")
        print(f"  Status: {health.status}")
        print(f"  Database: {health.supabase}")
        print(f"  Environment: {health.environment}")
        print(f"  Timestamp: {health.timestamp}")
        
        if health.status == "ok":
            print("✅ API is healthy")
        else:
            print("❌ API is not healthy")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Health check failed: {e}", file=sys.stderr)
        sys.exit(1)


def handle_events(args):
    """Handle events listing command."""
    try:
        client = create_client_from_env()
        
        events_response = client.get_events(
            project_id=args.project,
            agent_id=args.agent,
            user_id=args.user,
            limit=args.limit,
            offset=args.offset
        )
        
        if args.format == 'json':
            # Output as JSON
            output = {
                "events": [
                    {
                        "id": event.id,
                        "project_id": event.project_id,
                        "agent_id": event.agent_id,
                        "user_id": event.user_id,
                        "event_type": event.event_type,
                        "request_count": event.request_count,
                        "input_tokens": event.input_tokens,
                        "output_tokens": event.output_tokens,
                        "total_cost": event.total_cost,
                        "timestamp": event.timestamp.isoformat()
                    }
                    for event in events_response.events
                ],
                "pagination": events_response.pagination
            }
            print(json.dumps(output, indent=2))
        else:
            # Output as table
            print(f"Found {len(events_response.events)} events:")
            print()
            
            if events_response.events:
                # Print header
                print(f"{'ID':<12} {'Agent':<15} {'Type':<15} {'Tokens In':<10} {'Tokens Out':<11} {'Cost':<8} {'Timestamp':<20}")
                print("-" * 100)
                
                # Print events
                for event in events_response.events:
                    print(f"{event.id:<12} {event.agent_id:<15} {event.event_type:<15} "
                          f"{event.input_tokens:<10} {event.output_tokens:<11} "
                          f"${event.total_cost:<7.4f} {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                print()
                print(f"Showing {args.offset + 1}-{args.offset + len(events_response.events)} "
                      f"of {events_response.pagination['total']} events")
            else:
                print("No events found.")
                
    except Exception as e:
        print(f"Failed to fetch events: {e}", file=sys.stderr)
        sys.exit(1)


def handle_config(args):
    """Handle config display command."""
    config = get_env_config()
    
    print("AgentMeter Configuration:")
    print(f"  Base URL: {config['base_url']}")
    print(f"  Project ID: {config['project_id'] or '(not set)'}")
    print(f"  Agent ID: {config['agent_id'] or '(not set)'}")
    print(f"  User ID: {config['user_id'] or '(not set)'}")
    print(f"  API Key: {'***' if config['api_key'] else '(not set)'}")
    print(f"  Timeout: {config['timeout']}s")
    print(f"  Retries: {config['retries']}")
    print(f"  Auto Flush: {config['auto_flush']}")
    print(f"  Flush Interval: {config['flush_interval']}s")
    print(f"  Batch Size: {config['batch_size']}")
    
    if args.env:
        print("\nEnvironment Variables:")
        env_vars = [
            "AGENTMETER_BASE_URL",
            "AGENTMETER_PROJECT_ID", 
            "AGENTMETER_AGENT_ID",
            "AGENTMETER_USER_ID",
            "AGENTMETER_API_KEY",
            "AGENTMETER_TIMEOUT",
            "AGENTMETER_RETRIES",
            "AGENTMETER_AUTO_FLUSH",
            "AGENTMETER_FLUSH_INTERVAL",
            "AGENTMETER_BATCH_SIZE"
        ]
        
        for var in env_vars:
            import os
            value = os.getenv(var)
            if var == "AGENTMETER_API_KEY" and value:
                value = "***"
            print(f"  {var}: {value or '(not set)'}")


def handle_test(args):
    """Handle test command."""
    try:
        from .models import MeterEvent, EventType
        
        client = create_client_from_env()
        
        print("Testing AgentMeter connection...")
        
        # Test health
        health = client.health_check()
        print(f"✅ Health check passed: {health.status}")
        
        # Create test event
        event = MeterEvent(
            project_id=args.project,
            agent_id=args.agent,
            user_id=args.user or "test-user",
            event_type=EventType.API_REQUEST,
            tokens_in=10,
            tokens_out=5,
            api_calls=1,
            metadata={
                "test": True,
                "cli_version": "0.1.0",
                "source": "agentmeter-cli"
            }
        )
        
        print("Recording test event...")
        response = client.record_event(event)
        print(f"✅ Test event recorded: {response.event['id']}")
        print(f"   Total cost: ${response.event['total_cost']}")
        
        print("\n🎉 Test completed successfully!")
        print("Your AgentMeter integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()