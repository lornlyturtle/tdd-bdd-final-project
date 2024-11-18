# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHES)

        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHES)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_find_product_or_read_product(self):
        """It should Create a product, add to database, then Read from database"""
        product = ProductFactory()
        product.print()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_product_error(self):
        """It should test error thrown when update product without id"""
        product = ProductFactory()
        product.print()
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_update_product(self):
        """It should Update a product"""
        product = ProductFactory()
        product.print()
        product.id = None
        product.create()
        product.print()
        orig_id = product.id
        self.assertIsNotNone(orig_id)
        new_description = "The quick brown fox jumped over the lazy dogs."
        product.description = new_description
        product.update()
        # Ensure we've updated local instance
        self.assertEqual(product.id, orig_id)
        self.assertEqual(product.description, new_description)
        # Ensure product in database has been updated too
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.description, new_description)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_delete_product(self):
        """It should Delete a product"""
        # Create a product and store in the database
        product = ProductFactory()
        product.create()
        # Check the database only contains one item
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Remove the product
        product.delete()
        # Check the database is empty
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all a product"""
        # Start with no products in the database
        products = Product.all()
        self.assertEqual(len(products), 0)
        num_prod_to_add = 5
        for _ in range(num_prod_to_add):
            product = ProductFactory()
            product.create()
        # Check the database contains five items
        products = Product.all()
        self.assertEqual(len(products), num_prod_to_add)

    def test_find_product_by_name(self):
        """It should find a product by name"""
        num_prod_to_add = 5
        for _ in range(num_prod_to_add):
            product = ProductFactory()
            product.create()
        products = Product.all()
        first_product_name = products[0].name
        # Check how many times the name of the first
        # product appears in the list of all products
        num_products_with_same_name = 0
        for prod in products:
            print("current prod: " + prod.name)
            if prod.name == first_product_name:
                print("found a match for " + first_product_name)
                num_products_with_same_name = num_products_with_same_name + 1
            else:
                print("no match: " + prod.name + " is not " + first_product_name)
        # use find_by_name
        found_product_list = Product.find_by_name(first_product_name)
        self.assertEqual(num_products_with_same_name, found_product_list.count())

    def test_find_product_by_availability(self):
        """It should find a product by availability"""
        num_prod_to_add = 10
        for _ in range(num_prod_to_add):
            product = ProductFactory()
            product.create()
        products = Product.all()
        first_product_avail = products[0].available
        # Check how many times the availability of the first
        # product appears in the list of all products
        num_products_with_same_avail = 0
        for prod in products:
            print("current prod: " + prod.name)
            if prod.available == first_product_avail:
                print("found a match for " + str(first_product_avail))
                num_products_with_same_avail = num_products_with_same_avail + 1
            else:
                print("no match: " + prod.name + " is not " + str(first_product_avail))
        # use find_by_name
        found_product_list = Product.find_by_availability(first_product_avail)
        self.assertEqual(num_products_with_same_avail, found_product_list.count())
        for prod in found_product_list:
            self.assertEqual(prod.available, first_product_avail)

    def test_find_product_by_category(self):
        """It should find a product by category"""
        num_prod_to_add = 10
        for _ in range(num_prod_to_add):
            product = ProductFactory()
            product.create()
        products = Product.all()
        first_product_cat = products[0].category
        # Check how many times the availability of the first
        # product appears in the list of all products
        num_products_with_same_cat = 0
        for prod in products:
            print("current prod: " + prod.name)
            if prod.category == first_product_cat:
                print("found a match for " + str(first_product_cat))
                num_products_with_same_cat = num_products_with_same_cat + 1
            else:
                print("no match: " + prod.name + " is not " + str(first_product_cat) + ", it is: " + str(prod.category))
        # use find_by_name
        found_product_list = Product.find_by_category(first_product_cat)
        self.assertEqual(num_products_with_same_cat, found_product_list.count())
        for prod in found_product_list:
            self.assertEqual(prod.category, first_product_cat)

    def test_find_product_by_price(self):
        """It should find a product by price"""
        num_prod_to_add = 5
        for _ in range(num_prod_to_add):
            product = ProductFactory()
            product.create()
        products = Product.all()
        first_product_price = products[0].price
        # Check how many times the name of the first
        # product appears in the list of all products
        num_products_with_same_price = 0
        for prod in products:
            print("current prod: " + prod.name)
            if prod.price == first_product_price:
                num_products_with_same_price += 1
        # use find_by_name
        found_product_list = Product.find_by_price(first_product_price)
        self.assertIsNotNone(num_products_with_same_price)
        self.assertEqual(num_products_with_same_price, found_product_list.count())
        # Set second product price to integer for code coverage
        products[1].price = 30
        products[1].update()
        found_product_list = Product.find_by_price("30 ")
        self.assertEqual(1, found_product_list.count())
        self.assertEqual(products[1].price, found_product_list[0].price)
