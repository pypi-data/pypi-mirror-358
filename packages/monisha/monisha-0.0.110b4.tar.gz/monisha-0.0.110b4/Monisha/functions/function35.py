import arrow
from .function05 import Doxo
#============================================================

class Peimed:

    async def get01(moonus, location="Asia/Kolkata"):
        moon01 = arrow.now(location)
        moon02 = moon01.shift(days=moonus)
        moones = moon02.format(Doxo.DATA05)
        return moones

    async def get02(moonus, location="Asia/Kolkata"):
        moon01 = arrow.now(location)
        moon02 = moon01.format(Doxo.DATA05)
        moon03 = arrow.get(moon02, Doxo.DATA05)
        moon04 = arrow.get(moonus, Doxo.DATA05)
        moones = (moon04 - moon03).days
        return moones

    async def get03(moonus, location="Asia/Kolkata"):
        moon01 = arrow.now(location)
        moon02 = arrow.get(moonus, Doxo.DATA05)
        moon03 = moon02.replace(tzinfo=location)
        moones = round((moon03 - moon01).total_seconds())
        return moones

#============================================================
