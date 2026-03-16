import json
from decimal import Decimal

from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from packages.models import Package
from sub_categories.models import SubCategory

from .models import Component
from .views import ALLOWED_FILTER_FIELDS, ALLOWED_FILTER_LOOKUPS

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def make_supporting_objects():
    """Create the minimum set of related objects required by Component."""
    category = Category.objects.create(name="Resistor")
    sub_category = SubCategory.objects.create(name="SMD", category=category)
    brand = Brand.objects.create(name="Yageo")
    package = Package.objects.create(name="0402")
    return category, sub_category, brand, package


def make_component(**kwargs) -> Component:
    """Create a Component with sensible defaults."""
    category, sub_category, brand, package = make_supporting_objects()
    defaults = {
        "title": "R1 10k",
        "category": category,
        "sub_category": sub_category,
        "brand": brand,
        "package": package,
        "quantity": 100,
        "price": Decimal("0.05"),
    }
    defaults.update(kwargs)
    return Component.objects.create(**defaults)


def make_user(username="testuser", permissions=None) -> User:
    """Create an active test user, optionally assigning codenames.

    Args:
        username (str): Username to assign.
        permissions (list[str]): Codenames such as 'view_component'.

    Returns:
        User: Saved user instance.
    """
    user = User.objects.create_user(username=username, password="testpass123")
    if permissions:
        perms = Permission.objects.filter(codename__in=permissions)
        user.user_permissions.set(perms)
    return user


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class ComponentModelTest(TestCase):
    def setUp(self):
        self.category, self.sub_category, self.brand, self.package = (
            make_supporting_objects()
        )

    def _build(self, **kwargs) -> Component:
        defaults = {
            "title": "C1 100nF",
            "category": self.category,
            "sub_category": self.sub_category,
            "brand": self.brand,
            "package": self.package,
            "quantity": 50,
            "price": Decimal("0.02"),
        }
        defaults.update(kwargs)
        return Component(**defaults)

    def test_str_returns_title(self):
        component = self._build(title="LM358")
        self.assertEqual(str(component), "LM358")

    def test_total_value_calculated_correctly(self):
        component = self._build(price=Decimal("1.50"), quantity=10)
        self.assertEqual(component.total_value, Decimal("15.00"))

    def test_total_value_with_zero_price(self):
        component = self._build(price=Decimal("0.00"), quantity=10)
        self.assertEqual(component.total_value, Decimal("0.00"))

    def test_total_value_with_none_price(self):
        component = self._build(price=None, quantity=10)
        self.assertEqual(component.total_value, Decimal("0"))

    def test_total_value_with_zero_quantity(self):
        component = self._build(price=Decimal("1.00"), quantity=0)
        self.assertEqual(component.total_value, Decimal("0"))

    def test_clean_raises_on_negative_quantity(self):
        component = self._build(quantity=-1)
        with self.assertRaises(ValidationError) as ctx:
            component.clean()
        self.assertIn("quantity", ctx.exception.message_dict)

    def test_clean_raises_on_negative_price(self):
        component = self._build(price=Decimal("-0.01"))
        with self.assertRaises(ValidationError) as ctx:
            component.clean()
        self.assertIn("price", ctx.exception.message_dict)

    def test_clean_raises_on_both_negative(self):
        component = self._build(quantity=-5, price=Decimal("-1.00"))
        with self.assertRaises(ValidationError) as ctx:
            component.clean()
        errors = ctx.exception.message_dict
        self.assertIn("quantity", errors)
        self.assertIn("price", errors)

    def test_clean_passes_for_valid_values(self):
        component = self._build(quantity=0, price=Decimal("0.00"))
        # Should not raise
        component.clean()

    def test_clean_passes_when_price_is_none(self):
        component = self._build(price=None)
        component.clean()

    def test_default_ordering_by_title(self):
        Component.objects.create(
            title="Z Component",
            category=self.category,
            sub_category=self.sub_category,
            brand=self.brand,
            package=self.package,
        )
        Component.objects.create(
            title="A Component",
            category=self.category,
            sub_category=self.sub_category,
            brand=self.brand,
            package=self.package,
        )
        titles = list(Component.objects.values_list("title", flat=True))
        self.assertEqual(titles, sorted(titles))

    def test_equivalent_self_reference(self):
        c1 = Component.objects.create(
            title="NE555",
            category=self.category,
            sub_category=self.sub_category,
            brand=self.brand,
            package=self.package,
        )
        c2 = Component.objects.create(
            title="LM555",
            category=self.category,
            sub_category=self.sub_category,
            brand=self.brand,
            package=self.package,
            equivalent=c1,
        )
        self.assertEqual(c2.equivalent, c1)
        self.assertIn(c2, c1.equivalents.all())


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------


class ComponentFormTest(TestCase):
    def setUp(self):
        self.category, self.sub_category, self.brand, self.package = (
            make_supporting_objects()
        )

    def _form_data(self, **kwargs):
        defaults = {
            "title": "R1 10k",
            "category": self.category.pk,
            "sub_category": self.sub_category.pk,
            "brand": self.brand.pk,
            "package": self.package.pk,
            "quantity": 10,
            "price": "0.10",
        }
        defaults.update(kwargs)
        return defaults

    def test_valid_form(self):
        from .forms import ComponentForm

        form = ComponentForm(data=self._form_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_title_required(self):
        from .forms import ComponentForm

        form = ComponentForm(data=self._form_data(title=""))
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_category_required(self):
        from .forms import ComponentForm

        form = ComponentForm(data=self._form_data(category=""))
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_negative_quantity_invalid(self):
        from .forms import ComponentForm

        form = ComponentForm(data=self._form_data(quantity=-1))
        # Django's IntegerField doesn't validate sign by default; clean() does.
        # If the form is valid, clean() on the model would catch it.
        # Test that model.clean() is called via full_clean inside form.
        if form.is_valid():
            instance = form.save(commit=False)
            with self.assertRaises(ValidationError):
                instance.full_clean()

    def test_optional_fields_can_be_blank(self):
        from .forms import ComponentForm

        form = ComponentForm(
            data=self._form_data(
                description="",
                location="",
                serie_number="",
                price="",
                equivalent="",
            )
        )
        self.assertTrue(form.is_valid(), form.errors)


# ---------------------------------------------------------------------------
# View tests — ComponentListView
# ---------------------------------------------------------------------------


class ComponentListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("component_list")
        self.user = make_user(permissions=["view_component"])
        self.component = make_component()

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_user_without_permission_gets_403(self):
        user = make_user(username="noperm")
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_user_with_permission_gets_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_components_appear_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn(self.component, response.context["components"])

    def test_filter_by_title_icontains(self):
        make_component(
            **{
                "title": "Capacitor",
                "category": self.component.category,
                "sub_category": self.component.sub_category,
                "brand": self.component.brand,
                "package": self.component.package,
            }
        )
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
            {
                "filterField[]": "title",
                "filterLookup[]": "icontains",
                "filterValue[]": "R1",
            },
        )
        components = list(response.context["components"])
        self.assertTrue(all("R1" in c.title for c in components))

    def test_disallowed_filter_field_is_ignored(self):
        """Security: an unknown filterField must not be applied."""
        self.client.force_login(self.user)
        # Attempt to filter on 'password' or any non-whitelisted field
        response = self.client.get(
            self.url,
            {
                "filterField[]": "created_at__year",
                "filterLookup[]": "exact",
                "filterValue[]": "2000",
            },
        )
        # Should return 200 with all components (filter silently ignored)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.component, response.context["components"])

    def test_disallowed_lookup_is_ignored(self):
        """Security: non-whitelisted lookup types are silently ignored."""
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
            {
                "filterField[]": "title",
                "filterLookup[]": "regex",  # not in ALLOWED_FILTER_LOOKUPS
                "filterValue[]": ".*",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.component, response.context["components"])

    def test_sort_by_allowed_field(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {"sort": "quantity", "order": "desc"})
        self.assertEqual(response.status_code, 200)

    def test_sort_by_disallowed_field_ignored(self):
        self.client.force_login(self.user)
        # 'id' is not in ALLOWED_SORT_FIELDS; should not raise
        response = self.client.get(self.url, {"sort": "id", "order": "asc"})
        self.assertEqual(response.status_code, 200)

    def test_context_has_filter_state(self):
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
            {
                "filterField[]": "title",
                "filterLookup[]": "icontains",
                "filterValue[]": "R1",
            },
        )
        fs = response.context["filter_state"]
        self.assertEqual(fs["fields"], ["title"])
        self.assertEqual(fs["lookups"], ["icontains"])
        self.assertEqual(fs["values"], ["R1"])

    def test_pagination_is_10_per_page(self):
        # Create 15 components total (1 already exists in setUp)
        category = self.component.category
        sub_category = self.component.sub_category
        brand = self.component.brand
        package = self.component.package
        for i in range(14):
            Component.objects.create(
                title=f"Extra {i}",
                category=category,
                sub_category=sub_category,
                brand=brand,
                package=package,
            )
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["components"]), 10)


# ---------------------------------------------------------------------------
# View tests — ComponentCreateView
# ---------------------------------------------------------------------------


class ComponentCreateViewTest(TestCase):
    def setUp(self):
        self.url = reverse("component_create")
        self.user = make_user(permissions=["add_component"])
        self.category, self.sub_category, self.brand, self.package = (
            make_supporting_objects()
        )

    def test_get_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirects(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_post_creates_component_and_redirects(self):
        self.client.force_login(self.user)
        data = {
            "title": "New Component",
            "category": self.category.pk,
            "sub_category": self.sub_category.pk,
            "brand": self.brand.pk,
            "package": self.package.pk,
            "quantity": 5,
            "price": "1.00",
        }
        response = self.client.post(self.url, data)
        self.assertTrue(Component.objects.filter(title="New Component").exists())
        # Don't follow the redirect — the test user only has add_component, not view_component
        self.assertRedirects(
            response, reverse("component_list"), fetch_redirect_response=False
        )

    def test_post_invalid_data_shows_form_errors(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"title": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


# ---------------------------------------------------------------------------
# View tests — ComponentDetailView
# ---------------------------------------------------------------------------


class ComponentDetailViewTest(TestCase):
    def setUp(self):
        self.user = make_user(permissions=["view_component"])
        self.component = make_component()
        self.url = reverse("component_detail", kwargs={"pk": self.component.pk})

    def test_returns_200_for_existing_component(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["component"], self.component)

    def test_returns_404_for_missing_component(self):
        self.client.force_login(self.user)
        url = reverse("component_detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_redirects(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_filter_params_preserved_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url + "?sort=title&order=asc")
        self.assertIn("sort=title", response.context["filter_params"])


# ---------------------------------------------------------------------------
# View tests — ComponentUpdateView
# ---------------------------------------------------------------------------


class ComponentUpdateViewTest(TestCase):
    def setUp(self):
        self.user = make_user(permissions=["change_component"])
        self.component = make_component()
        self.url = reverse("component_update", kwargs={"pk": self.component.pk})

    def test_get_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_updates_component(self):
        self.client.force_login(self.user)
        data = {
            "title": "Updated Title",
            "category": self.component.category.pk,
            "sub_category": self.component.sub_category.pk,
            "brand": self.component.brand.pk,
            "package": self.component.package.pk,
            "quantity": 200,
            "price": "0.10",
        }
        self.client.post(self.url, data)
        self.component.refresh_from_db()
        self.assertEqual(self.component.title, "Updated Title")
        self.assertEqual(self.component.quantity, 200)

    def test_context_has_all_components_json(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn("all_components_json", response.context)
        json.loads(response.context["all_components_json"])  # valid JSON

    def test_context_has_existing_equivalents_json(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn("existing_equivalents_json", response.context)

    def test_anonymous_redirects(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")


# ---------------------------------------------------------------------------
# View tests — ComponentDeleteView
# ---------------------------------------------------------------------------


class ComponentDeleteViewTest(TestCase):
    def setUp(self):
        self.user = make_user(permissions=["delete_component"])
        self.component = make_component()
        self.url = reverse("component_delete", kwargs={"pk": self.component.pk})

    def test_get_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_deletes_component_and_redirects(self):
        self.client.force_login(self.user)
        pk = self.component.pk
        response = self.client.post(self.url)
        self.assertFalse(Component.objects.filter(pk=pk).exists())
        # Don't follow the redirect — the test user only has delete_component, not view_component
        self.assertRedirects(
            response, reverse("component_list"), fetch_redirect_response=False
        )

    def test_anonymous_redirects(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")


# ---------------------------------------------------------------------------
# View tests — load_subcategories AJAX
# ---------------------------------------------------------------------------


class LoadSubcategoriesViewTest(TestCase):
    def setUp(self):
        self.url = reverse("ajax_load_subcategories")
        self.category = Category.objects.create(name="Capacitor")
        self.sub1 = SubCategory.objects.create(
            name="Electrolytic", category=self.category
        )
        self.sub2 = SubCategory.objects.create(name="Ceramic", category=self.category)

    def test_returns_subcategories_for_valid_category(self):
        response = self.client.get(self.url, {"category_id": self.category.pk})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        ids = [item["id"] for item in data]
        self.assertIn(self.sub1.pk, ids)
        self.assertIn(self.sub2.pk, ids)

    def test_returns_empty_list_without_category_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_returns_empty_list_for_unknown_category(self):
        response = self.client.get(self.url, {"category_id": 99999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])


# ---------------------------------------------------------------------------
# Security — whitelist constants
# ---------------------------------------------------------------------------


class FilterWhitelistTest(SimpleTestCase):
    def test_allowed_filter_fields_are_frozenset(self):
        self.assertIsInstance(ALLOWED_FILTER_FIELDS, frozenset)

    def test_allowed_filter_lookups_are_frozenset(self):
        self.assertIsInstance(ALLOWED_FILTER_LOOKUPS, frozenset)

    def test_dangerous_fields_not_in_whitelist(self):
        for field in ("password", "is_superuser", "user__password", "created_at__year"):
            self.assertNotIn(
                field, ALLOWED_FILTER_FIELDS, f"{field!r} should be blocked"
            )

    def test_dangerous_lookups_not_in_whitelist(self):
        for lookup in ("regex", "iregex", "in", "range"):
            self.assertNotIn(
                lookup, ALLOWED_FILTER_LOOKUPS, f"{lookup!r} should be blocked"
            )


# ---------------------------------------------------------------------------
# Template tag tests (existing, preserved)
# ---------------------------------------------------------------------------


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
