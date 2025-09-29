def test_register_players(client, test_data):
    player_names = ['佐藤', '鈴木', '高橋', '田中']
    player_ids = []
    for name in player_names:
        res = client.post('/api/players', json={
            'group_id': test_data['group_id'],
            'name': name
        })
        assert res.status_code == 201
        data = res.get_json()
        player_ids.append(data['id'])
    test_data['player_ids'] = player_ids
