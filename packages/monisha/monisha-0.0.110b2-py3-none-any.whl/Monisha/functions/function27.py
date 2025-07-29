import asyncio
from .function09 import Storage
from ..exceptions import QueuedAlready
#======================================================================================

class Queue:

    async def add(tid, storage=Storage.USER_TID):
        if tid not in storage:
            storage.append(tid)
        else:
            raise QueuedAlready("ALREADY ADDED TO QUEUE")

#======================================================================================

    async def delete(tid, storage=Storage.USER_TID):
        storage.remove(tid) if tid in storage else 0

    async def position(tid, storage=Storage.USER_TID):
        return storage.index(tid) if tid in storage else 0

#======================================================================================

    async def queue(cid, wait=1, maximum=1, storage=Storage.USER_TID):
        while cid in storage:
            if storage.index(cid) + 1 > maximum:
                await asyncio.sleep(wait)
            else:
                break

#======================================================================================

    async def message(imog, text, button=None, maximum=1, storage=Storage.USER_TID):
        if maximum < len(storage):
            try: await imog.edit(text=text, reply_markup=button)
            except Exception: pass

#======================================================================================
