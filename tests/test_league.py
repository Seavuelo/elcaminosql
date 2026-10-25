import copy
import unittest
from unittest.mock import Mock
from game.league import LeagueGame, award_xp, new_state, RANKS, GODS


class LeagueTests(unittest.TestCase):
    def setUp(self):
        self.save = Mock(data={})
        self.game = LeagueGame(self.save)

    def test_academic_rewards_are_one_time_and_positive(self):
        self.assertEqual(award_xp(self.save, 100, 'exercise_1_1_0'), 100)
        self.assertEqual(award_xp(self.save, 100, 'exercise_1_1_0'), 0)
        self.assertEqual(award_xp(self.save, -100, 'invalid'), 0)
        self.assertEqual(self.game.state['xp'], 100)
        self.assertEqual(self.game.state['rewards'], ['exercise_1_1_0'])

    def test_buying_upgrade_deducts_exact_cost_and_caps_at_ten(self):
        award_xp(self.save, 10000, 'budget')
        for level in range(10):
            before = self.game.state['xp']
            cost = self.game.cost('vision')
            success, _ = self.game.buy('vision')
            self.assertTrue(success)
            self.assertEqual(self.game.level('vision'), level + 1)
            self.assertEqual(self.game.state['xp'], before - cost)
        before = copy.deepcopy(self.game.state)
        self.assertFalse(self.game.buy('vision')[0])
        self.assertEqual(self.game.state, before)

    def test_cannot_buy_without_xp_or_during_a_match(self):
        before = copy.deepcopy(self.game.state)
        self.assertFalse(self.game.buy('vision')[0])
        self.assertEqual(self.game.state, before)
        award_xp(self.save, 1000, 'budget')
        self.game.start_battle(seed=1)
        before = copy.deepcopy(self.game.state)
        self.assertFalse(self.game.buy('vision')[0])
        self.assertEqual(self.game.state, before)
        self.assertFalse(self.game.choose_god('nix'))
        self.assertFalse(self.game.choose_strategy('pressure'))

    def test_mastery_belongs_to_each_god(self):
        award_xp(self.save, 1000, 'budget')
        self.game.buy('mastery')
        self.assertEqual(self.game.level('mastery'), 1)
        self.game.choose_god('nix')
        self.assertEqual(self.game.level('mastery'), 0)
        self.game.buy('mastery')
        self.game.choose_god('astra')
        self.assertEqual(self.game.level('mastery'), 1)
        self.assertFalse(self.game.choose_god('invalid'))
        self.assertFalse(self.game.choose_strategy('invalid'))

    def test_upgrades_improve_odds_and_kda_for_the_same_opponents(self):
        base = self.game.simulate(12)
        self.game.state['upgrades'] = {key: 10 for key in self.game.state['upgrades']}
        self.game.state['mastery']['astra'] = 10
        improved = self.game.simulate(12)
        self.assertGreater(improved['win_chance'], base['win_chance'])
        self.assertGreater(improved['kills'], base['kills'])
        self.assertLess(improved['deaths'], base['deaths'])
        self.assertGreater(improved['assists'], base['assists'])

    def test_strategy_and_god_synergy_change_the_odds(self):
        self.game.state['upgrades']['vision'] = 10
        self.game.state['upgrades']['positioning'] = 10
        self.game.choose_strategy('safe')
        safe = self.game.simulate(3)['win_chance']
        self.game.choose_strategy('pressure')
        pressure = self.game.simulate(3)['win_chance']
        self.assertGreater(safe, pressure)
        self.game.choose_strategy('safe')
        self.game.choose_god('bront')
        self.assertGreater(self.game.simulate(3)['win_chance'], safe)

    def test_match_finishes_once_without_granting_farmable_xp(self):
        self.assertTrue(self.game.start_battle(seed=2))
        self.assertFalse(self.game.start_battle(seed=3))
        self.assertFalse(self.game.update(13))
        self.assertTrue(self.game.update(1))
        self.assertEqual(self.game.state['matches'], 1)
        self.assertIsNone(self.game.state['battle'])
        self.assertIsNotNone(self.game.state['last_match'])
        self.assertEqual(self.game.state['xp'], 0)
        self.assertFalse(self.game.update(1000))
        self.assertEqual(self.game.state['matches'], 1)

    def test_placements_and_every_rank(self):
        self.assertEqual(self.game.rank, 'Unranked')
        self.game.state['matches'] = 3
        for name, threshold in RANKS:
            self.game.state['rating'] = threshold
            self.assertEqual(self.game.rank, name)
        self.assertEqual([name for name, _ in RANKS], ['Madera', 'Fierro', 'Platilla', 'Dorado', 'Platino', 'Rubí', 'Prime', 'GOD'])

    def test_state_is_not_shared_between_games_and_new_save_resets_it(self):
        self.game.state['xp'] = 1000
        other = LeagueGame(Mock(data={}))
        self.assertEqual(other.state, new_state())
        self.save.data = {}
        self.assertEqual(self.game.state, new_state())

    def test_saved_match_resumes_with_same_result(self):
        self.game.start_battle(seed=7)
        self.game.update(5)
        expected = copy.deepcopy(self.game.state['battle']['result'])
        restored = LeagueGame(Mock(data=copy.deepcopy(self.save.data)))
        self.assertTrue(restored.update(9))
        self.assertEqual(restored.state['last_match']['kills'], expected['kills'])
        self.assertEqual(restored.state['last_match']['win'], expected['win'])
        self.assertEqual(restored.state['matches'], 1)


if __name__ == '__main__':
    unittest.main()
