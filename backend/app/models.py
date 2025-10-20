from app import db
from datetime import datetime, timezone
import uuid
from sqlalchemy import event
from enum import StrEnum

# =========================================================
# Enum定義
# =========================================================
class AccessLevel(StrEnum):
    VIEW = "VIEW"
    EDIT = "EDIT"
    OWNER = "OWNER"


# =========================================================
# グループ（最上位レイヤー）
# =========================================================
class Group(db.Model):
    __tablename__ = "tbl_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(
        db.String(64), nullable=False, default=lambda: str(uuid.uuid4())
    )  # グループ作成者（オーナー）
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        server_default=db.func.now(),
    )

    # リレーション
    tournaments = db.relationship("Tournament", back_populates="group")
    players = db.relationship(
        "Player", back_populates="group", cascade="all, delete-orphan"
    )

    # ✅ ShareLinkリレーション（Group固有 → group_links に変更）
    group_links = db.relationship(
        "ShareLink",
        primaryjoin="and_(ShareLink.resource_type=='group', "
                    "foreign(ShareLink.resource_id)==Group.id)",
        viewonly=True,
        lazy="joined"
    )


# =========================================================
# 大会
# =========================================================
class Tournament(db.Model):
    __tablename__ = "tbl_tournaments"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("tbl_groups.id"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Float, default=1.0)
    description = db.Column(db.Text)
    created_by = db.Column(db.String(64), nullable=False)  # 作成者
    started_at = db.Column(db.DateTime)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # 関連
    group = db.relationship("Group", back_populates="tournaments")
    tables = db.relationship(
        "Table", backref="tournament", lazy=True, cascade="all, delete-orphan"
    )

    # ✅ ShareLinkリレーション（大会 → tournament_links に変更）
    tournament_links = db.relationship(
        "ShareLink",
        primaryjoin="and_(ShareLink.resource_type=='tournament', "
                    "foreign(ShareLink.resource_id)==Tournament.id)",
        viewonly=True,
        lazy="joined"
    )
    participants = db.relationship(
        "TournamentPlayer",
        back_populates="tournament",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


# =========================================================
# 卓（テーブル）
# =========================================================
class Table(db.Model):
    __tablename__ = "tbl_tables"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tbl_tournaments.id"), nullable=False
    )
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default="normal")  # normal / chip
    created_by = db.Column(db.String(64), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    table_players = db.relationship("TablePlayer", back_populates="table", lazy=True)
    games = db.relationship(
        "Game", backref="table", lazy=True, cascade="all, delete-orphan"
    )

    # ✅ ShareLinkリレーション（卓 → table_links に変更）
    table_links = db.relationship(
        "ShareLink",
        primaryjoin="and_(ShareLink.resource_type=='table', "
                    "foreign(ShareLink.resource_id)==Table.id)",
        viewonly=True,
        lazy="joined"
    )


# =========================================================
# 卓プレイヤー（着席情報）
# =========================================================
class TablePlayer(db.Model):
    __tablename__ = "tbl_table_players"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("tbl_tables.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("tbl_players.id"), nullable=False)
    seat_position = db.Column(db.Integer)
    joined_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    table = db.relationship("Table", back_populates="table_players")
    player = db.relationship("Player", back_populates="table_participations")


# =========================================================
# プレイヤー
# =========================================================
class Player(db.Model):
    __tablename__ = "tbl_players"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("tbl_groups.id"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    nickname = db.Column(db.Text)
    display_order = db.Column(db.Integer)

    group = db.relationship("Group", back_populates="players")
    table_participations = db.relationship(
        "TablePlayer", back_populates="player", lazy=True
    )
    scores = db.relationship("Score", backref="player", lazy=True)
    tournament_participations = db.relationship(
        "TournamentPlayer", back_populates="player"
    )


# =========================================================
# ゲーム（半荘）
# =========================================================
class Game(db.Model):
    __tablename__ = "tbl_games"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("tbl_tables.id"), nullable=False)
    game_index = db.Column(db.Integer, nullable=False)
    memo = db.Column(db.Text)
    played_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(64), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    scores = db.relationship(
        "Score", backref="game", lazy=True, cascade="all, delete-orphan"
    )


# =========================================================
# スコア（各プレイヤーの点数）
# =========================================================
class Score(db.Model):
    __tablename__ = "tbl_scores"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("tbl_games.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("tbl_players.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer)
    uma = db.Column(db.Float)
    total_score = db.Column(db.Float)


# =========================================================
# 大会参加者
# =========================================================
class TournamentPlayer(db.Model):
    __tablename__ = "tbl_tournament_players"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tbl_tournaments.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("tbl_players.id"), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    tournament = db.relationship("Tournament", back_populates="participants")
    player = db.relationship("Player", back_populates="tournament_participations")

# =========================================================
# 共有リンク（短縮キー方式）
# =========================================================
class ShareLink(db.Model):
    __tablename__ = "tbl_share_links"

    id = db.Column(db.Integer, primary_key=True)
    short_key = db.Column(db.String(16), unique=True, nullable=False)
    resource_type = db.Column(db.String(32), nullable=False)  # group / tournament / table / game
    resource_id = db.Column(db.Integer, nullable=False)
    access_level = db.Column(db.Enum(AccessLevel), default=AccessLevel.VIEW, nullable=False)
    created_by = db.Column(db.String(64), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


# =========================================================
# Groupの最終更新日時を自動更新するイベントリスナー
# =========================================================
def touch_group(connection, group_id: int) -> bool:
    """Groupのlast_updated_atを現在時刻に更新"""
    if not group_id:
        return False
    connection.execute(
        db.text("UPDATE tbl_groups SET last_updated_at = :now WHERE id = :gid"),
        {"now": datetime.now(timezone.utc), "gid": group_id},
    )
    return True


# --- Groupの変更 ---
@event.listens_for(Group, "before_update")
def update_self_last_updated(mapper, connection, target):
    touch_group(connection, target.id)


# --- Tournamentの変更 ---
@event.listens_for(Tournament, "after_insert")
@event.listens_for(Tournament, "after_update")
@event.listens_for(Tournament, "after_delete")
def update_group_on_tournament_change(mapper, connection, target):
    touch_group(connection, target.group_id)


# --- Tableの変更 ---
@event.listens_for(Table, "after_insert")
@event.listens_for(Table, "after_update")
@event.listens_for(Table, "after_delete")
def update_group_on_table_change(mapper, connection, target):
    result = connection.execute(
        db.text("SELECT group_id FROM tbl_tournaments WHERE id = :tid"),
        {"tid": target.tournament_id},
    ).fetchone()
    if result:
        touch_group(connection, result.group_id)


# --- Gameの変更 ---
@event.listens_for(Game, "after_insert")
@event.listens_for(Game, "after_update")
@event.listens_for(Game, "after_delete")
def update_group_on_game_change(mapper, connection, target):
    result = connection.execute(
        db.text(
            "SELECT tr.group_id FROM tbl_tournaments tr "
            "JOIN tbl_tables t ON tr.id = t.tournament_id "
            "JOIN tbl_games gm ON gm.table_id = t.id "
            "WHERE gm.id = :gid"
        ),
        {"gid": target.id},
    ).fetchone()
    if result:
        touch_group(connection, result.group_id)
