"""Initialization failure handling without requiring a running database."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

spec = importlib.util.spec_from_file_location(
    'db_init', Path(__file__).resolve().parents[1] / 'record_service/src/create_db.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InitializationTests(unittest.TestCase):
    def settings(self):
        return module.Settings(
            _env_file=None, database_admin='admin', database_admin_password='admin-secret',
            database_default_name='postgres', database_host='tracker_database',
            database_port=5432, database_name='tracker', database_user='tracker-user',
            database_password="app'password",
        )

    @patch.object(module.psycopg2, 'connect')
    def test_application_connection_uses_internal_address_and_app_credentials(self, connect):
        self.settings().get_connection(module.ConnectionRole.user)
        connect.assert_called_once_with(
            dbname='tracker', user='tracker-user', password="app'password",
            host='tracker_database', port=5432, connect_timeout=5,
        )

    @patch.object(module.time, 'sleep')
    @patch.object(module.psycopg2, 'connect', side_effect=module.psycopg2.OperationalError('secret'))
    def test_connection_failure_is_bounded_and_does_not_disclose_credentials(self, connect, sleep):
        with self.assertRaisesRegex(RuntimeError, 'after 10 attempts') as caught:
            self.settings().get_connection(module.ConnectionRole.admin)
        self.assertNotIn('secret', str(caught.exception))
        self.assertEqual(connect.call_count, 10)
        self.assertEqual(sleep.call_count, 9)

    def test_existing_database_and_role_are_not_modified(self):
        settings = MagicMock()
        settings.database_user = 'tracker'
        settings.database_name = 'tracker'
        connection = settings.get_connection.return_value
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.side_effect = [(1,), (1,)]
        module.create_database(settings)
        self.assertEqual(cursor.execute.call_count, 2)
        for call in cursor.execute.call_args_list:
            self.assertTrue(call.args[0].startswith('SELECT'))
        connection.close.assert_called_once()

    def test_failed_schema_creation_closes_connection_and_propagates(self):
        settings = MagicMock()
        connection = settings.get_connection.return_value
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.execute.side_effect = RuntimeError('schema failed')
        with self.assertRaisesRegex(RuntimeError, 'schema failed'):
            module.create_tables(settings)
        connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
