# app/services/export_service.py
from app.models import db, Tournament, Group, Player, Table, Game, Score, TournamentPlayer

class ExportService:
    @staticmethod
    def export_tournament_results(tournament_id: int):
        tournament = Tournament.query.get_or_404(tournament_id)
        result = {
            'tournament': {'id': tournament.id, 'name': tournament.name},
            'groups': []
        }

        if not tournament.group:
            return result

        group = tournament.group
        group_data = {
            'id': group.id,
            'name': group.name,
            'players': []
        }

        players = (
            db.session.query(Player)
            .join(TournamentPlayer, Player.id == TournamentPlayer.player_id)
            .filter(TournamentPlayer.tournament_id == tournament.id)
            .all()
        )
        for player in players:
            scores = Score.query.filter_by(player_id=player.id).all()
            total_score = sum([s.score for s in scores])
            group_data['players'].append({
                'id': player.id,
                'name': player.name,
                'total_score': total_score,
                'games_played': len(scores)
            })

        result['groups'].append(group_data)
        return result

    @staticmethod
    def export_score_summary(tournament_id: int):
        tournament = Tournament.query.get_or_404(tournament_id)
        players = Player.query.filter_by(tournament_id=tournament.id).order_by(Player.id).all()
        player_map = {p.id: p.name for p in players}

        tables = Table.query.filter_by(tournament_id=tournament.id).all()
        result = {
            'players': [{'id': pid, 'name': pname} for pid, pname in player_map.items()],
            'tables': []
        }

        for table in tables:
            table_data = {'name': table.name, 'scores': {}}
            games = Game.query.filter_by(table_id=table.id).order_by(Game.id).all()
            for game in games:
                scores = Score.query.filter_by(game_id=game.id).all()
                for score in scores:
                    table_data['scores'][score.player_id] = (
                        table_data['scores'].get(score.player_id, 0) + score.score
                    )
            result['tables'].append(table_data)

        return result
