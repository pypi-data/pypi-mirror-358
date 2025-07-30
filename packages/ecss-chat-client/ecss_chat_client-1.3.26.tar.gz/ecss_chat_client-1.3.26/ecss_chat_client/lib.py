from urllib.request import Request

import urllib3

urllib3.disable_warnings()


class Base():
    def __init__(self, client):
        self.client = client
        self.short_url = client.short_url
        self.settings = client.settings
        self.proto = client.proto
        self.verify = client.verify
        self.server = client.server
        self.port = client.port
        self.tus_header_keys = [
            'Upload-Metadata',
            'Content-Length',
            'Upload-Offset',
            'Tus-Resumable',
            'Upload-Length',
            'Content-Type',
        ]

    def _make_request(
            self,
            endpoint,
            payload=None,
            params=None,
            method='post',
            files=None,
            short_path=False,
            tus_path=False,
    ) -> Request:
        if tus_path is True:
            url = f'{self.proto}://{self.server}/{endpoint}'
        elif short_path is False:
            url = f'{self.proto}://{self.server}:{self.port}/api/v1/{endpoint}'
        else:
            url = f'{self.proto}://{self.server}:{self.port}/{endpoint}'
        info = {
            'method': method.upper(),
            'username': getattr(self.client.session, 'username', 'unknown'),
            'url': url,
            'endpoint': endpoint,
            'headers': self.client.session.headers,
            'params': params or {},
            'payload': payload or {},
            'files': bool(files),
        }
        request_kwargs = {
            'params': params,
        }
        if files:
            request_kwargs['files'] = files
            if payload:
                request_kwargs['data'] = payload
        if tus_path is True and method.lower() == 'patch':
            request_kwargs['data'] = payload
        else:
            if payload:
                request_kwargs['json'] = payload

        if self.proto == 'https' and self.verify is False:
            request_kwargs['verify'] = self.verify
        request_method = getattr(self.client.session, method.lower())
        response = request_method(url, **request_kwargs)
        if tus_path is True:
            for tus_key in self.tus_header_keys:
                self.client.session.headers.pop(tus_key, None)
        response.info = info
        return response
