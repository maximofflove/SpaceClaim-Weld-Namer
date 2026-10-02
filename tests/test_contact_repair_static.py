# -*- coding: utf-8 -*-
"""Static source regression checks for v0.15.8 Contact repair routing.

These tests do not replace SpaceClaim/API V19 runtime validation.
"""
from __future__ import print_function
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(HERE), 'Weld_Namer.py')
with open(SOURCE, 'r') as stream:
    TEXT = stream.read()


class ContactRepairStaticTests(unittest.TestCase):
    def test_contact_validator_exists(self):
        self.assertIn('def validate_contact_named_selections(', TEXT)
        self.assertIn("r'^ctkt([1-9][0-9]*)([ab])$'", TEXT)

    def test_contact_repair_is_face_only(self):
        self.assertIn("if self.is_contact:\n            return 'Faces'", TEXT)

    def test_contact_manager_is_enabled(self):
        self.assertIn("else 'Contact Named Selection QA / Repair Manager' if purpose == CONTACT_MODE", TEXT)
        self.assertIn('self.manager.Enabled = True', TEXT)

    def test_contact_manager_uses_contact_highlight(self):
        self.assertIn('groups, items_count = highlight_contact_pair(context(), pair, False)', TEXT)

    def test_repair_target_supports_prefix(self):
        self.assertIn("def repair_target_name(record, side, prefix='w'):", TEXT)
        self.assertIn("return '%s%d%s' % (prefix, record['pair'], side)", TEXT)

    def test_shared_replace_verification_is_retained(self):
        self.assertIn('NamedSelection.Replace(actual, selection, Selection.Empty())', TEXT)
        self.assertIn('if expected_keys != verified_keys:', TEXT)

    def test_add_remove_buttons_still_route_to_shared_handler(self):
        self.assertIn("self.on_repair_side('a', 'add')", TEXT)
        self.assertIn("self.on_repair_side('b', 'add')", TEXT)
        self.assertIn("self.on_repair_side('a', 'remove')", TEXT)
        self.assertIn("self.on_repair_side('b', 'remove')", TEXT)


if __name__ == '__main__':
    unittest.main()
