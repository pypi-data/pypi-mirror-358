from dubidoc.enum import HttpMethod


__all__ = ('AuthenticationAPI',)


class AuthenticationAPI:
    def __init__(self, client):
        self.client = client

    def get_code(self, login):
        """
        Title: Отримати код авторизації
        Description: Метод відправки тимчасового коду для авторизації через email
        """
        path = self.PATH
        body = {'login': login}
        return self.client.make_request(HttpMethod.POST, path, body)

    def get_token(self, login, code):
        """
        Title: Отримати авторизаційний токен
        Description: Метод для отримання токену користувача на основі email та тимчасового коду авторизації
        """
        path = 'auth/get-token'
        body = {'login': login, 'code': code}
        return self.client.make_request(HttpMethod.POST, path, body)

    def refresh(self, refresh_token):
        """
        Title: Оновити авторизаційний токен
        Description: Продовжити дію авторизаційного токену користувача на основі refresh токену
        :param token_id:
        :return:
        """
        path = 'token/refresh'
        body = {'refresh_token': refresh_token}
        return self.client.delete(HttpMethod.POST, path, body)
