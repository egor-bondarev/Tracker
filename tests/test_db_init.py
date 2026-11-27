"""Initialization failure handling without requiring a running database."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # tracker_db, as PYTHONPATH=/app provides it in the image
spec = importlib.util.spec_from_file_location('db_init', ROOT / 'record_service/src/create_db.py')
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

    @patch('alembic.command.upgrade')
    def test_migrations_run_to_head_as_application_role(self, upgrade):
        settings = self.settings()
        with patch.object(module.psycopg2, 'connect') as connect:
            module.run_migrations(settings)
        connect.return_value.close.assert_called_once()
        config, revision = upgrade.call_args.args
        self.assertEqual(revision, 'head')
        url = config.attributes['sqlalchemy.url']
        self.assertEqual((url.username, url.password, url.host, url.database),
                         ('tracker-user', "app'password", 'tracker_database', 'tracker'))
        self.assertNotIn("app'password", repr(url))
        self.assertTrue(Path(config.get_main_option('script_location'), 'env.py').is_file())

    @patch('alembic.command.upgrade', side_effect=RuntimeError('migration failed'))
    def test_failed_migration_propagates(self, upgrade):
        with patch.object(module.psycopg2, 'connect'):
            with self.assertRaisesRegex(RuntimeError, 'migration failed'):
                module.run_migrations(self.settings())

if __name__ == '__main__':
    unittest.main()
