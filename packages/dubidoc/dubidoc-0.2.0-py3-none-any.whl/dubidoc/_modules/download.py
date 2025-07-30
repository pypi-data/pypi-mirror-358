from dubidoc.enum import HttpMethod


__all__ = ('DownloadAPI',)


class DownloadAPI:
    PATH = 'downloads'

    def __init__(self, client):
        self.client = client

    def bulk_uploads(self, body):
        path = self.PATH
        return self.client.make_request(HttpMethod.POST, path, body)

    def download(self, download_id):
        path = f'{self.PATH}/{download_id}/download'
        return self.client.make_request(HttpMethod.GET, path)

    def check_status(self, download_id):
        path = f'{self.PATH}/{download_id}/status'
        return self.client.make_request(HttpMethod.GET, path)
