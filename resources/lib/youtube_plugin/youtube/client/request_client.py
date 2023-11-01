# -*- coding: utf-8 -*-
"""

    Copyright (C) 2023-present plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from ...kodion.utils.requests import BaseRequestsClass
from ...youtube.youtube_exceptions import YouTubeException


class YouTubeRequestClient(BaseRequestsClass):
    CLIENTS = {
        # 4k no VP9 HDR
        # Limited subtitle availability
        'android_testsuite': {
            '_id': 30,
            '_query_subtitles': True,
            'json': {
                'params': '2AMBCgIQBg',
                'context': {
                    'client': {
                        'clientName': 'ANDROID_TESTSUITE',
                        'clientVersion': '1.9',
                        'androidSdkVersion': '29',
                        'osName': 'Android',
                        'osVersion': '10',
                        'platform': 'MOBILE',
                    },
                },
            },
            'headers': {
                'User-Agent': ('com.google.android.youtube/'
                               '{json[context][client][clientVersion]}'
                               ' (Linux; U; {json[context][client][osName]}'
                               ' {json[context][client][osVersion]};'
                               ' {json[context][client][gl]}) gzip'),
                'X-YouTube-Client-Name': '{_id}',
                'X-YouTube-Client-Version': '{json[context][client][clientVersion]}',
            },
            'params': {
                'key': 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w',
            },
        },
        'android': {
            '_id': 3,
            'json': {
                'params': '2AMBCgIQBg',
                'context': {
                    'client': {
                        'clientName': 'ANDROID',
                        'clientVersion': '17.31.35',
                        'androidSdkVersion': '30',
                        'osName': 'Android',
                        'osVersion': '11',
                        'platform': 'MOBILE',
                    },
                },
            },
            'headers': {
                'User-Agent': ('com.google.android.youtube/'
                               '{json[context][client][clientVersion]}'
                               ' (Linux; U; {json[context][client][osName]}'
                               ' {json[context][client][osVersion]};'
                               ' {json[context][client][gl]}) gzip'),
                'X-YouTube-Client-Name': '{_id}',
                'X-YouTube-Client-Version': '{json[context][client][clientVersion]}',
            },
            'params': {
                'key': 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w',
            },
        },
        # Only for videos that allow embedding
        # Limited to 720p on some videos
        'android_embedded': {
            '_id': 55,
            'json': {
                'params': '2AMBCgIQBg',
                'context': {
                    'client': {
                        'clientName': 'ANDROID_EMBEDDED_PLAYER',
                        'clientVersion': '17.36.4',
                        'clientScreen': 'EMBED',
                        'androidSdkVersion': '29',
                        'osName': 'Android',
                        'osVersion': '10',
                        'platform': 'MOBILE',
                    },
                },
                'thirdParty': {
                    'embedUrl': 'https://www.youtube.com/embed/{json[videoId]}',
                },
            },
            'headers': {
                'User-Agent': ('com.google.android.youtube/'
                               '{json[context][client][clientVersion]}'
                               ' (Linux; U; {json[context][client][osName]}'
                               ' {json[context][client][osVersion]};'
                               ' {json[context][client][gl]}) gzip'),
                'X-YouTube-Client-Name': '{_id}',
                'X-YouTube-Client-Version': '{json[context][client][clientVersion]}',
            },
            'params': {
                'key': 'AIzaSyCjc_pVEDi4qsv5MtC2dMXzpIaDoRFLsxw',
            },
        },
        # 4k with HDR
        # Some videos block this client, may also require embedding enabled
        # Limited subtitle availability
        'android_youtube_tv': {
            '_id': 29,
            '_query_subtitles': True,
            'json': {
                'params': '2AMBCgIQBg',
                'context': {
                    'client': {
                        'clientName': 'ANDROID_UNPLUGGED',
                        'clientVersion': '6.36',
                        'androidSdkVersion': '29',
                        'osName': 'Android',
                        'osVersion': '10',
                        'platform': 'MOBILE',
                    },
                },
            },
            'headers': {
                'User-Agent': ('com.google.android.apps.youtube.unplugged/'
                               '{json[context][client][clientVersion]}'
                               ' (Linux; U; {json[context][client][osName]}'
                               ' {json[context][client][osVersion]};'
                               ' {json[context][client][gl]}) gzip'),
                'X-YouTube-Client-Name': '{_id}',
                'X-YouTube-Client-Version': '{json[context][client][clientVersion]}',
            },
            'params': {
                'key': 'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w',
            },
        },
        'ios': {
            '_id': 5,
            'json': {
                'context': {
                    'client': {
                        'clientName': 'IOS',
                        'clientVersion': '17.33.2',
                        'deviceModel': 'iPhone14,3',
                        'osName': 'iOS',
                        'osVersion': '15_6',
                        'platform': 'MOBILE',
                    },
                },
            },
            'headers': {
                'User-Agent': ('com.google.ios.youtube/'
                               '{json[context][client][clientVersion]}'
                               ' ({json[context][client][deviceModel]};'
                               ' U; CPU {json[context][client][osName]}'
                               ' {json[context][client][osVersion]}'
                               ' like Mac OS X)'),
                'X-YouTube-Client-Name': '{_id}',
                'X-YouTube-Client-Version': '{json[context][client][clientVersion]}',
            },
            'params': {
                'key': 'AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc',
            },
        },
        # Used to requests captions for clients that don't provide them
        # Requires handling of nsig to overcome throttling (TODO)
        'smarttv_embedded': {
            '_id': 85,
            'json': {
                'params': '2AMBCgIQBg',
                'context': {
                    'client': {
                        'clientName': 'TVHTML5_SIMPLY_EMBEDDED_PLAYER',
                        'clientScreen': 'WATCH',
                        'clientVersion': '2.0',
                    },
                },
                'thirdParty': {
                    'embedUrl': 'https://www.youtube.com',
                },
            },
            # Headers from a 2022 Samsung Tizen 6.5 based Smart TV
            'headers': {
                'User-Agent': ('Mozilla/5.0 (SMART-TV; LINUX; Tizen 6.5)'
                               ' AppleWebKit/537.36 (KHTML, like Gecko)'
                               ' 85.0.4183.93/6.5 TV Safari/537.36'),
            },
            'params': {
                'key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
            },
        },
        # Used for misc api requests by default
        # Requires handling of nsig to overcome throttling (TODO)
        'web': {
            '_id': 1,
            'json': {
                'context': {
                    'client': {
                        'clientName': 'WEB',
                        'clientVersion': '2.20220801.00.00',
                    },
                },
            },
            # Headers for a "Galaxy S20 Ultra" from Chrome dev tools device
            # emulation
            'headers': {
                'User-Agent': ('Mozilla/5.0 (Linux; Android 10; SM-G981B)'
                               ' AppleWebKit/537.36 (KHTML, like Gecko)'
                               ' Chrome/80.0.3987.162 Mobile Safari/537.36'),
                'Referer': 'https://www.youtube.com/watch?v={json[videoId]}'
            },
            'params': {
                'key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',
            },
        },
        '_common': {
            '_access_token': None,
            'json': {
                'contentCheckOk': True,
                'context': {
                    'client': {
                        'gl': None,
                        'hl': None,
                    },
                },
                'playbackContext': {
                    'contentPlaybackContext': {
                        'html5Preference': 'HTML5_PREF_WANTS',
                    },
                },
                'racyCheckOk': True,
                'thirdParty': {},
                'user': {
                    'lockedSafetyMode': False
                },
                'videoId': None,
            },
            'headers': {
                'Origin': 'https://www.youtube.com',
                'Referer': 'https://www.youtube.com/watch?v={json[videoId]}',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Authorization': 'Bearer {_access_token}',
            },
            'params': {
                'key': None,
                'prettyPrint': 'false'
            },
        },
    }

    def __init__(self, context):
        super(YouTubeRequestClient, self).__init__(
            context=context, exc_type=YouTubeException
        )

    @staticmethod
    def json_traverse(json_data, path):
        if not json_data or not path:
            return None

        result = json_data
        for keys in path:
            is_dict = isinstance(result, dict)
            if not is_dict and not isinstance(result, list):
                return None

            if not isinstance(keys, (list, tuple)):
                keys = [keys]
            for key in keys:
                if is_dict:
                    if key not in result:
                        continue
                elif not isinstance(key, int) or len(result) <= key:
                    continue
                result = result[key]
                break
            else:
                return None

        if result == json_data:
            return None
        return result

    def build_client(self, client_name, auth_header=False):
        def _merge_dicts(item1, item2, _=Ellipsis):
            if not isinstance(item1, dict) or not isinstance(item2, dict):
                return item1 if item2 is _ else item2
            new = {}
            keys = set(item1)
            keys.update(item2)
            for key in keys:
                value = _merge_dicts(item1.get(key, _), item2.get(key, _))
                if value is _:
                    continue
                if isinstance(value, str) and '{' in value:
                    _format['{0}.{1}'.format(id(new), key)] = (new, key, value)
                new[key] = value
            return new or _
        _format = {}

        client = (self.CLIENTS.get(client_name) or self.CLIENTS['web']).copy()
        client = _merge_dicts(self.CLIENTS['_common'], client)

        client['json']['videoId'] = self.video_id
        if auth_header and self._access_token:
            client['_access_token'] = self._access_token
            client['params'] = None
        elif 'Authorization' in client['headers']:
            del client['headers']['Authorization']

        for values, key, value in _format.values():
            if key in values:
                values[key] = value.format(**client)

        return client
