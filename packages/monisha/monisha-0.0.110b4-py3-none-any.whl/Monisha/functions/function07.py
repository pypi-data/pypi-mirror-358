import asyncio
from .collections import SMessage
#======================================================================================

async def commandR(command, **kwargs):
    try:
        mainos = await asyncio.create_subprocess_exec(*command,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, **kwargs) 
        moonus = await mainos.communicate()
        result = moonus[0].strip()
        errors = moonus[1].strip()
        codeos = mainos.returncode
        return SMessage(results=result, taskcode=codeos, errors=errors)
    except Exception as errors:
        return SMessage(errors=errors)

#======================================================================================
