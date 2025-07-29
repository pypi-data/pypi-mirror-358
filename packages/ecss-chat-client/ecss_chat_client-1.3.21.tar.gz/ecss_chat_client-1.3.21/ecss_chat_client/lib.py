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

    def _make_request(
            self,
            endpoint,
            payload=None,
            params=None,
            method='post',
            files=None,
            short_path=False,
    ):
        if short_path is False:
            url = f'{self.proto}://{self.server}:{self.port}/api/v1/{endpoint}'
        else:
            url = f'{self.proto}://{self.server}:{self.port}/{endpoint}'

        if self.proto == 'https':
            if method.lower() == 'get':
                return self.client.session.get(
                    url,
                    params=params,
                    verify=self.verify,
                )
            else:
                return self.client.session.post(
                    url,
                    json=payload,
                    params=params,
                    files=files,
                    verify=self.verify,
                )

        if self.proto == 'http':
            if method.lower() == 'get':
                return self.client.session.get(url, params=params)
            else:
                return self.client.session.post(
                    url, json=payload, params=params, files=files,
                )
