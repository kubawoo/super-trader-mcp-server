import signal
import sys
from super_trader.mcpserver import start_server


def main() -> None:
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    start_server()


if __name__ == "__main__":
    main()
