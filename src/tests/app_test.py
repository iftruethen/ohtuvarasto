"""Tests for the Flask warehouse management application."""
import unittest
import app as app_module


class TestWarehouseApp(unittest.TestCase):
    """Test cases for warehouse management application."""

    def setUp(self):
        """Set up test client and clear warehouses before each test."""
        app_module.app.config["TESTING"] = True
        app_module.app.config["WTF_CSRF_ENABLED"] = False
        self.client = app_module.app.test_client()
        app_module.warehouses.clear()
        app_module.next_id = 1

    def test_index_empty(self):
        """Test index page with no warehouses."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No warehouses yet", response.data)

    def test_create_warehouse_get(self):
        """Test create warehouse form page."""
        response = self.client.get("/create")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Create New Warehouse", response.data)

    def test_create_warehouse_post(self):
        """Test creating a new warehouse."""
        response = self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Warehouse", response.data)
        self.assertEqual(len(app_module.warehouses), 1)

    def test_create_warehouse_without_name(self):
        """Test creating warehouse without name fails."""
        response = self.client.post("/create", data={
            "name": "",
            "capacity": "100",
            "initial_balance": "0"
        }, follow_redirects=True)
        self.assertIn(b"Name is required", response.data)
        self.assertEqual(len(app_module.warehouses), 0)

    def test_warehouse_details(self):
        """Test warehouse details page."""
        self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.client.get("/warehouse/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Warehouse", response.data)
        self.assertIn(b"100", response.data)
        self.assertIn(b"50", response.data)

    def test_warehouse_details_not_found(self):
        """Test warehouse details for non-existent warehouse."""
        response = self.client.get("/warehouse/999", follow_redirects=True)
        self.assertIn(b"Warehouse not found", response.data)

    def test_add_to_warehouse(self):
        """Test adding items to warehouse."""
        self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "0"
        })
        response = self.client.post("/warehouse/1/add", data={
            "amount": "25"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Added 25", response.data)
        self.assertEqual(app_module.warehouses[1]["varasto"].saldo, 25)

    def test_remove_from_warehouse(self):
        """Test removing items from warehouse."""
        self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.client.post("/warehouse/1/remove", data={
            "amount": "20"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Removed 20", response.data)
        self.assertEqual(app_module.warehouses[1]["varasto"].saldo, 30)

    def test_edit_warehouse_get(self):
        """Test edit warehouse form page."""
        self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.client.get("/warehouse/1/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Edit Warehouse", response.data)
        self.assertIn(b"Test Warehouse", response.data)

    def test_edit_warehouse_post(self):
        """Test editing a warehouse."""
        self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        })
        response = self.client.post("/warehouse/1/edit", data={
            "name": "Updated Warehouse",
            "capacity": "200",
            "balance": "75"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Updated Warehouse", response.data)
        self.assertEqual(app_module.warehouses[1]["name"], "Updated Warehouse")
        self.assertEqual(app_module.warehouses[1]["varasto"].tilavuus, 200)
        self.assertEqual(app_module.warehouses[1]["varasto"].saldo, 75)

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        self.client.post("/create", data={
            "name": "Test Warehouse",
            "capacity": "100",
            "initial_balance": "50"
        })
        self.assertEqual(len(app_module.warehouses), 1)
        response = self.client.post(
            "/warehouse/1/delete",
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"deleted successfully", response.data)
        self.assertEqual(len(app_module.warehouses), 0)

    def test_index_with_warehouses(self):
        """Test index page with warehouses."""
        self.client.post("/create", data={
            "name": "Warehouse 1",
            "capacity": "100",
            "initial_balance": "50"
        })
        self.client.post("/create", data={
            "name": "Warehouse 2",
            "capacity": "200",
            "initial_balance": "0"
        })
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Warehouse 1", response.data)
        self.assertIn(b"Warehouse 2", response.data)

    def test_varasto_rules_respected(self):
        """Test that Varasto rules are respected when editing."""
        # Create warehouse with capacity 100
        self.client.post("/create", data={
            "name": "Test",
            "capacity": "100",
            "initial_balance": "0"
        })
        # Try to set balance higher than capacity - Varasto should limit it
        self.client.post("/warehouse/1/edit", data={
            "name": "Test",
            "capacity": "100",
            "balance": "200"
        })
        # Balance should be limited to capacity
        self.assertEqual(app_module.warehouses[1]["varasto"].saldo, 100)
