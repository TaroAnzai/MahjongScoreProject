def test_create_tournament(client, test_data):
    res = client.post('/api/tournaments', json={
        'group_id': test_data['group_id'],
        'name': '春季大会'
    })
    assert res.status_code == 201
    data = res.get_json()
    test_data['tournament_id'] = data['id']
    test_data['tournament_key'] = data['tournament_key']
    test_data['tournament_edit_key'] = data['edit_key']
