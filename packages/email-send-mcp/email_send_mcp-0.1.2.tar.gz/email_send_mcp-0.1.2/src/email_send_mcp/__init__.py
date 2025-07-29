"""MCP Email Server - A Model Context Protocol server for email functionality."""

import argparse
import asyncio
from . import server


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description="MCP Email Server - Send emails via MCP protocol")
    parser.add_argument("--dir", type=str, help="Specify the directory where attachments are located.")

    args = parser.parse_args()

    asyncio.run(server.serve(args.dir))


__version__ = "0.1.0"
__all__ = ["main", "server"]

if __name__ == "__main__":
    main()
