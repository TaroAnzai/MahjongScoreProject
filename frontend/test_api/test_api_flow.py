from test_api.group_module import test_create_group, test_login_group
from test_api.player_module import test_register_players
from test_api.tournament_module import test_create_tournament
from test_api.table_module import test_create_table, test_register_game

def test_full_flow(client):
    test_data = {}

    test_create_group(client, test_data)
    test_login_group(client, test_data)
    test_register_players(client, test_data)
    test_create_tournament(client, test_data)
    test_create_table(client, test_data)
    test_register_game(client, test_data)