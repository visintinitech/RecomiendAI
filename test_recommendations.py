def test_recommendations_requires_auth(client):
    resp = client.get('/api/users/1/recommendations')
    assert resp.status_code == 401

def test_recommendations_ok(client, auth_headers):
    resp = client.get('/api/users/1/recommendations', headers=auth_headers)
    assert resp.status_code == 200
