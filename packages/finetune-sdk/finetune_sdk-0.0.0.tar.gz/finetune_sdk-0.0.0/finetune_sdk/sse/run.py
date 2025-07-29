import aiohttp
import asyncio

from finetune_sdk.sse.event_listener import EventListener
from finetune_sdk.sse.events import handle_event
from finetune_sdk.agent.registry import AGENT_REGISTRY, autodiscover_agents

async def start_worker():
    print("Discovering agent functions...")
    discovered = autodiscover_agents()
    print(f"Imported {len(discovered)} modules.")
    print(f"Agents registered: {list(AGENT_REGISTRY.keys())}")

    retry_delay = 1  # Start with 1 second
    max_delay = 60  # Cap the backoff

    while True:
        try:
            event_listener = EventListener(handle_event)
            await event_listener.start()
            print(f"Disconnected from event stream. Retrying in {retry_delay}s...")
        except aiohttp.ClientResponseError as e:
            print(f"HTTP error occurred: {e.status} - {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

        await asyncio.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, max_delay)  # Exponential backoff


if __name__ == "__main__":
    asyncio.run(start_worker())