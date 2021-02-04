# -*- coding: utf-8 -*-
# Copyright 2021 The Matrix.org Foundation C.I.C.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest

from synapse.storage.engines.postgres import PostgresEngine
from synapse.storage.engines.sqlite import Sqlite3Engine

from . import create_user_directory_search_module_with_config


class UserDirectorySearchModuleTestCase(unittest.TestCase):
    def test_parse_config(self):
        """Test that parsing a config produces the expected ModuleConfig object."""
        user_config = {"weighted_display_name_like": "testabc [SoMeThInG]"}
        _, _, module_config = create_user_directory_search_module_with_config(
            user_config
        )

        # Check that the generated config contains what we expect
        self.assertEqual(
            module_config.weighted_display_name_like,
            user_config["weighted_display_name_like"],
        )

    def test_get_search_query_ordering(self):
        """Tests UserDirectorySearchModule.get_search_query_ordering return values"""
        user_config = {"weighted_display_name_like": "[Modernisation]"}

        module, _, _ = create_user_directory_search_module_with_config(user_config)

        # Check postgres

        # Check the generated SQL and arguments of the above config when using postgres
        sql, args = module.get_search_query_ordering(PostgresEngine)

        # We don't care too much about the specifics of the SQL, just that our injected
        # CASE is present
        self.assertIn("display_name like ?", sql.lower())

        # Check that the returned arguments match our config
        expected_args = ("%" + user_config["weighted_display_name_like"] + "%",)
        self.assertEqual(args, expected_args)

        # Check sqlite

        # Check the generated SQL and arguments of the above config when using postgres
        sql, args = module.get_search_query_ordering(Sqlite3Engine)

        # We don't do anything different from Synapse's default SQL
        self.assertGreater(len(sql), 0)

        # Nor do we return any extra arguments
        expected_args = ()
        self.assertEqual(args, expected_args)
