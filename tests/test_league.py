import copy
import unittest
from unittest.mock import Mock
from game.league import LeagueGame, award_xp, new_state, RANKS, GODS, MATCH_DURATION, UPGRADES, RELICS, STRATEGIES


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
        self.assertFalse(self.game.update(MATCH_DURATION-1))
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
        self.assertEqual([name for name, _ in RANKS], [
            'Madera 3', 'Madera 2', 'Madera 1',
            'Fierro 3', 'Fierro 2', 'Fierro 1',
            'Platilla 3', 'Platilla 2', 'Platilla 1',
            'Dorado 3', 'Dorado 2', 'Dorado 1',
            'Platino 3', 'Platino 2', 'Platino 1',
            'Rubí 3', 'Rubí 2', 'Rubí 1',
            'Prime 3', 'Prime 2', 'Prime 1',
            'GOD'
        ])

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
        self.assertTrue(restored.update(MATCH_DURATION-5))
        self.assertEqual(restored.state['last_match']['kills'], expected['kills'])
        self.assertEqual(restored.state['last_match']['win'], expected['win'])
        self.assertEqual(restored.state['matches'], 1)

    def test_old_saves_keep_xp_upgrades_and_an_in_progress_match(self):
        legacy=new_state()
        legacy.pop('relic')
        legacy['mastery']={key:4 for key in ('astra','bront','nix')}
        legacy.update(xp=721,rating=190,matches=6)
        result=dict(win=True,kills=3,deaths=4,assists=2,god='nix',strategy='pressure',events=[])
        legacy['battle']=dict(seed=9,elapsed=20.,duration=28.,result=result)
        restored=LeagueGame(Mock(data={'league':copy.deepcopy(legacy)}))
        self.assertEqual(restored.state['xp'],721)
        self.assertEqual(restored.state['mastery']['nix'],4)
        self.assertEqual(restored.state['mastery']['zenit'],0)
        self.assertTrue(restored.update(8))
        self.assertEqual(restored.state['matches'],7)
        self.assertEqual(restored.state['last_match']['kills'],3)

    def test_events_sum_to_score_and_never_call_a_tower_an_assist(self):
        for upgraded in (False,True):
            if upgraded:
                self.game.state['upgrades']={key:10 for key in self.game.state['upgrades']}
                self.game.state['mastery']['astra']=10
            for seed in range(40):
                result=self.game.simulate(seed)
                for key,stat in [('k','kills'),('d','deaths'),('a','assists')]:
                    self.assertEqual(sum(e[key] for e in result['events']),result[stat],(seed,key))
                for event in result['events']:
                    self.assertLess(event['time'],MATCH_DURATION)
                    if event.get('objective'):
                        self.assertEqual(event['type'],'objective')
                        self.assertEqual(event['a'],0)
                    if event.get('combo')==4:self.assertEqual(event['k'],4)
                first=next((e for e in result['events'] if 'Primera sangre' in e['text']),None)
                if first:self.assertFalse(any(e['d'] for e in result['events'] if e['time']<first['time']))

    def test_precision_windows_are_sparse_bounded_and_use_the_corresponding_upgrade(self):
        for level in (0,5,10):
            self.game.state['upgrades']={key:level for key in self.game.state['upgrades']}
            self.game.state['mastery']['astra']=level
            for seed in (2,3):
                self.game.state['battle']=None;self.game.start_battle(seed)
                windows=self.game.state['battle']['windows']
                self.assertIn(len(windows),(2,3))
                for cue in windows:
                    self.assertAlmostEqual(cue['window'],.3+level*.1)
                    self.assertGreaterEqual(cue['window'],.3)
                    self.assertLessEqual(cue['window'],1.3)
                    self.assertLess(cue['at']+cue['windup']+cue['window'],MATCH_DURATION)
                    self.assertGreaterEqual(cue['radius'],9)
                    self.assertLessEqual(cue['radius'],23)

    def test_early_miss_and_outside_click_resolve_once_without_reward(self):
        for outside in (False,True):
            self.game.state['battle']=None;self.game.start_battle(2)
            battle=self.game.state['battle'];cue=battle['windows'][0]
            battle['elapsed']=cue['at']+(.0 if not outside else cue['windup']+cue['window']*.5)
            before=copy.deepcopy(battle['result'])
            result=self.game.attempt_timing((0.,0.) if outside else None)
            self.assertFalse(result['success'])
            self.assertIsNone(self.game.attempt_timing())
            for stat in ('kills','deaths','assists','bonus'):self.assertEqual(before[stat],battle['result'][stat])

    def test_precise_play_changes_actual_events_and_can_change_the_winner(self):
        flipped=False
        for seed in range(100):
            self.game.state['battle']=None;self.game.start_battle(seed)
            battle=self.game.state['battle'];initial=copy.deepcopy(battle['result'])
            for cue in battle['windows']:
                battle['elapsed']=cue['at']+cue['windup']+cue['window']*.5
                self.assertTrue(self.game.attempt_timing()['perfect'])
            self.game.update(MATCH_DURATION)
            result=self.game.state['last_match']
            self.assertGreater(result['kills'],initial['kills'])
            self.assertGreater(result['win_chance'],initial['win_chance'])
            for key,stat in [('k','kills'),('d','deaths'),('a','assists')]:self.assertEqual(sum(e[key] for e in result['events']),result[stat])
            if not initial['win'] and result['win']:flipped=True;break
        self.assertTrue(flipped)
        self.assertEqual(self.game.state['xp'],0)

    def test_penta_adds_only_the_fifth_kill_after_a_real_quadra(self):
        self.game.state['upgrades']={key:10 for key in self.game.state['upgrades']}
        self.game.state['mastery']['astra']=10
        for seed in range(100):
            result=self.game.simulate(seed)
            if any(e.get('combo')==4 for e in result['events']):break
        else:self.fail('No se generó ninguna cuadra')
        self.game.start_battle(seed)
        battle=self.game.state['battle'];cue=battle['windows'][-1]
        battle['elapsed']=cue['at']+cue['windup']+cue['window']*.5
        before=self.game.live_score()[0]
        outcome=self.game.attempt_timing(cue['pos'])
        self.assertIn('Penta',outcome['text'])
        self.assertEqual(self.game.live_score()[0],before+1)
        self.assertTrue(any(e.get('combo')==5 and e['k']==1 for e in battle['result']['events']))

    def test_background_match_and_large_dt_do_not_make_actions_or_free_xp(self):
        self.game.start_battle(4);before=copy.deepcopy(self.game.state['battle']['result'])
        self.game.update(100000,interactive=False)
        result=self.game.state['last_match']
        self.assertEqual((result['kills'],result['deaths'],result['assists']),(before['kills'],before['deaths'],before['assists']))
        self.assertTrue(all(e['status']=='skipped' for e in result['precision']))
        self.assertEqual(self.game.state['xp'],0)
        self.assertFalse(self.game.update(10))

    def test_save_and_reload_during_a_cue_preserves_the_single_reward(self):
        self.game.start_battle(11)
        battle=self.game.state['battle'];cue=battle['windows'][-1]
        battle['elapsed']=cue['at']+cue['windup']+cue['window']*.5
        restored=LeagueGame(Mock(data=copy.deepcopy(self.save.data)))
        self.assertTrue(restored.attempt_timing()['success'])
        again=LeagueGame(Mock(data=copy.deepcopy(restored.save.data)))
        self.assertIsNone(again.attempt_timing())
        again.update(100)
        self.assertEqual(again.state['matches'],1)

    def test_enemy_and_loadout_matter_and_choices_are_locked_in_battle(self):
        self.assertEqual(len(GODS),9)
        self.assertEqual(len(STRATEGIES)*len(RELICS)*len(GODS),324)
        self.game.state['matches']=4
        self.assertEqual(self.game.scout()['weak'],'vision')
        self.assertTrue(self.game.choose_relic('fang'))
        self.game.choose_strategy('pressure');bad=self.game.preparation()['chance']
        self.game.choose_god('bront');self.game.choose_strategy('safe');self.game.choose_relic('aegis')
        self.assertGreater(self.game.preparation()['chance'],bad)
        self.game.start_battle(2)
        self.assertFalse(self.game.choose_relic('lens'))
        self.assertFalse(self.game.choose_god('selka'))
        self.assertFalse(self.game.choose_strategy('team'))
        self.assertFalse(self.game.buy('invalid')[0])

    def test_live_score_starts_empty_and_changes_only_at_real_events(self):
        self.game.start_battle(7)
        self.assertEqual(self.game.live_score(),(0,0,0))
        battle=self.game.state['battle']
        for event in battle['result']['events']:
            battle['elapsed']=event['time']
            seen=[e for e in battle['result']['events'] if e['time']<=battle['elapsed']]
            self.assertEqual(self.game.live_score(),tuple(sum(e[key] for e in seen) for key in ('k','d','a')))

    def test_player_interventions_cannot_leave_a_false_first_blood_message(self):
        for seed in range(40):
            self.game.state['battle']=None;self.game.start_battle(seed)
            battle=self.game.state['battle']
            for cue in battle['windows']:
                battle['elapsed']=cue['at']+cue['windup']+cue['window']*.5
                self.game.attempt_timing()
                events=battle['result']['events']
                blood=[e for e in events if 'Primera sangre' in e['text']]
                self.assertLessEqual(len(blood),1)
                if blood:self.assertFalse(any(e['k']+e['d']+e['a']>0 for e in events if e['time']<blood[0]['time']))


if __name__ == '__main__':
    unittest.main()
