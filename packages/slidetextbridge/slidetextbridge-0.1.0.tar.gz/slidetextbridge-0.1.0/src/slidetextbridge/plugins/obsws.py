'''
Send text to OBS Studio
'''

import simpleobsws
from slidetextbridge.core import config
from . import base


class ObsWsEmitter(base.PluginBase):
    '''
    Emit text to OBS Studio
    '''
    @classmethod
    def type_name(cls):
        return 'obsws'

    @staticmethod
    def config(data):
        'Return the config object'
        cfg = config.ConfigBase()
        base.set_config_arguments(cfg)
        cfg.add_argment('url', type=str, default='ws://localhost:4455/')
        cfg.add_argment('password', type=str, default=None)
        cfg.add_argment('source_name', type=str, default=None)
        cfg.parse(data)
        return cfg

    def __init__(self, ctx, cfg=None):
        super().__init__(ctx=ctx, cfg=cfg)
        self.ws = None
        self.connect_to(cfg.src)

    async def _ws_connect(self):
        self.ws = simpleobsws.WebSocketClient(url=self.cfg.url, password=self.cfg.password)
        await self.ws.connect()
        if not await self.ws.wait_until_identified():
            self.ws.disconnect()
            self.ws = None

    async def update(self, slide, args):
        if not slide:
            text = ''
        elif isinstance(slide, str):
            text = slide
        else:
            text = str(slide)

        try:
            if not self.ws:
                await self._ws_connect()

            await self._send_request('SetInputSettings', {
                'inputName': self.cfg.source_name,
                'inputSettings': {'text': text}
            })
        except Exception as e: # pylint: disable=W0718
            print(f'Error: obsws({self.cfg.location}): {e}')

    async def _send_request(self, req, data, retry=2):
        while retry > 0:
            retry -= 1
            try:
                res = await self.ws.call(simpleobsws.Request(req, data))
                if res.ok():
                    return res.responseData
            except Exception as e: # pylint: disable=W0718
                try:
                    await self.ws.disconnect()
                except: # pylint: disable=W0702
                    pass
                if retry == 0:
                    raise e
                try: # pylint: disable=W0702
                    await self._ws_connect()
                except:
                    self.ws = None
