from dubidoc.enum import HttpMethod

__all__ = ('DeviceAPI',)


class DeviceAPI:
    def __init__(self, client):
        self.client = client

    def register(self, token):
        """
        Title: Зареєструвати пристрій для відправки сповіщень
        Description: Зареєструвати device token який отриманий через Firebase Cloud Messaging для відправки нотифікацій користувачу
        """
        path = 'devices'
        body = {'token': token}
        return self.client.make_request(HttpMethod.POST, path, body)

    def unregister(self, token):
        """
        Title: Відписати пристрій від отримання сповіщень
        Description: Скасувати відправку сповіщень для device token
        """
        path = f'devices/{token}'
        return self.client.make_request(HttpMethod.DELETE, path)
