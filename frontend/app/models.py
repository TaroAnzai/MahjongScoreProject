
from app import db 
from datetime import datetime, timezone


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    group_key = db.Column(db.String(64), unique=True, nullable=False)
    edit_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tournaments = db.relationship('Tournament', backref='group', lazy=True)
    players = db.relationship("Player", back_populates="group", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Float, default=1.0) 
    description = db.Column(db.Text)
    tournament_key = db.Column(db.String(64), unique=True, nullable=False)
    edit_key = db.Column(db.String(64), unique=True, nullable=False)
    started_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


    tables = db.relationship('Table', backref='tournament', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rate': self.rate,
            'description': self.description,
            'group_id': self.group_id,
            'tournament_key': self.tournament_key,
            'edit_key': self.edit_key,
            'started_at': self.started_at.isoformat() if self.started_at else None,
        }

class Table(db.Model):
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    type = db.Column(db.String(20), default='normal')  # 'normal' または 'chip'
    table_players = db.relationship('TablePlayer', back_populates='table', lazy=True)
    games = db.relationship('Game', backref='table', lazy=True)
    table_key = db.Column(db.String(64), unique=True, nullable=False)
    edit_key = db.Column(db.String(64), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tournament_id': self.tournament_id,
            'table_key': self.table_key,
            'edit_key': self.edit_key,
            'type': self.type,
        }

class TablePlayer(db.Model):
    __tablename__ = 'table_players'
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    seat_position = db.Column(db.Integer)
    joined_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    table = db.relationship('Table', back_populates='table_players')
    player = db.relationship('Player', back_populates='table_participations')

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    nickname = db.Column(db.Text)
    display_order = db.Column(db.Integer)

    table_participations = db.relationship('TablePlayer', back_populates='player', lazy=True)
    scores = db.relationship('Score', backref='player', lazy=True)
    tournament_participations = db.relationship('TournamentPlayer', back_populates='player')

    group = db.relationship("Group", back_populates="players")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nickname': self.nickname,
            'group_id': self.group_id,
        }


class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=False)
    game_index = db.Column(db.Integer, nullable=False)
    played_at = db.Column(db.DateTime)
    memo = db.Column(db.Text)

    scores = db.relationship(
        'Score',
        backref='game',
        lazy=True,
        cascade='all, delete-orphan'
    )



class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer)
    uma = db.Column(db.Float)
    total_score = db.Column(db.Float)

class TournamentPlayer(db.Model):
    __tablename__ = 'tournament_players'
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # 関係
    tournament = db.relationship('Tournament', backref=db.backref('tournament_players', lazy='dynamic'))
    player = db.relationship('Player', back_populates='tournament_participations')

    def to_dict(self):
        return {
            'id': self.id,
            'tournament_id': self.tournament_id,
            'player_id': self.player_id,
            'player_name': self.player.name,
            'created_at': self.created_at.isoformat(),
        }
