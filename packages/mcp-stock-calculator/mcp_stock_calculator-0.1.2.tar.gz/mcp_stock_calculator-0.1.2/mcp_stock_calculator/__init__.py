import argparse
import asyncio

from .server import run_server

def main():
    """MCP Wiki kel: Read Wikipedia articles and convert them to Markdown."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to read Wikipedia articles and convert them to Markdown."
    )
    parser.parse_args()
    asyncio.run(run_server())

if __name__ == "__main__":
    main()

