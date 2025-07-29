# Copyright 2023 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from config_tempest.tests.base import BaseConfigTempestTest
from config_tempest import utils


class TestUtils(BaseConfigTempestTest):
    """Utils test class

    Tests for get_base_url method.
    """

    def setUp(self):
        super(TestUtils, self).setUp()
        self.fake_urls = [
            "http://10.200.16.10:8774",
            "http://10.200.16.10:5000/v3",
            "http://10.200.16.10/path",
            "http://10.200.16.10:8774/path",
            "http://10.200.16.10:8774/path/v2.1",
            "http://10.200.16.10:8774/path/v2/58f582e50641fead037e8e3f7ca59f",
        ]
        self.expected_base_urls = [
            "http://10.200.16.10:8774/",
            "http://10.200.16.10:5000/",
            "http://10.200.16.10/path/",
            "http://10.200.16.10:8774/path/",
            "http://10.200.16.10:8774/path/",
            "http://10.200.16.10:8774/path/",
        ]
        self.test_cases = zip(self.fake_urls, self.expected_base_urls)

    def test_get_base_url(self):
        for url, expected_base_url in self.test_cases:
            with self.subTest(url=url):
                base_url = utils.get_base_url(url)
                self.assertEqual(expected_base_url, base_url)
