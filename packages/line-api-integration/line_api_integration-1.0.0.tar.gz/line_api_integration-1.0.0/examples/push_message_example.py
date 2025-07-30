"""Example demonstrating push message functionality."""

import asyncio

from line_api import LineAPIConfig, LineMessagingClient, TextMessage


async def main() -> None:
    """Demonstrate push message functionality."""
    # Load configuration from environment
    try:
        config = LineAPIConfig.from_env_file()
        print(f"✅ Configuration loaded: {config}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        print("\nPlease ensure you have the following environment variables set:")
        print("- LINE_CHANNEL_ACCESS_TOKEN")
        print("- LINE_CHANNEL_SECRET")
        print("\nOr create a .env file with these values.")
        return

    # Get user ID from input
    user_id = input("Enter the LINE user ID to send message to: ").strip()
    if not user_id:
        print("❌ User ID is required")
        return

    # Create messages
    messages = [
        TextMessage.create("Hello from LINE API Integration Library! 🚀"),
        TextMessage.create("This is a push message sent using the new library."),
    ]

    # Send push message
    async with LineMessagingClient(config) as client:
        try:
            success = await client.push_message(user_id, messages)
            if success:
                print("✅ Push message sent successfully!")
            else:
                print("❌ Failed to send push message")
        except Exception as e:
            print(f"❌ Error sending push message: {e}")


if __name__ == "__main__":
    asyncio.run(main())
