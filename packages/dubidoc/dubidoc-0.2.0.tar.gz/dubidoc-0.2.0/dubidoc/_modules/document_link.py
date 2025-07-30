from dubidoc.enum import HttpMethod

__all__ = ('DocumentLinkAPI',)


class DocumentLinkAPI:
    PATH = 'documents/{}/links'

    def __init__(self, client):
        self.client = client

    def generate_public_link(self, document_id, body):
        path = self.PATH.format(document_id)
        return self.client.make_request(HttpMethod.POST, path, body)

    def revoke_public_link(self, document_id):
        path = self.PATH.format(document_id)
        return self.client.make_request(HttpMethod.DELETE, path)
