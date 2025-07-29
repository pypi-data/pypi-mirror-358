# Copyright © 2020 Amazon Web Services
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import os
import mock
import requests
import responses

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.http_method import HttpMethod
from osdu_api.configuration.config_manager import DefaultConfigManager


class MockTokenRefresher(TokenRefresher):

    def refresh_token():
        """
        We need to define this method, because original TokenRefresher.refresh_token is abstract one.
        """
        return "stubbed"


class TestBaseClient(unittest.TestCase):

    def _create_mock_error_response(self, status_code = 400):
        mock_response_error = mock.Mock(spec=requests.Response)
        mock_response_error.ok = False
        mock_response_error.status_code = status_code
        mock_response_error.raise_for_status = mock.Mock(side_effect=requests.HTTPError)
        return mock_response_error

    @mock.patch.object(BaseClient, '_refresh_service_principal_token', return_value="stubbed")
    def test_init(self, mocked_token_method):
        # Arrange

        # Act
        client = BaseClient(config_manager=DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini'), data_partition_id="opendes")

        # Assert
        mocked_token_method.assert_called()

    @responses.activate
    @mock.patch.object(BaseClient, '_refresh_service_principal_token', return_value="stubbed")
    def test_make_request(self, mocked_token_method):
        # Arrange
        client = BaseClient(config_manager=DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini'), data_partition_id="opendes")
        client.service_principal_token = 'stubbed'
        responses.add(responses.PUT, 'http://stubbed', json={'response': 'true'}, status=200)

        # Act
        response = client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})

        # Assert
        mocked_token_method.assert_called()
        self.assertEqual(response.content, b'{"response": "true"}')

    @responses.activate
    @mock.patch.object(BaseClient, '_send_request_with_bearer_token', return_value="stubbed")
    def test_make_request_with_bearer(self, mocked_send_request):

        config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
        config_manager._parsed_config._sections["environment"]["use_service_principal"] = "False"

        client = BaseClient(config_manager=config_manager, data_partition_id="opendes")

        client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={}, bearer_token="subbed")
        mocked_send_request.assert_called()

    @responses.activate
    @mock.patch.object(BaseClient, '_send_request_with_principle_token', return_value="stubbed")
    @mock.patch.object(BaseClient, '_refresh_service_principal_token', return_value="stubbed")
    def test_make_request_with_principle(self, mocked_send_request, mocked_refresh_principle):

        config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
        config_manager._parsed_config._sections["environment"]["use_service_principal"] = "True"

        client = BaseClient(config_manager=config_manager, data_partition_id="opendes")
        client.service_principal_token = 'stubbed'

        client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})
        mocked_refresh_principle.assert_called()
        mocked_send_request.assert_called()

    @responses.activate
    @mock.patch.object(BaseClient, '_send_request_with_token_refresher', return_value="stubbed")
    def test_make_request_with_token_refresher(
        self,
        mocked_send_request,
    ):
        token_refresher = MockTokenRefresher()
        config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
        config_manager._parsed_config._sections["environment"]["use_service_principal"] = "False"

        client = BaseClient(config_manager=config_manager, data_partition_id="opendes", token_refresher=token_refresher)

        client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})
        mocked_send_request.assert_called()

    def test_make_request_with_token_refresher_retry(self):
        http_status_codes = (400, 503)

        for http_status_code in http_status_codes:
            with self.subTest(http_status_code=http_status_code):
                token_refresher = MockTokenRefresher()
                config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
                config_manager._parsed_config._sections["environment"]["use_service_principal"] = "False"
                client = BaseClient(config_manager=config_manager, data_partition_id="opendes", token_refresher=token_refresher)

                mock_response = self._create_mock_error_response(http_status_code)

                client._send_request = mock.Mock(side_effect=[mock_response, mock_response, mock_response, mock_response])

                response = client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})

                self.assertEqual(client._send_request.call_count, 3)
                self.assertEqual(response.status_code, http_status_code)

    def test_make_request_with_token_refresher_retry_second_request_is_ok(self):
        http_status_codes = (400, 503)

        for http_status_code in http_status_codes:
            with self.subTest(http_status_code=http_status_code):
                token_refresher = MockTokenRefresher()
                token_refresher.refresh_token = mock.Mock()
                config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
                config_manager._parsed_config._sections["environment"]["use_service_principal"] = "False"

                client = BaseClient(config_manager, "opendes", token_refresher=token_refresher)

                mock_response_error = self._create_mock_error_response(http_status_code)

                mock_response_ok = mock.Mock(spec=requests.Response)
                mock_response_ok.status_code = 200

                client._send_request = mock.Mock(side_effect=[mock_response_error, mock_response_ok])

                response = client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})

                token_refresher.refresh_token.assert_not_called()
                self.assertEqual(client._send_request.call_count, 2)
                self.assertEqual(response.status_code, 200)

    def test_make_request_with_token_refresher_retry_first_unauth_or_forbidden(self):
        http_status_codes = (401, 403)

        for http_status_code in http_status_codes:
            with self.subTest(http_status_code=http_status_code):
                token_refresher = MockTokenRefresher()
                token_refresher.refresh_token = mock.Mock()
                config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
                config_manager._parsed_config._sections["environment"]["use_service_principal"] = "False"

                client = BaseClient(config_manager, "opendes", token_refresher=token_refresher)

                mock_response_unauth = self._create_mock_error_response(http_status_code)
                mock_response_error = self._create_mock_error_response()
                mock_response_ok = mock.Mock(spec=requests.Response)
                mock_response_ok.status_code = 200

                client._send_request = mock.Mock(side_effect=[mock_response_unauth, mock_response_error, mock_response_ok])

                response = client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})

                token_refresher.refresh_token.assert_called_once()
                self.assertEqual(client._send_request.call_count, 3)
                self.assertEqual(response.status_code, 200)

    def test_make_request_with_token_refresher_retry_all_unauth_or_forbidden(self):
        http_status_codes = (401, 403)

        for http_status_code in http_status_codes:
            with self.subTest(http_status_code=http_status_code):
                token_refresher = MockTokenRefresher()
                token_refresher.refresh_token = mock.Mock()
                config_manager = DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini')
                config_manager._parsed_config._sections["environment"]["use_service_principal"] = "False"

                client = BaseClient(config_manager, "opendes", token_refresher=token_refresher)

                mock_response_unauth = self._create_mock_error_response(http_status_code)

                client._send_request = mock.Mock(side_effect=[mock_response_unauth, mock_response_unauth, mock_response_unauth])

                response = client.make_request(method=HttpMethod.PUT, url='http://stubbed', data={})

                token_refresher.refresh_token.assert_called_once()
                self.assertEqual(client._send_request.call_count, 2)
                self.assertEqual(response.status_code, http_status_code)
