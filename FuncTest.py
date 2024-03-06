import unittest
from datetime import date

from DBActions import DBActions
import pathlib
import os

from Habit import HabitMaster, HabitLog


def del_test_db():
    """to delete test_db file after testing"""
    os.remove(pathlib.Path('habit_db').absolute())


class CreateDBObjects(unittest.TestCase):
    # initialize dba object with test_db instead of habit_db to keep productive DB clean
    db_con: str = 'habit_db'
    dba = DBActions(db_con=db_con)
    hm = HabitMaster()
    hl = HabitLog()

    @classmethod
    def setUpClass(cls):
        pass  # TODO: probably not needed

    @classmethod
    def tearDownClass(cls): # TODO: remove quote when finished
        """delete test_db file after testing"""
        # del_test_db()

    def test_a_tab_creation(self):
        """creates test_db and checks whether all tables were created"""
        print('test_tab_creation')
        # to create test database 'test_db' -> 3 Tables must be created
        self.assertEqual(self.dba.create_tables(), 3)
        # then add some records? Or make this a test case? Or Both?

    def test_add_habit(self):
        print('test_add_habit')  # TODO: Offer Option to generate test data in menu + option to del test data
        # name, status, description, is_quant., periodicity, frequency, start, end, cur_per, cur_year, quantity unit
        habits = [['sports', 1, 'cardio exercise twice every week', 0, 'weekly', 2, date.fromisoformat('2024-02-01'),
                   date.fromisoformat('2199-12-31'), '5', 2024, '', ''],
                  ['water', 1, 'drink 8 glasses of water every day', 1, 'daily', 1, date.fromisoformat('2024-02-01'),
                   date.fromisoformat('2199-12-31'), '2024-02-01', 2024, 8, 'glasses'],
                  ['dentist', 1, 'see dentist for check up once a year', 0, 'yearly', 1,
                   date.fromisoformat('2022-01-01'), date.fromisoformat('2199-12-31'), 2022, 2022, '', ''],
                  ['run3k', 1, 'do two 3k runs every month', 1, 'monthly', 2, date.fromisoformat('2024-02-01'),
                   date.fromisoformat('2199-12-31'), '2', 2024, 3, 'km'],
                  ['brush teeth', 1, 'brush teeth twice a day', 0, 'daily', 2, date.fromisoformat('2022-01-01'),
                   date.fromisoformat('2199-12-31'), '2024-02-01', 2024, '', '']]
        count = 0
        for habit in habits:
            count = count + self.dba.create_habit(habit[0], habit[1], habit[2], habit[3], habit[4], habit[5], habit[6],
                                                  habit[7], habit[8], habit[9], habit[10], habit[11])[0]
        # count should be 10 because for each habit 2 records have to be created -> rowcount should be 2 for each
        self.assertEqual(count, 10)

    def test_b_log_habits(self):
        print('test_log_habit')
        # name, log_date, completed, quantity, partial)
        habit_logs = [['water', date.fromisoformat('2024-02-01'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-02'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-03'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-04'), 0, 7, 0.875],
                      ['water', date.fromisoformat('2024-02-05'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-06'), 0, 6, 0.75],
                      ['water', date.fromisoformat('2024-02-07'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-08'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-09'), 0, 5, 0.625],
                      ['water', date.fromisoformat('2024-02-10'), 0, 7, 0.875],
                      ['water', date.fromisoformat('2024-02-11'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-12'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-13'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-14'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-15'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-16'), 0, 6, 0.75],
                      ['water', date.fromisoformat('2024-02-17'), 0, 9, 1.125],
                      ['water', date.fromisoformat('2024-02-18'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-19'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-20'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-21'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-22'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-23'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-24'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-25'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-26'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-27'), 0, 7, 0.875],
                      ['water', date.fromisoformat('2024-02-28'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-02-29'), 1, 8, 1],
                      ['water', date.fromisoformat('2024-03-01'), 0, 7, 0.875],
                      ['brush teeth', date.fromisoformat('2024-02-01'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-01'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-02'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-02'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-03'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-03'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-04'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-04'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-05'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-05'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-06'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-06'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-07'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-07'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-08'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-08'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-09'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-09'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-10'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-10'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-11'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-11'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-12'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-12'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-13'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-13'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-14'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-14'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-15'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-15'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-16'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-16'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-17'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-17'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-18'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-18'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-19'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-19'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-20'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-20'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-21'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-21'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-22'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-22'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-23'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-23'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-24'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-24'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-25'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-25'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-26'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-26'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-27'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-27'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-28'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-28'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-29'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-02-29'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-03-01'), 1, '', ''],
                      ['brush teeth', date.fromisoformat('2024-03-01'), 1, '', ''],
                      ['dentist', date.fromisoformat('2022-03-17'), 1, '', ''],
                      ['dentist', date.fromisoformat('2023-02-09'), 1, '', ''],
                      ['dentist', date.fromisoformat('2023-11-06'), 1, '', ''],
                      ['dentist', date.fromisoformat('2024-01-18'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-02'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-05'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-07'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-13'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-16'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-21'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-27'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-02-24'), 1, '', ''],
                      ['sports', date.fromisoformat('2024-03-02'), 1, '', ''],
                      ['run3k', date.fromisoformat('2024-02-09'), 0, 2.1, 0.7],
                      ['run3k', date.fromisoformat('2024-02-18'), 1, 3, 1],
                      ['run3k', date.fromisoformat('2024-02-29'), 1, 3., 1.067]]

        for log in habit_logs:
            # print(log)
            self.hl.log_completion(log[0], log[1], log[2], log[3], log[4])
        # each log must result in 1 record in habit_logs
        self.assertEqual(self.dba.count_logs(), 106)

    def test_c_calc_streak_complete(self):  # sport, twice-weekly, with irregular logging
        print('test_calc_streak_complete')
        streak_sports = self.dba.get_active_habit_streak('sports')
        streak_row_count = self.dba.get_row_count_by_habit('sports', 'habit_streaks', 'id')
        # there may be only 1 record because streak is complete starting from week 6 as the first full week since start,
        # although it was not logged chronologically, because this must trigger the full calculation
        self.assertEqual(1, streak_row_count, "Test failed for habit_streaks row count for 'sports'")
        # streak has to be 4 because each week has been complete
        self.assertEqual(4, streak_sports[6], "Test failed for streak for 'sport'.")
        # streak date has to be March, 2nd 2024 because this is the last log completing the last week
        self.assertEqual('2024-03-02', str(streak_sports[5]), "Test failed for streak date for 'sport'.")

    def test_d_calc_streak_same_per(self):  # run3k, monthly, chronologically logged
        print('test_calc_streak_same_per')
        # streak_sports = self.dba.get_active_habit_streak('sports')
        streak_run3k = self.dba.get_active_habit_streak('run3k')
        streak_row_count = self.dba.get_row_count_by_habit('run3k', 'habit_streaks', 'id')
        # streak calculation within in the same period, chronologically logged
        # -> calculation is based on previously determined streak;

        # there must be only one record in habit_streaks:
        self.assertEqual(1, streak_row_count, "Test failed for habit_streaks row count for 'run3k'")
        # streak has to be 1 because there have been 2 complete 3ks in Feb
        self.assertEqual(1, streak_run3k[6], "Test failed for streak for 'run3k'.")
        # streak date has to be Feb, 29 2024 because this is the 2nd complete log, 1 incomplete log may not be counted
        self.assertEqual('2024-02-29', str(streak_run3k[5]), "Test failed for streak date for 'run3k'.")

    def test_e_calc_streak_next_per(self):  # teeth, daily -> each day is a next_per
        print('test_calc_streak_next_per')
        streak_teeth = self.dba.get_active_habit_streak('brush teeth')
        streak_row_count = self.dba.get_row_count_by_habit('brush teeth', 'habit_streaks', 'id')

        # there must be only one record in habit_streaks:
        self.assertEqual(streak_row_count, 1)
        # full streak because completed each day -> streak must be 30
        self.assertEqual(30, streak_teeth[6], "Test failed for streak for 'teeth'.")
        # and streak date must be the last log date
        self.assertEqual('2024-03-01', str(streak_teeth[5]), "Test failed for streak date for 'teeth'.")

    def test_f_calc_streak_bonus_log(self):  # dentist, yearly, one bonus log
        print('test_calc_streak_bonus_log')
        streak_dentist = self.dba.get_active_habit_streak('dentist')
        streak_row_count = self.dba.get_row_count_by_habit('dentist', 'habit_streaks', 'id')

        # there must be only one record in habit_streaks:
        self.assertEqual(1, streak_row_count, "Test failed for habit_streaks row count for 'dentist'")
        # logged in each of 3 years, with one bonus log in 2023 which must have no effect
        self.assertEqual(3, streak_dentist[6], "Test failed for streak for 'dentist'.")
        # therefore streak date must be the last log date
        self.assertEqual('2024-01-18', str(streak_dentist[5]), "Test failed for streak date for 'dentist'.")

    def test_g_calc_streak_broken(self):  # water, daily quantifiable, broken 6 times
        print('test_calc_streak_broken')
        streak_water = self.dba.get_active_habit_streak('water')
        streak_row_count = self.dba.get_row_count_by_habit('water', 'habit_streaks', 'id')

        # there must be 7 records in habit_streaks - 6 for previous streaks and one new initial record:
        self.assertEqual(7, streak_row_count, "Test failed for habit_streaks row count for 'water'")

        # current streak must be 0 because last record broke the streak
        self.assertEqual(0, streak_water[6], "Test failed for current streak for 'water'.")

        # therefore the current record must be initial and not have a streak date
        self.assertEqual(None, streak_water[5], "Test failed for initial streak date for 'water'.")

    def test_g_max_streak_per_habits(self):
        print('test_max_streak_per_habits')
        # expected max streaks per habit:
        max_streaks = [['dentist', 3], ['water', 9], ['brush teeth', 30], ['sports', 4], ['run3k', 1]]
        for entry in max_streaks:
            habit, streak, str_date = self.dba.get_max_streak(entry[0])
            self.assertEqual(entry[1], streak, "Test failed for habit " + str(habit))

    def test_g_max_streak(self):
        print('test_max_streak')
        # as daily habit with no breaks brush teeth must have the max streak of 30 with date 2024-03-01
        habit, streak, str_date = self.dba.get_max_streak()
        self.assertEqual('brush teeth', habit)
        self.assertEqual(30, streak)
        self.assertEqual('2024-03-01', str_date)

    def test_h_delete_habit(self):
        print('test_delete_habit')
        # TODO: implement this

    def test_i_tab_deletion(self):
        print('test_i_tab_deletion')
        """deletes all tables from test_db"""
        # 3 Tables must be deleted, 0 tables remain
        self.assertEqual(self.dba.delete_tables(), 0)


if __name__ == '__main__':
    unittest.main()
