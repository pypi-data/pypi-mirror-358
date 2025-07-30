from dubidoc.enum import HttpMethod


__all__ = ('OrganizationAPI',)


class OrganizationAPI:
    PATH = 'organizations'

    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client.make_request(HttpMethod.GET, self.PATH)

    def get(self, document_id):
        path = f'{self.PATH}/{document_id}'
        return self.client.make_request(HttpMethod.GET, path)

    def edit(self, document_id, body):
        path = f'{self.PATH}/{document_id}'
        return self.client.make_request(HttpMethod.PUT, path, body)
