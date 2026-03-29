#!/usr/bin/env python3
"""AWS-powered Multi-Agent Code Assistant - Bedrock Copilot.

Modern, production-ready CLI tool with enterprise security.
"""

import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import Settings
from src.core.security.config import AWSCredentialChain
from src.core.storage.vector_memory_db import get_vector_db
from src.core.storage.thread_safety import get_thread_safe_storage


# Configure logging
def setup_logging(debug: bool = False) -> None:
    """Set up logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def print_banner() -> None:
    """Print welcome banner."""
    banner = r"""
╔═══════════════════════════════════════════════════════════╗
║                   Bedrock Copilot 3.0                     ║
║          AWS-Powered Multi-Agent Code Assistant           ║
║                                                           ║
║  Modern • Secure • Production-Ready                       ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_info() -> None:
    """Print system information."""
    settings = Settings()
    
    print("\n📊 System Information:")
    print(f"  • Environment: {settings.env}")
    print(f"  • Debug Mode: {settings.debug}")
    print(f"  • AWS Region: {settings.aws_region}")
    print(f"  • Default Model: {settings.default_model}")
    print(f"  • Vector DB: {settings.vector_db_path}")
    print()


def validate_environment() -> bool:
    """Validate environment and credentials."""
    print("🔍 Validating environment...\n")
    
    # Check AWS credentials
    if not AWSCredentialChain.validate():
        print("❌ AWS credentials not found")
        print("\nPlease set up AWS credentials using one of these methods:")
        print("  1. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("  2. AWS config file: ~/.aws/credentials")
        print("  3. IAM role (if running on EC2)")
        return False
    
    # Check vector DB
    try:
        db = get_vector_db()
        stats = db.get_stats()
        print(f"✅ Vector DB: {stats['backend']} at {stats['db_path']}")
    except Exception as e:
        print(f"⚠️  Vector DB: {e}")
    
    print("\n✅ Environment validation complete\n")
    return True


def print_commands() -> None:
    """Print available commands."""
    print("📋 Available Commands:")
    print()
    print("  General:")
    print("    • help              - Show this help message")
    print("    • version           - Show version information")
    print("    • status            - Show system status")
    print("    • exit              - Exit the program")
    print()
    print("  Code Analysis:")
    print("    • /ask <query>      - Ask AI about code")
    print("    • /analyze <file>   - Analyze code file")
    print("    • /map              - Map repository structure")
    print()
    print("  Configuration:")
    print("    • /config           - Show current configuration")
    print("    • /models           - List available models")
    print("    • /select <model>   - Select AI model")
    print()
    print("  Utilities:")
    print("    • /read <file>      - Read file content")
    print("    • /grep <pattern>   - Search files")
    print("    • /usage            - Show API usage")
    print()


def show_status() -> None:
    """Show system status."""
    settings = Settings()
    storage = get_thread_safe_storage()
    
    print("\n📈 System Status:")
    print(f"  • Environment: {settings.env}")
    print(f"  • Debug: {settings.debug}")
    print(f"  • Stored Items: {len(storage.get_all())}")
    
    try:
        db = get_vector_db()
        stats = db.get_stats()
        total_docs = sum(col.get("documents", 0) for col in stats["collections"])
        print(f"  • Vector DB Documents: {total_docs}")
    except Exception:
        print(f"  • Vector DB: Unavailable")
    
    print()


async def interactive_mode() -> None:
    """Run interactive CLI mode."""
    print("👋 Welcome to Bedrock Copilot 3.0!")
    print("Type 'help' for available commands or 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("copilot> ").strip()
            
            if not user_input:
                continue
            
            # Parse commands
            if user_input == "help":
                print_commands()
            elif user_input == "status":
                show_status()
            elif user_input == "version":
                print("\nBedrock Copilot v3.0.0 (Production)")
                print("Build: Modern Security-First Architecture\n")
            elif user_input == "exit":
                print("\n👋 Goodbye!")
                break
            else:
                print(f"\n❓ Unknown command: {user_input}")
                print("Type 'help' for available commands.\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main() -> int:
    """Main entry point."""
    settings = Settings()
    setup_logging(settings.debug)
    
    print_banner()
    print_info()
    
    if not validate_environment():
        return 1
    
    try:
        asyncio.run(interactive_mode())
        return 0
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=settings.debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
