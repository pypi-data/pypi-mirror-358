
from collections import deque
from typing import Dict, List, Optional, Any


class QueueManager:
    """Manages music queues for different guilds."""
    
    def __init__(self):
        self.queues: Dict[int, deque] = {}
    
    def add_to_queue(self, guild_id: int, source: Any) -> None:
        """Add a source to the guild's queue."""
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        self.queues[guild_id].append(source)
    
    def get_next(self, guild_id: int) -> Optional[Any]:
        """Get the next source from the guild's queue."""
        if guild_id in self.queues and self.queues[guild_id]:
            return self.queues[guild_id].popleft()
        return None
    
    def get_queue(self, guild_id: int) -> List[str]:
        """Get the current queue as a list of titles."""
        if guild_id in self.queues:
            return [source.title for source in self.queues[guild_id]]
        return []
    
    def clear_queue(self, guild_id: int) -> None:
        """Clear the guild's queue."""
        if guild_id in self.queues:
            self.queues[guild_id].clear()
    
    def remove_from_queue(self, guild_id: int, index: int) -> bool:
        """Remove a specific item from the queue by index."""
        if guild_id in self.queues and 0 <= index < len(self.queues[guild_id]):
            queue_list = list(self.queues[guild_id])
            queue_list.pop(index)
            self.queues[guild_id] = deque(queue_list)
            return True
        return False
    
    def shuffle_queue(self, guild_id: int) -> None:
        """Shuffle the guild's queue."""
        if guild_id in self.queues:
            import random
            queue_list = list(self.queues[guild_id])
            random.shuffle(queue_list)
            self.queues[guild_id] = deque(queue_list)
    
    def queue_size(self, guild_id: int) -> int:
        """Get the size of the guild's queue."""
        if guild_id in self.queues:
            return len(self.queues[guild_id])
        return 0
