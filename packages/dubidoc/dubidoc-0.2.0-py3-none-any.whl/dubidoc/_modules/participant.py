from dubidoc.enum import HttpMethod

__all__ = ('ParticipantAPI',)


class ParticipantAPI:
    def __init__(self, client):
        self.client = client

    def add_participant(self, document_id, body):
        path = 'documents/{}/participants'.format(document_id)
        return self.client.make_request(HttpMethod.POST, path, body)

    def remove_participant(self, participant_id):
        """
        It sounds like it should be DELETE 'documents/{}/participants/{}', but
        each participant has own unique id, so it should be 'participants/{}'.
        You can retrieve participant_id from the response of 'add_participant' method.
        """
        path = 'participants/{}'.format(participant_id)
        return self.client.make_request(
            HttpMethod.DELETE,
            path,
        )
