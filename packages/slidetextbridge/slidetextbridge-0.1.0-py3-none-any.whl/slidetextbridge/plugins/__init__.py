'''
Accumulate plugins
'''

from . import text_filters
from . import debug_helper

plugin_classes = []

plugin_classes.append(text_filters.TextLinebreakFilter)
plugin_classes.append(text_filters.RegexFilter)
plugin_classes.append(debug_helper.StdoutEmitter)

try:
    from . import obsws
    plugin_classes.append(obsws.ObsWsEmitter)
except ImportError as e:
    print(f'Info: obsws is unsupported: {e}')

try:
    from . import powerpoint
    plugin_classes.append(powerpoint.PowerPointCapture)
except ImportError as e:
    print(f'Info: Microsoft PowerPoint is unsupported: {e}')

try:
    from . import impress
    plugin_classes.append(impress.ImpressCapture)
except ImportError as e:
    print(f'Info: LibreOffice is unsupported: {e}')

try:
    from . import jmespath_filter
    plugin_classes.append(jmespath_filter.JMESPathFilter)
except ImportError as e:
    print(f'Info: JMESPath filter is unsupported: {e}')

try:
    from . import webserver
    plugin_classes.append(webserver.WebServerEmitter)
except ImportError as e:
    print(f'Info: Web server is unsupported: {e}')

plugins = {cls.type_name(): cls for cls in plugin_classes}
