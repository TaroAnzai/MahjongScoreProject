from datetime import datetime, timezone
from app import db
from app.models import AccessLevel, Game, Table, Score,TablePlayer
from app.service_errors import (
    ServiceNotFoundError,
    ServicePermissionError,
    ServiceValidationError,
)
from app.utils.share_link_utils import create_default_share_links, get_share_link_by_key

from sqlalchemy import func

_ACCESS_PRIORITY = {
    AccessLevel.VIEW: 1,
    AccessLevel.EDIT: 2,
    AccessLevel.OWNER: 3,
}


# =========================================================
# 内部ユーティリティ
# =========================================================
def _require_table(short_key: str):
    """共有キーから卓を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("table_keyが無効です。")
    if link.resource_type != "table":
        raise ServicePermissionError("table_keyの対象が一致しません。")

    table = Table.query.get(link.resource_id)
    if not table:
        raise ServiceNotFoundError("卓が見つかりません。")
    return link, table


def _require_game(short_key: str):
    """共有キーから対局を特定"""
    link = get_share_link_by_key(short_key)
    if not link:
        raise ServiceNotFoundError("game_keyが無効です。")
    if link.resource_type != "game":
        raise ServicePermissionError("game_keyの対象が一致しません。")

    game = Game.query.get(link.resource_id)
    if not game:
        raise ServiceNotFoundError("対局が見つかりません。")
    return link, game


def _ensure_access(link, required: AccessLevel, message: str):
    """アクセスレベルチェック"""
    if _ACCESS_PRIORITY[link.access_level] < _ACCESS_PRIORITY[required]:
        raise ServicePermissionError(message)


# =========================================================
# サービス関数群
# =========================================================
def create_game(table_key: str, data: dict) -> Game:
    """卓に対局（スコア付き）を追加"""

    link = get_share_link_by_key(table_key)
    if not link:
        raise ServiceNotFoundError("table_keyが無効です。")

    _ensure_access(link, AccessLevel.EDIT, "対局を作成する権限がありません。")

    if not link or link.resource_type != "table":
        raise ServiceNotFoundError("指定された卓が見つかりません。")

    table = Table.query.get(link.resource_id)
    if not table:
        raise ServiceNotFoundError("卓が存在しません。")

    scores = data.get("scores", [])
    memo = data.get("memo")

    if not isinstance(scores, list) or not scores:
        raise ServiceValidationError("scores はリスト形式で必須です。")

    total = sum(s.get("score", 0) for s in scores)
    if total != 0:
        raise ServiceValidationError("スコアの合計は0である必要があります。")
    # ✅ 卓に登録されているプレイヤーID一覧を取得
    table_player_ids = {
        tp.player_id for tp in TablePlayer.query.filter_by(table_id=table.id).all()
    }
    if not table_player_ids:
        raise ServiceValidationError("この卓にはまだプレイヤーが登録されていません。")
    #作成者情報
    created_by = table.created_by or "anonymous"
    # game_index 自動採番
    max_index = db.session.query(func.max(Game.game_index)).filter_by(table_id=table.id).scalar()
    next_index = (max_index or 0) + 1

    game = Game(
        table_id=table.id,
        game_index=next_index,
        memo=memo,
        created_by=created_by,  # ← ここを継承する
    )
    db.session.add(game)
    db.session.flush()  # game.idを確定

    for s in scores:
        pid = s.get("player_id")
        val = s.get("score")
        if pid is None or val is None:
            raise ServiceValidationError("player_id と score は必須です。")

        if pid not in table_player_ids:
            raise ServiceValidationError(f"player_id {pid} はこの卓に登録されていません。")
        db.session.add(Score(game_id=game.id, player_id=pid, score=val))

    db.session.commit()
    return game

def get_games_by_table(table_key: str):
    """卓共有キーから対局一覧（スコア込み）を取得"""
    from app.utils.share_link_utils import get_share_link_by_key
    from app.models import Game, Score, Table

    link = get_share_link_by_key(table_key)
    if not link or link.resource_type != "table":
        raise ServiceNotFoundError("table_keyが無効です。")

    table = Table.query.get(link.resource_id)
    if not table:
        raise ServiceNotFoundError("卓が存在しません。")

    games = Game.query.filter_by(table_id=table.id).order_by(Game.id.asc()).all()
    result = []
    for g in games:
        scores = [
            {"player_id": s.player_id, "score": s.score}
            for s in Score.query.filter_by(game_id=g.id).all()
        ]
        result.append({
            "id": g.id,
            "table_id": table.id,
            "game_index": g.game_index,
            "memo": g.memo,
            "scores": scores,
        })
    return result
def get_game_by_key(table_key: str, game_id: int) -> Game:
    """Tableキー,Game_idから取得"""
    link = get_share_link_by_key(table_key)
    if not link:
        raise ServiceNotFoundError("table_keyが無効です。")
    _ensure_access(link, AccessLevel.VIEW, "対局を閲覧する権限がありません。")
    game = Game.query.get_or_404(game_id)
    return game


def update_game(table_key: str,game_id: int, data: dict) -> Game:
    """Tableキー,Game_idから更新（メモ・日付・スコア）"""
    link, table = _require_table(table_key)
    if not link:
        raise ServiceNotFoundError("table_keyが無効です。")
    _ensure_access(link, AccessLevel.EDIT, "対局を更新する権限がありません。")
    game = Game.query.get_or_404(game_id)
    if game.table_id != table.id:
        raise ServiceNotFoundError("指定された対局が見つかりません。")
    # --- 基本項目更新 ---
    if "game_index" in data:
        game.game_index = data["game_index"]
    if "memo" in data:
        game.memo = data["memo"]
    if "played_at" in data:
        game.played_at = data["played_at"]

    # --- スコア更新処理 ---
    scores = data.get("scores")
    if scores is not None:
        if not isinstance(scores, list):
            raise ServiceValidationError("scores はリスト形式である必要があります。")

        total = sum(s.get("score", 0) for s in scores)
        if total != 0:
            raise ServiceValidationError("スコアの合計は0でなければなりません。")

        # 既存スコア削除
        Score.query.filter_by(game_id=game.id).delete()

        # 新しいスコアを追加
        for s in scores:
            player_id = s.get("player_id")
            score_val = s.get("score")
            if player_id is None or score_val is None:
                continue
            db.session.add(Score(game_id=game.id, player_id=player_id, score=score_val))

    db.session.commit()
    db.session.refresh(game)

    return game


def delete_game(table_key: str, game_id: int) -> None:
    """対局共有キーから削除"""
    link, table = _require_table(table_key)
    if not link:
        raise ServiceNotFoundError("table_keyが無効です。")
    _ensure_access(link, AccessLevel.EDIT, "対局を削除する権限がありません。")
    game = Game.query.get_or_404(game_id)
    if game.table_id != table.id:
        raise ServiceNotFoundError("指定された対局が見つかりません。")
    db.session.delete(game)
    db.session.commit()
