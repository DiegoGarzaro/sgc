from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from components.models import Component
from packages.models import Package
from sub_categories.models import SubCategory
from suppliers.models import Supplier

from . import metrics

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_related():
    category = Category.objects.create(name="IC")
    sub_category = SubCategory.objects.create(name="Amplifier", category=category)
    brand = Brand.objects.create(name="TI")
    package = Package.objects.create(name="DIP8")
    return category, sub_category, brand, package


def make_component(title="LM358", quantity=50, price=Decimal("1.00"), **kwargs):
    category, sub_category, brand, package = make_related()
    return Component.objects.create(
        title=title,
        category=category,
        sub_category=sub_category,
        brand=brand,
        package=package,
        quantity=quantity,
        price=price,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Metrics tests
# ---------------------------------------------------------------------------


class GetComponentMetricsTest(TestCase):
    def test_returns_zeros_when_no_components(self):
        result = metrics.get_component_metrics()
        self.assertEqual(result["total_quantity"], 0)
        self.assertEqual(result["component_count"], 0)

    def test_counts_components_correctly(self):
        make_component(title="C1", quantity=10, price=Decimal("0.10"))
        make_component(title="C2", quantity=20, price=Decimal("0.20"))
        result = metrics.get_component_metrics()
        self.assertEqual(result["component_count"], 2)
        self.assertEqual(result["total_quantity"], 30)

    def test_total_price_calculated_in_db(self):
        make_component(title="C1", quantity=2, price=Decimal("3.00"))
        make_component(title="C2", quantity=5, price=Decimal("2.00"))
        result = metrics.get_component_metrics()
        # 2*3.00 + 5*2.00 = 6 + 10 = 16
        self.assertIn("16", result["total_price"])

    def test_handles_null_price(self):
        make_component(title="C1", quantity=10, price=None)
        # Should not raise
        result = metrics.get_component_metrics()
        self.assertEqual(result["component_count"], 1)


class GetSupplierMetricsTest(TestCase):
    def test_returns_zero_when_no_suppliers(self):
        result = metrics.get_supplier_metrics()
        self.assertEqual(result["supplier_count"], 0)

    def test_counts_suppliers(self):
        Supplier.objects.create(name="Mouser")
        Supplier.objects.create(name="Digikey")
        result = metrics.get_supplier_metrics()
        self.assertEqual(result["supplier_count"], 2)


class GetComponentQuantityTest(TestCase):
    def test_returns_dates_and_values_lists(self):
        result = metrics.get_component_quantity()
        self.assertIn("dates", result)
        self.assertIn("values", result)
        self.assertEqual(len(result["dates"]), 7)
        self.assertEqual(len(result["values"]), 7)

    def test_values_are_integers(self):
        result = metrics.get_component_quantity()
        for v in result["values"]:
            self.assertIsInstance(v, int)


class GetComponentQuantityPerCategoryTest(TestCase):
    def test_returns_empty_when_no_components(self):
        result = metrics.get_component_quantity_per_category()
        self.assertEqual(result["categories"], [])
        self.assertEqual(result["values"], [])

    def test_groups_by_category(self):
        make_component(title="C1", quantity=10)
        make_component(title="C2", quantity=5)
        result = metrics.get_component_quantity_per_category()
        self.assertGreater(len(result["categories"]), 0)
        total = sum(result["values"])
        self.assertEqual(total, 15)

    def test_ordered_by_quantity_descending(self):
        category_a = Category.objects.create(name="A")
        category_b = Category.objects.create(name="B")
        sub_a = SubCategory.objects.create(name="X", category=category_a)
        sub_b = SubCategory.objects.create(name="Y", category=category_b)
        brand = Brand.objects.create(name="BR")
        package = Package.objects.create(name="PKG")

        Component.objects.create(
            title="Low",
            category=category_a,
            sub_category=sub_a,
            brand=brand,
            package=package,
            quantity=5,
        )
        Component.objects.create(
            title="High",
            category=category_b,
            sub_category=sub_b,
            brand=brand,
            package=package,
            quantity=100,
        )
        result = metrics.get_component_quantity_per_category()
        self.assertGreaterEqual(result["values"][0], result["values"][-1])


class GetLowStockComponentsTest(TestCase):
    def setUp(self):
        self.low = make_component(title="Low", quantity=3)
        self.ok = make_component(title="OK", quantity=20)

    def test_returns_only_below_threshold(self):
        result = list(metrics.get_low_stock_components(threshold=10))
        self.assertIn(self.low, result)
        self.assertNotIn(self.ok, result)

    def test_default_threshold_is_10(self):
        result = list(metrics.get_low_stock_components())
        self.assertIn(self.low, result)

    def test_ordered_by_quantity_ascending(self):
        make_component(title="Very Low", quantity=1)
        result = list(metrics.get_low_stock_components(threshold=10))
        quantities = [c.quantity for c in result]
        self.assertEqual(quantities, sorted(quantities))

    def test_invalid_threshold_defaults_to_10(self):
        result = list(metrics.get_low_stock_components(threshold="bad"))
        self.assertIn(self.low, result)

    def test_select_related_avoids_n_plus_1(self):
        """Ensure brand and category are prefetched (no extra queries per row)."""
        result = metrics.get_low_stock_components(threshold=10)
        with self.assertNumQueries(1):
            for c in result:
                _ = c.brand.name
                _ = c.category.name


# ---------------------------------------------------------------------------
# Home view tests
# ---------------------------------------------------------------------------


class HomeViewTest(TestCase):
    def setUp(self):
        self.url = reverse("home")
        self.user = User.objects.create_user(username="tester", password="pass123")

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_authenticated_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_has_component_metrics(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn("component_metrics", response.context)

    def test_context_has_low_stock_threshold(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn("low_stock_threshold", response.context)
        self.assertEqual(response.context["low_stock_threshold"], 10)

    def test_custom_threshold_applied(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {"low_stock_threshold": "5"})
        self.assertEqual(response.context["low_stock_threshold"], 5)

    def test_invalid_threshold_defaults_to_10(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {"low_stock_threshold": "abc"})
        self.assertEqual(response.context["low_stock_threshold"], 10)

    def test_threshold_clamped_to_max_100(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, {"low_stock_threshold": "999"})
        self.assertEqual(response.context["low_stock_threshold"], 100)

    def test_ajax_request_returns_json(self):
        self.client.force_login(self.user)
        response = self.client.get(
            self.url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("html", data)

    def test_standard_thresholds_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn("standard_thresholds", response.context)
        self.assertIn(10, response.context["standard_thresholds"])


# ---------------------------------------------------------------------------
# CustomLoginView tests
# ---------------------------------------------------------------------------


class CustomLoginViewTest(TestCase):
    def setUp(self):
        self.url = reverse("login")
        self.active_user = User.objects.create_user(
            username="active", password="pass123", is_active=True
        )
        self.inactive_user = User.objects.create_user(
            username="inactive", password="pass123", is_active=False
        )

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_active_user_can_login(self):
        response = self.client.post(
            self.url, {"username": "active", "password": "pass123"}
        )
        self.assertRedirects(response, reverse("home"))

    def test_inactive_user_cannot_login(self):
        response = self.client.post(
            self.url, {"username": "inactive", "password": "pass123"}
        )
        # Django's ModelBackend rejects inactive users at authenticate() level,
        # so the form is invalid and the view returns 200 (stays on login page).
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get("_auth_user_id"))

    def test_wrong_password_fails(self):
        response = self.client.post(
            self.url, {"username": "active", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
