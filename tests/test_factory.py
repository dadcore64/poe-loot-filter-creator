from app import create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_health(client):
    response = client.get('/health')
    assert response.data == b'OK'
