from typing import List

from buco_db_controller.models.fixture_stats import FixtureStats
from buco_db_controller.repositories.fixture_stats_repository import FixtureStatsRepository
from buco_db_controller.services.fixture_service import FixtureService


class FixtureStatsService:
    apifootball = 'api_football'
    flashscore = 'flashscore'

    def __init__(self):
        self.api_football_fixture_stats_repository = FixtureStatsRepository(self.apifootball)
        self.flashscore_fixture_stats_repository = FixtureStatsRepository(self.flashscore)
        self.fixture_service = FixtureService()

    def upsert_many_fixture_stats(self, fixture_stats: list, source: str):
        if source == self.apifootball:
            self.api_football_fixture_stats_repository.upsert_many_fixture_stats(fixture_stats)
        elif source == self.flashscore:
            self.flashscore_fixture_stats_repository.upsert_many_fixture_stats(fixture_stats)

    def get_fixture_stats(self, fixture_id: int) -> dict[str, FixtureStats]:
        api_football_response = self.api_football_fixture_stats_repository.get_fixture_stats(fixture_id)
        flashscore_response = self.flashscore_fixture_stats_repository.get_fixture_stats(fixture_id)

        if not api_football_response.get('data', []) and not flashscore_response.get('data', []):
            # TODO: Investigate if this can be replaced with return None
            raise ValueError(f'No fixture stats found for fixture {fixture_id}')

        api_football_fixture_stats = FixtureStats.from_dict(api_football_response)
        flashscore_fixture_stats = FixtureStats.from_dict(flashscore_response)

        fixture_stats = {
            self.apifootball: api_football_fixture_stats,
            self.flashscore: flashscore_fixture_stats,
        }
        return fixture_stats

    def get_fixture_stats_over_season(self, team_id: int, league_id: int, season: int) -> dict[str, List[FixtureStats]]:
        fixture_ids = self.fixture_service.get_fixture_ids(team_id, league_id, season)

        api_football_fixture_stats = self.api_football_fixture_stats_repository.get_many_fixture_stats(fixture_ids)
        api_football_fixture_stats = [FixtureStats.from_dict(fixture_stat) for fixture_stat in api_football_fixture_stats]

        flashscore_fixture_stats = self.flashscore_fixture_stats_repository.get_many_fixture_stats(fixture_ids)
        flashscore_fixture_stats = [FixtureStats.from_dict(fixture_stat) for fixture_stat in flashscore_fixture_stats]

        fixture_stats = {
            self.apifootball: api_football_fixture_stats,
            self.flashscore: flashscore_fixture_stats,
        }
        return fixture_stats

    def get_league_fixture_stats(self, league_id: int, season: int) -> dict[str, List[FixtureStats]]:
        fixture_ids = self.fixture_service.get_league_fixture_ids(league_id, season)

        api_football_fixture_stats = self.api_football_fixture_stats_repository.get_many_fixture_stats(fixture_ids)
        api_football_fixture_stats = [FixtureStats.from_dict(fixture_stat) for fixture_stat in api_football_fixture_stats]

        flashscore_fixture_stats = self.flashscore_fixture_stats_repository.get_many_fixture_stats(fixture_ids)
        flashscore_fixture_stats = [FixtureStats.from_dict(fixture_stat) for fixture_stat in flashscore_fixture_stats]

        fixture_stats = {
            self.apifootball: api_football_fixture_stats,
            self.flashscore: flashscore_fixture_stats,
        }
        return fixture_stats