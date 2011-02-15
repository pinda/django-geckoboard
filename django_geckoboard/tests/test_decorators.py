"""
Tests for the Geckoboard decorators.
"""

from django.http import HttpRequest, HttpResponseForbidden
from django.utils.datastructures import SortedDict

from django_geckoboard.decorators import widget, number_widget, rag_widget, \
        text_widget, pie_chart, line_chart, geck_o_meter, TEXT_NONE, \
        TEXT_INFO, TEXT_WARN
from django_geckoboard.tests.utils import TestCase
import base64


class WidgetDecoratorTestCase(TestCase):
    """
    Tests for the ``widget`` decorator.
    """

    def setUp(self):
        super(WidgetDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.xml_request = HttpRequest()
        self.xml_request.POST['format'] = '1'
        self.json_request = HttpRequest()
        self.json_request.POST['format'] = '2'

    def test_api_key(self):
        self.settings_manager.set(GECKOBOARD_API_KEY='abc')
        req = HttpRequest()
        req.META['HTTP_AUTHORIZATION'] = "basic %s" % base64.b64encode('abc')
        resp = widget(lambda r: "test")(req)
        self.assertEqual('<?xml version="1.0" ?><root>test</root>',
                resp.content)

    def test_missing_api_key(self):
        self.settings_manager.set(GECKOBOARD_API_KEY='abc')
        req = HttpRequest()
        resp = widget(lambda r: "test")(req)
        self.assertTrue(isinstance(resp, HttpResponseForbidden), resp)
        self.assertEqual('Geckoboard API key incorrect', resp.content)

    def test_wrong_api_key(self):
        self.settings_manager.set(GECKOBOARD_API_KEY='abc')
        req = HttpRequest()
        req.META['HTTP_AUTHORIZATION'] = "basic %s" % base64.b64encode('def')
        resp = widget(lambda r: "test")(req)
        self.assertTrue(isinstance(resp, HttpResponseForbidden), resp)
        self.assertEqual('Geckoboard API key incorrect', resp.content)

    def test_xml_get(self):
        req = HttpRequest()
        req.GET['format'] = '1'
        resp = widget(lambda r: "test")(req)
        self.assertEqual('<?xml version="1.0" ?><root>test</root>',
                resp.content)

    def test_json_get(self):
        req = HttpRequest()
        req.GET['format'] = '2'
        resp = widget(lambda r: "test")(req)
        self.assertEqual('"test"', resp.content)

    def test_xml_post(self):
        req = HttpRequest()
        req.POST['format'] = '1'
        resp = widget(lambda r: "test")(req)
        self.assertEqual('<?xml version="1.0" ?><root>test</root>',
                resp.content)

    def test_json_post(self):
        req = HttpRequest()
        req.POST['format'] = '2'
        resp = widget(lambda r: "test")(req)
        self.assertEqual('"test"', resp.content)

    def test_scalar_xml(self):
        resp = widget(lambda r: "test")(self.xml_request)
        self.assertEqual('<?xml version="1.0" ?><root>test</root>',
                resp.content)

    def test_scalar_json(self):
        resp = widget(lambda r: "test")(self.json_request)
        self.assertEqual('"test"', resp.content)

    def test_dict_xml(self):
        resp = widget(lambda r: SortedDict([('a', 1),
                ('b', 2)]))(self.xml_request)
        self.assertEqual('<?xml version="1.0" ?><root><a>1</a><b>2</b></root>',
                resp.content)

    def test_dict_json(self):
        resp = widget(lambda r: SortedDict([('a', 1),
                ('b', 2)]))(self.json_request)
        self.assertEqual('{"a": 1, "b": 2}', resp.content)

    def test_list_xml(self):
        resp = widget(lambda r: {'list': [1, 2, 3]})(self.xml_request)
        self.assertEqual('<?xml version="1.0" ?><root><list>1</list>'
                '<list>2</list><list>3</list></root>', resp.content)

    def test_list_json(self):
        resp = widget(lambda r: {'list': [1, 2, 3]})(self.json_request)
        self.assertEqual('{"list": [1, 2, 3]}', resp.content)

    def test_dict_list_xml(self):
        resp = widget(lambda r: {'item': [{'value': 1, 'text': "test1"},
                {'value': 2, 'text': "test2"}]})(self.xml_request)
        self.assertEqual('<?xml version="1.0" ?><root>'
                '<item><text>test1</text><value>1</value></item>'
                '<item><text>test2</text><value>2</value></item></root>',
                resp.content)

    def test_dict_list_json(self):
        resp = widget(lambda r: {'item': [SortedDict([('value', 1),
                ('text', "test1")]), SortedDict([('value', 2), ('text',
                        "test2")])]})(self.json_request)
        self.assertEqual('{"item": [{"value": 1, "text": "test1"}, '
                '{"value": 2, "text": "test2"}]}', resp.content)


class NumberDecoratorTestCase(TestCase):
    """
    Tests for the ``number`` decorator.
    """

    def setUp(self):
        super(NumberDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.request = HttpRequest()
        self.request.POST['format'] = '2'

    def test_scalar(self):
        widget = number_widget(lambda r: 10)
        resp = widget(self.request)
        self.assertEqual('{"item": [{"value": 10}]}', resp.content)

    def test_singe_value(self):
        widget = number_widget(lambda r: [10])
        resp = widget(self.request)
        self.assertEqual('{"item": [{"value": 10}]}', resp.content)

    def test_two_values(self):
        widget = number_widget(lambda r: [10, 9])
        resp = widget(self.request)
        self.assertEqual('{"item": [{"value": 10}, {"value": 9}]}',
                resp.content)


class RAGDecoratorTestCase(TestCase):
    """
    Tests for the ``rag`` decorator.
    """

    def setUp(self):
        super(RAGDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.request = HttpRequest()
        self.request.POST['format'] = '2'

    def test_scalars(self):
        widget = rag_widget(lambda r: (10, 5, 1))
        resp = widget(self.request)
        self.assertEqual(
                '{"item": [{"value": 10}, {"value": 5}, {"value": 1}]}',
                resp.content)

    def test_tuples(self):
        widget = rag_widget(lambda r: ((10, "ten"), (5, "five"),
                (1, "one")))
        resp = widget(self.request)
        self.assertEqual('{"item": [{"value": 10, "text": "ten"}, '
                '{"value": 5, "text": "five"}, {"value": 1, "text": "one"}]}',
                resp.content)


class TextDecoratorTestCase(TestCase):
    """
    Tests for the ``text`` decorator.
    """

    def setUp(self):
        super(TextDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.request = HttpRequest()
        self.request.POST['format'] = '2'

    def test_string(self):
        widget = text_widget(lambda r: "test message")
        resp = widget(self.request)
        self.assertEqual('{"item": [{"text": "test message", "type": 0}]}',
                resp.content)

    def test_list(self):
        widget = text_widget(lambda r: ["test1", "test2"])
        resp = widget(self.request)
        self.assertEqual('{"item": [{"text": "test1", "type": 0}, '
                '{"text": "test2", "type": 0}]}', resp.content)

    def test_list_tuples(self):
        widget = text_widget(lambda r: [("test1", TEXT_NONE),
                ("test2", TEXT_INFO), ("test3", TEXT_WARN)])
        resp = widget(self.request)
        self.assertEqual('{"item": [{"text": "test1", "type": 0}, '
                '{"text": "test2", "type": 2}, '
                '{"text": "test3", "type": 1}]}', resp.content)


class PieChartDecoratorTestCase(TestCase):
    """
    Tests for the ``pie_chart`` decorator.
    """

    def setUp(self):
        super(PieChartDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.request = HttpRequest()
        self.request.POST['format'] = '2'

    def test_scalars(self):
        widget = pie_chart(lambda r: [1, 2, 3])
        resp = widget(self.request)
        self.assertEqual(
                '{"item": [{"value": 1}, {"value": 2}, {"value": 3}]}',
                resp.content)

    def test_tuples(self):
        widget = pie_chart(lambda r: [(1, ), (2, ), (3, )])
        resp = widget(self.request)
        self.assertEqual(
                '{"item": [{"value": 1}, {"value": 2}, {"value": 3}]}',
                resp.content)

    def test_2tuples(self):
        widget = pie_chart(lambda r: [(1, "one"), (2, "two"),
                (3, "three")])
        resp = widget(self.request)
        self.assertEqual('{"item": [{"value": 1, "label": "one"}, '
                '{"value": 2, "label": "two"}, '
                '{"value": 3, "label": "three"}]}', resp.content)

    def test_3tuples(self):
        widget = pie_chart(lambda r: [(1, "one", "00112233"),
                (2, "two", "44556677"), (3, "three", "8899aabb")])
        resp = widget(self.request)
        self.assertEqual('{"item": ['
                '{"value": 1, "label": "one", "colour": "00112233"}, '
                '{"value": 2, "label": "two", "colour": "44556677"}, '
                '{"value": 3, "label": "three", "colour": "8899aabb"}]}',
                resp.content)


class LineChartDecoratorTestCase(TestCase):
    """
    Tests for the ``line_chart`` decorator.
    """

    def setUp(self):
        super(LineChartDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.request = HttpRequest()
        self.request.POST['format'] = '2'

    def test_values(self):
        widget = line_chart(lambda r: ([1, 2, 3],))
        resp = widget(self.request)
        self.assertEqual('{"item": [1, 2, 3], "settings": {}}', resp.content)

    def test_x_axis(self):
        widget = line_chart(lambda r: ([1, 2, 3],
                ["first", "last"]))
        resp = widget(self.request)
        self.assertEqual('{"item": [1, 2, 3], '
                '"settings": {"axisx": ["first", "last"]}}', resp.content)

    def test_axes(self):
        widget = line_chart(lambda r: ([1, 2, 3],
                ["first", "last"], ["low", "high"]))
        resp = widget(self.request)
        self.assertEqual('{"item": [1, 2, 3], "settings": '
                '{"axisx": ["first", "last"], "axisy": ["low", "high"]}}',
                resp.content)

    def test_color(self):
        widget = line_chart(lambda r: ([1, 2, 3],
                ["first", "last"], ["low", "high"], "00112233"))
        resp = widget(self.request)
        self.assertEqual('{"item": [1, 2, 3], "settings": '
                '{"axisx": ["first", "last"], "axisy": ["low", "high"], '
                '"colour": "00112233"}}', resp.content)


class GeckOMeterDecoratorTestCase(TestCase):
    """
    Tests for the ``line_chart`` decorator.
    """

    def setUp(self):
        super(GeckOMeterDecoratorTestCase, self).setUp()
        self.settings_manager.delete('GECKOBOARD_API_KEY')
        self.request = HttpRequest()
        self.request.POST['format'] = '2'

    def test_scalars(self):
        widget = geck_o_meter(lambda r: (2, 1, 3))
        resp = widget(self.request)
        self.assertEqual('{"item": 2, "max": {"value": 3}, '
                '"min": {"value": 1}}', resp.content)

    def test_tuples(self):
        widget = geck_o_meter(lambda r: (2, (1, "min"), (3, "max")))
        resp = widget(self.request)
        self.assertEqual('{"item": 2, "max": {"value": 3, "text": "max"}, '
                '"min": {"value": 1, "text": "min"}}', resp.content)
