# Python Imports #
from typing import List

# External Imports #
import json
import aiofiles


async def read_json_file(file_path: str) -> List[str]:
    """ Return all URLs from the QUEUE file. """
    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)
    return data