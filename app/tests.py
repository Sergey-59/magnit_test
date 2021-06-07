'''
    Base test
'''


def test_index(client):
    assert client.get('/').status_code == 302


def test_registration(client):
    assert client.post('/registration',
                       json={"email": "test4@gmail.com", "password": "12345", "name": "PyTest"}).status_code == 200

    assert client.post('/registration',
                       json={"password": "12345", "name": "PyTest"}).status_code == 400

    assert client.post('/login', json={"email": "test4@gmail.com", "password": "12345"}).status_code == 200
