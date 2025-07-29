import unittest
from unittest.mock import MagicMock, AsyncMock

from slidetextbridge.plugins import text_filters

def make_slide(texts):
    return text_filters.TextFilteredSlide(
            {'shapes': [{'text': t} for t in texts]}
    )

class TestTextFilters(unittest.IsolatedAsyncioTestCase):

    def test_type_name(self):
        self.assertEqual(text_filters.TextLinebreakFilter.type_name(), 'linebreak')
        self.assertEqual(text_filters.RegexFilter.type_name(), 'regex')

    def test_config(self):
        cfg = text_filters.RegexFilter.config(
                data = {'patterns': [
                    {'p': 'p1', 'r': 'r1'},
                    {'p': 'p2', 'r': 'r2'},
                ]}
        )

        self.assertEqual(len(cfg.patterns), 2)
        self.assertEqual(cfg.patterns[0][0].pattern, 'p1')
        self.assertEqual(cfg.patterns[0][1], 'r1')
        self.assertEqual(cfg.patterns[1][0].pattern, 'p2')
        self.assertEqual(cfg.patterns[1][1], 'r2')

    async def test_linebreak_filter_strip(self):
        ctx = MagicMock()

        cfg = text_filters.TextLinebreakFilter.config({
            'strip': True,
        })
        filter_obj = text_filters.TextLinebreakFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()
        slide = make_slide(['A', 'B ', ' C ', ' D'])

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['A', 'B', 'C', 'D'])

        cfg = text_filters.TextLinebreakFilter.config({
            'strip': False,
        })
        filter_obj = text_filters.TextLinebreakFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()
        slide = make_slide(['A', 'B ', ' C ', ' D'])

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['A', 'B ', ' C ', ' D'])

    async def test_linebreak_filter_split_join(self):
        ctx = MagicMock()

        cfg = text_filters.TextLinebreakFilter.config({
            'split_long_line': 8,
            'joined_column_max': 4,
            'join_by': '-'
        })
        filter_obj = text_filters.TextLinebreakFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()
        slide = make_slide([
            'abcdefghijk', # Check too long ASCII word
            'a\nb',
        ])

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, [
            'abcdefgh\nijk',
            'a-b',
        ])

    async def test_linebreak_filter_delimiters(self):
        ctx = MagicMock()

        cfg = text_filters.TextLinebreakFilter.config({
            'shape_delimiter': '/',
            'line_delimiter': ':',
        })
        filter_obj = text_filters.TextLinebreakFilter(ctx=ctx, cfg=cfg)
        filter_obj.emit = AsyncMock()
        slide = make_slide([
            'a\nb',
            'c',
        ])

        await filter_obj.update(slide, args=None)

        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0]
        self.assertEqual(res.to_texts(), [
            'a:b',
            'c',
        ])
        self.assertEqual(str(res), 'a:b/c')


    async def test_regex_filter(self):
        ctx = MagicMock()

        cfg = text_filters.RegexFilter.config({
            'patterns': [
                {'p': r'(Th|th)is', 'r': r'\1at'},
            ]
        })
        filter_obj = text_filters.RegexFilter(ctx=ctx, cfg=cfg)

        filter_obj.emit = AsyncMock()
        slide = make_slide(['This is a pen.'])
        await filter_obj.update(slide, args=None)
        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['That is a pen.'])

        filter_obj.emit = AsyncMock()
        slide = MagicMock()
        slide.to_texts.return_value = ['Who is this?', ]
        await filter_obj.update(slide, args=None)
        filter_obj.emit.assert_awaited_once()
        res = filter_obj.emit.await_args[0][0].to_texts()
        self.assertEqual(res, ['Who is that?'])

    # TODO: Also check the combination with jmespath filter


if __name__ == '__main__':
    unittest.main()
