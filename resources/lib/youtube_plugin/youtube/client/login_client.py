# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import time
from urllib.parse import parse_qsl

from requests.exceptions import InvalidJSONError

from .request_client import YouTubeRequestClient
from ...youtube.youtube_exceptions import (
    InvalidGrant,
    LoginException,
    YouTubeException,
)
from .__config__ import (
    api,
    developer_keys,
    keys_changed,
    youtube_tv,
)


class LoginClient(YouTubeRequestClient):
    api_keys_changed = keys_changed

    CONFIGS = {
        'youtube-tv': {
            'system': 'YouTube TV',
            'key': youtube_tv['key'],
            'id': youtube_tv['id'],
            'secret': youtube_tv['secret']
        },
        'main': {
            'system': 'All',
            'key': api['key'],
            'id': api['id'],
            'secret': api['secret']
        },
        'developer': developer_keys
    }

    def __init__(self, context, config=None, language='en-US', region='',
                 access_token='', access_token_tv=''):
        self._context = context

        self._config = self.CONFIGS['main'] if config is None else config
        self._config_tv = self.CONFIGS['youtube-tv']
        # the default language is always en_US (like YouTube on the WEB)
        if not language:
            language = 'en_US'
        language = language.replace('-', '_')
        self._language = language
        self._region = region

        self._access_token = access_token
        self._access_token_tv = access_token_tv

        self._log_error_callback = None

        super(LoginClient, self).__init__(context=context)

    @staticmethod
    def _login_json_hook(response):
        json_data = None
        try:
            json_data = response.json()
            if 'error' in json_data:
                raise YouTubeException('"error" in response JSON data',
                                       json_data=json_data,
                                       response=response,)
        except ValueError as error:
            raise InvalidJSONError(error, response=response)
        response.raise_for_status()
        return json_data

    @staticmethod
    def _login_error_hook(error, response):
        json_data = getattr(error, 'json_data', None)
        if not json_data:
            return None, None, None, None, LoginException
        if json_data['error'] == 'authorization_pending':
            return None, None, json_data, False, False
        if (json_data['error'] == 'invalid_grant'
                and json_data.get('code') == '400'):
            return None, None, json_data, False, InvalidGrant(json_data)
        return None, None, json_data, False, LoginException(json_data)

    def set_log_error(self, callback):
        self._log_error_callback = callback

    def log_error(self, text):
        if self._log_error_callback:
            self._log_error_callback(text)
        else:
            print(text)

    def verify(self):
        return self._verify

    def set_access_token(self, access_token=''):
        self._access_token = access_token

    def set_access_token_tv(self, access_token_tv=''):
        self._access_token_tv = access_token_tv

    def revoke(self, refresh_token):
        # https://developers.google.com/youtube/v3/guides/auth/devices
        headers = {'Host': 'accounts.google.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        post_data = {'token': refresh_token}

        self.request('https://accounts.google.com/o/oauth2/revoke',
            method='POST', data=post_data, headers=headers,
            response_hook=self._login_json_hook,
            error_hook=self._login_error_hook,
            error_title='Logout Failed',
            error_info='Revoke failed: {exc}',
            raise_exc=LoginException
        )

    def refresh_token_tv(self, refresh_token):
        client_id = str(self.CONFIGS['youtube-tv']['id'])
        client_secret = str(self.CONFIGS['youtube-tv']['secret'])
        return self.refresh_token(refresh_token, client_id=client_id, client_secret=client_secret)

    def refresh_token(self, refresh_token, client_id='', client_secret=''):
        # https://developers.google.com/youtube/v3/guides/auth/devices
        headers = {'Host': 'www.googleapis.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        client_id = client_id or self._config['id']
        client_secret = client_secret or self._config['secret']
        post_data = {'client_id': client_id,
                     'client_secret': client_secret,
                     'refresh_token': refresh_token,
                     'grant_type': 'refresh_token'}

        config_type = self._get_config_type(client_id, client_secret)
        client_summary = ''.join([
            '(config_type: |', config_type, '|',
            ' client_id: |', client_id[:5], '...|',
            ' client_secret: |', client_secret[:5], '...|)'
        ])
        self._context.log_debug('Refresh token for ' + client_summary)

        json_data = self.request('https://www.googleapis.com/oauth2/v4/token',
            method='POST', data=post_data, headers=headers,
            response_hook=self._login_json_hook,
            error_hook=self._login_error_hook,
            error_title='Login Failed',
            error_info='Refresh failed for ' + client_summary + ': {exc}',
            raise_exc=LoginException
        )

        if json_data:
            access_token = json_data['access_token']
            expires_in = time.time() + int(json_data.get('expires_in', 3600))
            return access_token, expires_in
        return '', ''

    def request_access_token_tv(self, code, client_id='', client_secret=''):
        client_id = client_id or self.CONFIGS['youtube-tv']['id']
        client_secret = client_secret or self.CONFIGS['youtube-tv']['secret']
        return self.request_access_token(code, client_id=client_id, client_secret=client_secret)

    def request_access_token(self, code, client_id='', client_secret=''):
        # https://developers.google.com/youtube/v3/guides/auth/devices
        headers = {'Host': 'www.googleapis.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        client_id = client_id or self._config['id']
        client_secret = client_secret or self._config['secret']
        post_data = {'client_id': client_id,
                     'client_secret': client_secret,
                     'code': code,
                     'grant_type': 'http://oauth.net/grant_type/device/1.0'}

        config_type = self._get_config_type(client_id, client_secret)
        client_summary = ''.join([
            '(config_type: |', config_type, '|',
            ' client_id: |', client_id[:5], '...|',
            ' client_secret: |', client_secret[:5], '...|)'
        ])
        self._context.log_debug('Requesting access token for ' + client_summary)

        json_data = self.request('https://www.googleapis.com/oauth2/v4/token',
            method='POST', data=post_data, headers=headers,
            response_hook=self._login_json_hook,
            error_hook=self._login_error_hook,
            error_title='Login Failed',
            error_info='Access token request failed for ' + client_summary + ': {exc}',
            raise_exc=LoginException('Login Failed: Unknown response')
        )
        return json_data

    def request_device_and_user_code_tv(self):
        client_id = str(self.CONFIGS['youtube-tv']['id'])
        return self.request_device_and_user_code(client_id=client_id)

    def request_device_and_user_code(self, client_id=''):
        # https://developers.google.com/youtube/v3/guides/auth/devices
        headers = {'Host': 'accounts.google.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded'}

        client_id = client_id or self._config['id']
        post_data = {'client_id': client_id,
                     'scope': 'https://www.googleapis.com/auth/youtube'}

        config_type = self._get_config_type(client_id)
        client_summary = ''.join([
            '(config_type: |', config_type, '|',
            ' client_id: |', client_id[:5], '...|)',
        ])
        self._context.log_debug('Requesting device and user code for ' + client_summary)

        json_data = self.request('https://accounts.google.com/o/oauth2/device/code',
            method='POST', data=post_data, headers=headers,
            response_hook=self._login_json_hook,
            error_hook=self._login_error_hook,
            error_title='Login Failed',
            error_info='Requesting device and user code failed for ' + client_summary + ': {exc}',
            raise_exc=LoginException('Login Failed: Unknown response')
        )
        return json_data

    def get_access_token(self):
        return self._access_token

    def authenticate(self, username, password):
        headers = {'device': '38c6ee9a82b8b10a',
                   'app': 'com.google.android.youtube',
                   'User-Agent': 'GoogleAuth/1.4 (GT-I9100 KTU84Q)',
                   'content-type': 'application/x-www-form-urlencoded',
                   'Host': 'android.clients.google.com',
                   'Connection': 'Keep-Alive',
                   'Accept-Encoding': 'gzip'}

        post_data = {'device_country': self._region.lower(),
                     'operatorCountry': self._region.lower(),
                     'lang': self._language.replace('-', '_'),
                     'sdk_version': '19',
                     # 'google_play_services_version': '6188034',
                     'accountType': 'HOSTED_OR_GOOGLE',
                     'Email': username.encode('utf-8'),
                     'service': 'oauth2:https://www.googleapis.com/auth/youtube '
                                'https://www.googleapis.com/auth/youtube.force-ssl '
                                'https://www.googleapis.com/auth/plus.me '
                                'https://www.googleapis.com/auth/emeraldsea.mobileapps.doritos.cookie '
                                'https://www.googleapis.com/auth/plus.stream.read '
                                'https://www.googleapis.com/auth/plus.stream.write '
                                'https://www.googleapis.com/auth/plus.pages.manage '
                                'https://www.googleapis.com/auth/identity.plus.page.impersonation',
                     'source': 'android',
                     'androidId': '38c6ee9a82b8b10a',
                     'app': 'com.google.android.youtube',
                     # 'client_sig': '24bb24c05e47e0aefa68a58a766179d9b613a600',
                     'callerPkg': 'com.google.android.youtube',
                     # 'callerSig': '24bb24c05e47e0aefa68a58a766179d9b613a600',
                     'Passwd': password.encode('utf-8')}

        result = self.request('https://android.clients.google.com/auth',
            method='POST', data=post_data, headers=headers,
            error_title='Login Failed',
            raise_exc=LoginException
        )

        lines = result.text.replace('\n', '&')
        params = dict(parse_qsl(lines))
        token = params.get('Auth', '')
        expires = int(params.get('Expiry', -1))
        if not token or expires == -1:
            raise LoginException('Failed to get token')

        return token, expires

    def _get_config_type(self, client_id, client_secret=None):
        """used for logging"""
        if client_secret is None:
            using_conf_tv = (client_id == self.CONFIGS['youtube-tv'].get('id'))
            using_conf_main = (client_id == self.CONFIGS['main'].get('id'))
        else:
            using_conf_tv = ((client_id == self.CONFIGS['youtube-tv'].get('id')) and (client_secret == self.CONFIGS['youtube-tv'].get('secret')))
            using_conf_main = ((client_id == self.CONFIGS['main'].get('id')) and (client_secret == self.CONFIGS['main'].get('secret')))
        if not using_conf_main and not using_conf_tv:
            return 'None'
        if using_conf_tv:
            return 'YouTube-TV'
        if using_conf_main:
            return 'YouTube-Kodi'
        return 'Unknown'
