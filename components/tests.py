from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase


class PaginationQueryTagTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def render_tag(self, params):
        request = self.factory.get("/test", data=params)
        template = Template(
            "{% load querystring_tags %}{% pagination_query as q %}{{ q }}"
        )
        return template.render(Context({"request": request}))

    def test_removes_page_parameter(self):
        output = self.render_tag({"page": "2", "search": "abc"})
        self.assertEqual(output, "&amp;search=abc")

    def test_returns_empty_when_only_page(self):
        output = self.render_tag({"page": "3"})
        self.assertEqual(output, "")

    def test_returns_empty_for_no_params(self):
        output = self.render_tag({})
        self.assertEqual(output, "")


class PaginationTemplateTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def render_pagination(self, page_number, params=None):
        params = params or {}
        paginator = Paginator(list(range(30)), 5)
        page_obj = paginator.get_page(page_number)
        request = self.factory.get("/test", params)
        tmpl = Template(
            "{% load querystring_tags %}{% include 'components/_pagination.html' %}"
        )
        return tmpl.render(Context({"request": request, "page_obj": page_obj}))

    def test_links_include_existing_querystring(self):
        html = self.render_pagination(1, {"filter": "x"})
        self.assertIn("?page=2&amp;filter=x", html)
