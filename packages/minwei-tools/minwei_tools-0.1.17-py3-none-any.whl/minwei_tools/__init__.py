
import sys
if '-m' not in sys.argv:
    from .dotter import Dotter
    from .async_dotter import AsyncDotter
    from .dotter_style import DotStyle as DotStyle
    from .dotter import piano as piano
    from .dotter import cycle as cycle
    import minwei_tools.rs_result as rs_result
    import minwei_tools.server as server
    import minwei_tools.uv_doc as uv_doc


__all__ = [
    "Dotter",
    "AsyncDotter",
    "piano",
    "slash",
    "rs_result",
    "server",
    "DotStyle"
]