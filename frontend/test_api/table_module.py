def test_create_table(client, test_data):
    res = client.post('/api/tables', json={
        'tournament_id': test_data['tournament_id'],
        'name': '卓A',
        'player_ids': test_data['player_ids']
    })
    assert res.status_code == 201
    data = res.get_json()
    test_data['table_id'] = data['id']

def test_register_game(client, test_data):
    res = client.post(f"/api/tables/{test_data['table_id']}/games", json={
        'scores': [
            {'player_id': test_data['player_ids'][0], 'score': 20},
            {'player_id': test_data['player_ids'][1], 'score': -10},
            {'player_id': test_data['player_ids'][2], 'score': -5},
            {'player_id': test_data['player_ids'][3], 'score': -5},
        ]
    })
    assert res.status_code == 201
    data = res.get_json()
    test_data['game_id'] = data['game_id']
