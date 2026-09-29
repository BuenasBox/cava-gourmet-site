"""Costa Rica date helpers — single source of truth.

Costa Rica does not observe daylight saving; its offset is always UTC-6.
Bare `time.strftime("%d/%m/%Y")` (no explicit `t`) uses `time.localtime()`,
i.e. the SERVER's timezone — on Vercel that's UTC, not Costa Rica. Near
Costa Rica midnight (18:00-23:59 CR = 00:00-05:59 UTC the next day), that
recorded the wrong calendar day. `registrar_experiencia.py` and `scan.py`
both had their own copy of this mistake.
"""

import time

_CR_OFFSET_SECONDS = 6 * 3600


def costa_rica_today(now=None):
    """Today's date in Costa Rica (UTC-6, no DST), as dd/mm/yyyy."""
    ts = time.time() if now is None else now
    return time.strftime("%d/%m/%Y", time.gmtime(ts - _CR_OFFSET_SECONDS))
