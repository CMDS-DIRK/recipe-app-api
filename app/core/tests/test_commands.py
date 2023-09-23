"""Test custom Django management commands."""

# to mock the behavior of the database,
# need to be able to simulate if the database is returning response
from unittest.mock import patch

# can be one of the errors that occurs when django is trying to
# connect before db is ready
from psycopg2 import OperationalError as Psycopg2Error

# helper function provided by django, will help to call the command for testing
from django.core.management import call_command
# another possible error depending on the startup phase the database is in
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database until database is ready to accept connections.
        It tests the situation where the database is ready and also checks
        if the command is set up correctly. """
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError"""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
