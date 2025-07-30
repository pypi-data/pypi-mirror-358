from typing import Optional

from buco_db_controller.models.team import Team


class xG:
    def __init__(
            self,
            fixture_id: int,
            ht: Team,
            at: Team,
            ht_xg: Optional[float],
            at_xg: Optional[float],
            ht_goals: int,
            at_goals: int
    ):
        self.fixture_id: int = fixture_id
        self.ht: Team = ht
        self.at: Team = at
        self.ht_xg: Optional[float] = float(ht_xg) if ht_xg else None
        self.at_xg: Optional[float] = float(at_xg) if at_xg else None
        self.ht_goals: int = ht_goals
        self.at_goals: int = at_goals

    @classmethod
    def from_dict(cls, response: dict) -> 'xG':
        fixture_id = response['parameters']['fixture']
        data = response['data']

        ht_stats = data['home'].get('statistics') or {}
        at_stats = data['away'].get('statistics') or {}

        return cls(
            fixture_id=fixture_id,
            ht=Team(
                team_id=data['home']['team']['id'],
                name=data['home']['team']['name'],
            ),
            at=Team(
                team_id=data['away']['team']['id'],
                name=data['away']['team']['name'],
            ),
            ht_xg=ht_stats.get('xg'),
            at_xg=at_stats.get('xg'),
            ht_goals=ht_stats.get('goals'),
            at_goals=at_stats.get('goals')
        )
