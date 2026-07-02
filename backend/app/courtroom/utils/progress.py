import asyncio
from typing import Dict

# Global dictionary mapping thread_id to asyncio.Queue
active_queues: Dict[str, asyncio.Queue] = {}

def update_progress(config, message: str):
    """
    Pushes a progress message into the active thread's streaming queue.
    """
    if not config:
        return
        
    thread_id = config.get("configurable", {}).get("thread_id")
    if not thread_id:
        return
        
    queue = active_queues.get(thread_id)
    if queue:
        try:
            # Safely put the message on the event loop running in this thread
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(
                queue.put_nowait,
                {"type": "progress", "message": message}
            )
        except RuntimeError:
            # Occurs if there is no running event loop in the current thread context
            pass
