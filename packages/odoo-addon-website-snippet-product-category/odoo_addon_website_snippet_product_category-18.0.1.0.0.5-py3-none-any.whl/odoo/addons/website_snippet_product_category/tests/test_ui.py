# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import odoo.tests
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestUi(odoo.tests.HttpCase):
    def test_admin_tour_marginless_gallery(self):
        self.start_tour(
            self.env["website"].get_client_action_url("/"),
            "product_category",
            login="admin",
        )
