import pytest

from app.models import AccessLevel, Tournament


def _create_tournament(client, group_key, name="Main Tournament"):
    """新仕様：グループ共有キーをURLに含める"""
    return client.post(
        f"/api/groups/{group_key}/tournaments",
        json={"name": name},
    )

def _create_table(client, tournament_key, name="Primary Table"):
    """新仕様：大会キーをURLに含めて作成"""
    return client.post(
        f"/api/tournaments/{tournament_key}/tables",
        json={"name": name},
    )
@pytest.mark.api
class TestTournamentEndpoints:
    def test_create_tournament_requires_group_edit(self, client, db_session, create_group):
        group_data, links = create_group()

        # ✅ group_keyをURLに利用（edit権限）
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        assert res.status_code == 201
        tournament = res.get_json()
        assert tournament["group_id"] == group_data["id"]

        # ✅ tournament_links に変更
        levels = {link["access_level"] for link in tournament["tournament_links"]}
        assert levels == {AccessLevel.EDIT.value, AccessLevel.VIEW.value}

        assert "view_link" in tournament
        assert "edit_link" in tournament

    def test_create_tournament_with_view_link_forbidden(self, client, db_session, create_group):
        group_data, links = create_group()
        # VIEW権限では作成不可
        res = _create_tournament(client, links[AccessLevel.VIEW.value])
        assert res.status_code == 403

    def test_get_tournament_requires_view(self, client, db_session, create_group):
        # グループとリンクを作成
        group_data, links = create_group()

        # EDIT権限のリンクで大会を作成
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        tournament = res.get_json()

        # === 作成された大会のリンク辞書を作成 ===
        t_links = {
            link["access_level"]: link["short_key"]
            for link in tournament["tournament_links"]
        }

        # === VIEW権限のトーナメントリンクで取得 ===
        ok = client.get(f"/api/tournaments/{t_links[AccessLevel.VIEW.value]}")
        assert ok.status_code == 200

        fetched = ok.get_json()
        assert "view_link" in fetched
        assert "started_at" in fetched
        # === 検証1: tournament_links が存在する ===
        assert "tournament_links" in fetched
        links_data = fetched["tournament_links"]

        # === 検証2: すべて VIEW のみ ===
        assert all(link["access_level"] == "VIEW" for link in links_data), \
            f"Expected all VIEW links, got: {[l['access_level'] for l in links_data]}"

        # === 検証3: 他のアクセスレベル(EDIT, OWNER)が含まれない ===
        levels = [link["access_level"] for link in links_data]
        assert "EDIT" not in levels, f"Unexpected EDIT links: {links_data}"
        assert "OWNER" not in levels, f"Unexpected OWNER links: {links_data}"

        # === 検証4: 正しい大会が返ってきている ===

        assert fetched["id"] == tournament["id"]

        # === 検証5: グループ情報が含まれている ===
        print(fetched["parent_group_link"])
        assert "parent_group_link" in fetched
        assert "view_link" in fetched['parent_group_link']


        # === 検証5: グループのVIEWキーでは403になる ===
        forbidden = client.get(f"/api/tournaments/{links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403


    def test_update_tournament_requires_edit(self, client, db_session, create_group):
        group_data, links = create_group()
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        tournament = res.get_json()
        t_links = {
            link["access_level"]: link["short_key"] for link in tournament["tournament_links"]
        }

        # VIEW権限では更新不可
        forbidden = client.put(
            f"/api/tournaments/{t_links[AccessLevel.VIEW.value]}",
            json={"name": "Forbidden"},
        )
        assert forbidden.status_code == 403

        # EDIT権限で更新OK
        allowed = client.put(
            f"/api/tournaments/{t_links[AccessLevel.EDIT.value]}",
            json={"name": "Updated"},
        )
        assert allowed.status_code == 200
        updated = db_session.get(Tournament, tournament["id"])
        assert updated.name == "Updated"

    def test_delete_tournament_requires_group_edit(self, client, db_session, create_group):
        group_data, links = create_group()
        res = _create_tournament(client, links[AccessLevel.EDIT.value])
        tournament = res.get_json()
        t_links = {
            link["access_level"]: link["short_key"] for link in tournament["tournament_links"]
        }

        # VIEW権限で削除不可
        forbidden = client.delete(f"/api/tournaments/{t_links[AccessLevel.VIEW.value]}")
        assert forbidden.status_code == 403

        # EDIT権限で削除OK
        allowed = client.delete(f"/api/tournaments/{t_links[AccessLevel.EDIT.value]}")
        assert allowed.status_code == 200
        #assert allowed.get_json()["message"] == "Tournament deleted"
        assert db_session.get(Tournament, tournament["id"]) is None

    def test_get_tournaments_by_group(self, client, db_session, create_group):
        """GET: /api/groups/<group_key>/tournaments - グループ内大会一覧取得"""
        group_data, links = create_group()

        # まずグループ内に大会を2件作成
        res1 = _create_tournament(client, links[AccessLevel.EDIT.value], name="Autumn Cup")
        res2 = _create_tournament(client, links[AccessLevel.EDIT.value], name="Winter Cup")
        assert res1.status_code == 201
        assert res2.status_code == 201

        # GET: 大会一覧取得
        res_list = client.get(f"/api/groups/{links[AccessLevel.VIEW.value]}/tournaments")
        assert res_list.status_code == 200

        data = res_list.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

        Tournament1 = data[0]
        assert "view_link" in Tournament1
        assert "edit_link" not in Tournament1
        assert "owner_link" not in Tournament1


        # 名称で確認
        names = [t["name"] for t in data]
        assert "Autumn Cup" in names
        assert "Winter Cup" in names

        # 存在しない group_key で 404
        res_404 = client.get("/api/groups/xxxxxx/tournaments")
        assert res_404.status_code == 404
        assert any("group_key" in m for m in res_404.get_json()['errors']['json']["message"])

    def test_get_tables_by_tournament(self, client, db_session, create_group):
        """GET: /api/tournaments/<tournament_key>/tables - 大会内卓一覧取得"""
        # --- 前提：グループ・大会を作成 ---
        group_data, group_links = create_group()
        tournament_data = _create_tournament(
            client, group_links[AccessLevel.EDIT.value]
        )
        tournament_links = {
            link["access_level"]: link["short_key"] for link in tournament_data.get_json()["tournament_links"]
        }
        # --- 卓を2件登録 ---
        for i in range(1, 3):
            res = client.post(
                f"/api/tournaments/{tournament_links[AccessLevel.EDIT.value]}/tables",
                json={"name": f"table {i}"},
            )
            assert res.status_code == 201

        # --- GET: 一覧取得 ---
        res_list = client.get(f"/api/tournaments/{tournament_links[AccessLevel.VIEW.value]}/tables")
        assert res_list.status_code == 200

        data = res_list.get_json()
        assert isinstance(data, list)
        assert len(data) == 2

        Game1 = data[0]
        assert "view_link" in Game1
        assert "edit_link" not in Game1
        assert "owner_link" not in Game1


        # --- 存在しない tournament_key で 404 ---
        res_404 = client.get("/api/tournaments/xxxxxx/tables")
        assert res_404.status_code == 404
        assert "共有リンクが無効です。" in res_404.get_json()['errors']['json']["message"]
