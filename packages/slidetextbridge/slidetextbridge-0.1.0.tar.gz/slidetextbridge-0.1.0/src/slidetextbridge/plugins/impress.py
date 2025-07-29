'''
Get text from LibreOffice Impress
'''

import asyncio
import uno
from slidetextbridge.core import config
from . import base


class ImpressCapture(base.PluginBase):
    '''
    Get text from LibreOffice Impress
    '''
    @classmethod
    def type_name(cls):
        return 'impress'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg, has_src=False)
        cfg.add_argment('host', type=str, default='localhost')
        cfg.add_argment('port', type=int, default=2002)
        cfg.add_argment('pipe_name', type=str)
        cfg.add_argment('poll_wait_time', type=float, default=0.1)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self._last_slide = self
        self._desktop = None
        self._connect_error_reported = False
        self._get_slide_error_reported = False

    async def initialize(self):
        asyncio.create_task(self._loop())

    async def _loop(self):
        while True:
            if not self._desktop:
                try:
                    self._connect()
                    self._connect_error_reported = False
                except Exception as e: # pylint: disable=W0718
                    self._desktop = None
                    if not self._connect_error_reported:
                        self._connect_error_reported = True
                        print(f'Error: impress({self.cfg.location}): failed to connect: {e}')
                    await asyncio.sleep(1)
                    continue

            try:
                slide = self._get_slide()
                self._get_slide_error_reported = False
            except Exception as e: # pylint: disable=W0718
                if not self._get_slide_error_reported:
                    self._get_slide_error_reported = True
                    print(f'Error: impress({self.cfg.location}): failed to get slide: {e}')
                self._desktop = None
                await asyncio.sleep(1)
                continue

            if slide != self._last_slide:
                self._last_slide = slide
                await self.emit(ImpressSlide(slide))

            await asyncio.sleep(self.cfg.poll_wait_time)

    def _connect(self):
        context = uno.getComponentContext()
        resolver = context.ServiceManager.createInstanceWithContext(
                'com.sun.star.bridge.UnoUrlResolver', context)
        if self.cfg.pipe_name:
            uno_conn = f'uno:pipe,name={self.cfg.pipe_name}'
        else:
            uno_conn = f'uno:socket,host={self.cfg.host},port={self.cfg.port}'
        uno_inst = resolver.resolve(f'{uno_conn};urp;StarOffice.ComponentContext')
        self._desktop = uno_inst.ServiceManager.createInstanceWithContext(
                'com.sun.star.frame.Desktop', uno_inst)

    def _get_slide(self):
        c = self._desktop.getCurrentComponent()
        if not c:
            return None
        presentation = c.getPresentation()
        controller = presentation.getController()
        if not controller:
            return None
        return controller.getCurrentSlide()


class ImpressSlide(base.SlideBase):
    'The slide class returned by ImpressCapture'

    def __init__(self, slide=None, data=None):
        self._slide = slide
        if isinstance(data, list):
            self._dict = {'shapes': data}
        else:
            self._dict = data

    def to_texts(self):
        '''
        List all texts
        :return:  List of strings
        '''
        if self._dict:
            return _list_texts(self._dict)
        if self._slide:
            texts = []
            for shape in self._slide:
                texts.append(shape.Text.getString())
            return texts
        return []

    def to_dict(self):
        if self._dict:
            return self._dict
        if not self._slide:
            return {}
        shapes = []
        for shape in self._slide:
            s = base.SlideBase.convert_object(shape, params=(
                ('Text', lambda v: v.getString()),
                'CharColor',
                'CharHeight',
                'CharFontName',
            ))
            s['text'] = shape.Text.getString()
            shapes.append(s)
        self._dict = {'shapes': shapes}
        return self._dict


def _list_texts(obj):
    if isinstance(obj, str):
        return [obj, ]
    if isinstance(obj, (int, float, bool)):
        return []
    if isinstance(obj, dict):
        for key in ('shapes', 'text'):
            if key in obj:
                return _list_texts(obj[key])
        return []
    ret = []
    for x in obj:
        if x:
            ret += _list_texts(x)
    return ret
