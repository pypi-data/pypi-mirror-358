from ..client.game_client import GameClient
import asyncio
from typing import Callable, Dict







class Interpreter(GameClient):
    
    
    async def _interpreter(self, action: Dict[str, Callable]) -> None:
        
        
        auto_tasks = []
        for prefix, handler in action.items():
            task = asyncio.create_task(self.process_data(prefix, handler, 0.5))
            auto_tasks.append(task)
            
        await asyncio.gather(*auto_tasks)  
            
            
    