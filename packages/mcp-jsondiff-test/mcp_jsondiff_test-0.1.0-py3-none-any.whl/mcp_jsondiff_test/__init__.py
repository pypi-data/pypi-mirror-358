import argparse
from .server import mcp
def main():
    """MCP jsondiff kel: Compare the two json strings."""
    parser = argparse.ArgumentParser(
        description="Gives you the ability to compare the two json strings."
    )
    parser.parse_args()
    mcp.run()
if __name__ == "__main__":
    main()