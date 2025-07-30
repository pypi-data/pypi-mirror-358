from dubidoc.enum import HttpMethod

__all__ = ('AccessTokenAPI',)


class AccessTokenAPI:
    PATH = 'access-tokens'

    def __init__(self, client):
        self.client = client

    def get_tokens(self):
        """
        Отримати список всіх згенерованих Вами API-ключів (токенів)
        """
        path = self.PATH
        return self.client.make_request(HttpMethod.GET, path)

    def generate_token(self, title):
        """
        Генерування статичного API-ключа (токену) для доступу до API
        :param title:
        """
        path = self.PATH
        return self.client.make_request(HttpMethod.POST, path, body={'title': title})

    def revoke_token(self, token_id):
        """
        Зробити обраний API-ключ (токен) недійсним
        :param token_id:
        """
        path = f'{self.PATH}/{token_id}'
        return self.client.make_request(HttpMethod.DELETE, path)
