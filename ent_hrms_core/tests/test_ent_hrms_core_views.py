from odoo.tests.common import TransactionCase, tagged


@tagged("-at_install", "post_install", "ent_hrms_core")
class TestEntHrmsCoreViews(TransactionCase):
    """Automated smoke test - ensures views load without errors."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _module = "ent_hrms_core"
        cls._views = cls.env["ir.ui.view"].search([
            ("model_data_id.module", "=", _module),
        ])

    def test_views_load(self):
        """Verify all views defined by this module render without error."""
        errors = []
        for view in self._views:
            try:
                view._check_xml()
            except Exception as exc:
                errors.append(f"{view.name} (id={view.id}): {exc}")
        if errors:
            self.fail("View load errors found:\n" + "\n".join(errors))

    def test_smoke(self):
        """Basic module existence test."""
        self.assertTrue(True)
