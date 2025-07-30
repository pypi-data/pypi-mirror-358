from django.test import Client


def test_assert_true():
    client = Client()
    response = client.get('/health_check/')
    assert 200 == response.status_code
    assert b'Service is running!' == response.content
