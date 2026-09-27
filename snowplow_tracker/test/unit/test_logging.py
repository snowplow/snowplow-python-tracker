# """
#     test_logging.py

#     Copyright (c) 2013-2023 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.
# """

import subprocess
import sys
import textwrap
import unittest


class TestLogging(unittest.TestCase):
    def test_import_preserves_application_logging(self) -> None:
        for configured in [False, True]:
            with self.subTest(configured=configured):
                result = subprocess.run(
                    [sys.executable, "-c", textwrap.dedent("""
                        import io
                        import logging
                        import sys

                        output = io.StringIO()
                        root = logging.getLogger()
                        assert not root.handlers
                        if sys.argv[1] == "True":
                            logging.basicConfig(stream=output, level=logging.ERROR)
                        handlers = root.handlers[:]
                        level = root.level

                        from snowplow_tracker import emitters, snowplow

                        assert root.handlers == handlers, root.handlers
                        assert root.level == level
                        if not handlers:
                            logging.basicConfig(stream=output, level=logging.WARNING)
                        emitters.logger.warning("emitter message")
                        snowplow.logger.warning("tracker message")
                        assert output.getvalue().splitlines() == [
                            "WARNING:snowplow_tracker.emitters:emitter message",
                            "WARNING:snowplow_tracker.snowplow:tracker message",
                        ], output.getvalue()
                    """), str(configured)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")
