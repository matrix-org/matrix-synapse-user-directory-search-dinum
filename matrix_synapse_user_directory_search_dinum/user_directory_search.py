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
import logging
from typing import Dict, Optional, Tuple

import attr

from synapse.module_api import ModuleApi
from synapse.storage.engines import BaseDatabaseEngine
from synapse.storage.engines.postgres import PostgresEngine
from synapse.storage.engines.sqlite import Sqlite3Engine

logger = logging.getLogger(__name__)


@attr.s
class ModuleConfig(object):
    weighted_display_name_like = attr.ib(type=Optional[str], default=None)


class UserDirectorySearchModule:
    """Allows server admins to provide a Python module that augments the results of a
    user directory search.
    """

    def __init__(self, config: ModuleConfig, module_api: ModuleApi):
        self.weighted_display_name_like = config.weighted_display_name_like

    @staticmethod
    def parse_config(config: Dict) -> ModuleConfig:
        """Parse the dict provided by the homeserver's config
        Args:
            config: A dictionary containing configuration options for this provider
        Returns:
            A custom config object for this module
        """
        return ModuleConfig(
            weighted_display_name_like=config.get("weighted_display_name_like")
        )

    def get_search_query_ordering(
        self, database_engine_type: BaseDatabaseEngine
    ) -> Tuple[str, Tuple]:
        """Returns the contents of the ORDER BY section of the user directory search
        query. The full query can be found in UserDirectoryStore.

        Args:
            database_engine_type: The type of database engine that is in use. One of
                those in synapse/storage/engines/*.
                Ex. synapse.storage.engines.PostgresEngine

        Returns:
            A tuple containing:

            * A string that can be placed after ORDER BY in order to influence the
              ordering of results from a user directory search.
            * A tuple containing any extra arguments to provide to the query.
        """
        if database_engine_type == PostgresEngine:
            # We order by rank and then if a user has profile info.
            # This ranking algorithm is hand tweaked for "best" results. Broadly
            # the idea is that a higher weight is given to exact matches.
            # The array of numbers are the weights for the various part of the
            # search: (domain, _, display name, localpart)
            sql = """
                (CASE WHEN d.user_id IS NOT NULL THEN 4.0 ELSE 1.0 END)
            """

            args = ()
            if self.weighted_display_name_like is not None:
                sql += """\
    * (CASE WHEN display_name LIKE ? THEN 2.0 ELSE 1.0 END)\
                """
                args += ("%" + self.weighted_display_name_like + "%",)

            sql += """
                * (CASE WHEN avatar_url IS NOT NULL THEN 1.2 ELSE 1.0 END)
                * (
                    3 * ts_rank_cd(
                        '{0.1, 0.1, 0.9, 1.0}',
                        vector,
                        to_tsquery('simple', ?),
                        8
                    )
                    + ts_rank_cd(
                        '{0.1, 0.1, 0.9, 1.0}',
                        vector,
                        to_tsquery('simple', ?),
                        8
                    )
                )
                DESC,
                display_name IS NULL,
                avatar_url IS NULL
            """
            return sql, args
        elif database_engine_type == Sqlite3Engine:
            # We order by rank and then if a user has profile info.
            return (
                """
                rank(matchinfo(user_directory_search)) DESC,
                display_name IS NULL,
                avatar_url IS NULL
            """,
                (),
            )
        else:
            raise Exception("Received an unrecognized database engine")
