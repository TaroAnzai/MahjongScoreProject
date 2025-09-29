def test_create_group(client, test_data):
    res = client.post('/api/groups', json={
        'name': 'テストグループ',
        'description': 'pytest用'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'id' in data and 'group_key' in data and 'edit_key' in data
    test_data['group_id'] = data['id']
    test_data['group_key'] = data['group_key']
    test_data['group_edit_key'] = data['edit_key']

def test_login_group(client, test_data):
    print(test_data)
    res = client.post('/api/login/by-key', json={
        'edit_key': test_data['group_edit_key'],
        'type': 'group'
    })
    assert res.status_code == 200
