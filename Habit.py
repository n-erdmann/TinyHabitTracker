from datetime import date, datetime, timedelta
import datetime
import questionary
import pandas as pd

from DBActions import DBActions


class Habit:
    def __init__(self, name='', description='', start='', end='', status: int = '', periodicity='',
                 frequency: int = '', quantity='', unit='', is_quantifiable: int = '', dba=DBActions()):
        """initialize the habit class attributes"""
        """ name: str, description: str, start: datetime.date, end: datetime.date, status: int, periodicity: str,
        frequency: int, today: datetime.date, quantity: float, unit: str, is_quantifiable: int """
        # self.dba = DBActions()
        self.name = name
        self.description = description
        self.start = start
        self.end = end
        self.status = status
        self.periodicity = periodicity
        self.frequency = frequency
        self.quantity = quantity
        self.unit = unit
        self.is_quantifiable = is_quantifiable
        self.periodicity_range = ['daily', 'weekly', 'monthly', 'yearly']
        self.dba = dba

    def get_active_habit_info(self, habit: str, info: bool = True, streaks: bool = True) -> list:
        """reads habit master data and/or habit streak data for given habit
        returned lists can be chosen by specifying bool values for attributes info and streak
        :param habit: habit name
        :param info: boolean flag to choose habit master data information
        :param streaks: boolean flag to choose streak data
        :return: one or two lists (habit_info, habit_streaks)"""
        if info:
            habit_info = self.dba.get_active_habit_info(name=habit)

        if streaks:
            habit_streaks = self.dba.get_active_habit_streak(name=habit)

        # habit_log = dba.get_habit_logs(name=habit)

        if info is True and streaks is True:
            return habit_info, habit_streaks
        elif info is True and streaks is False:
            return habit_info
        elif info is False and streaks is True:
            return habit_streaks

    @staticmethod
    def get_periodicity(habit: str, date: datetime.date = datetime.date.today(), dba: object = DBActions()) -> str:
        """returns the current periodicity of the habit - daily, weekly, monthly or yearly"""
        periodicity = dba.get_periodicity(name=habit, date=date)

        return periodicity

    @property
    def get_periodicity_range(self) -> tuple:
        """returns a list of possible periodicity values for the habit tracker.
        Available periodicity values are specified in Habit class attributes
        :return: tuple (list of periodicity values, dictionary of periodicity values)
        """
        per_list = self.periodicity_range

        per_dict = {}
        n = 1
        for per in per_list:
            per_dict[n] = per
            n += 1
        return self.periodicity_range, per_dict


class HabitMaster(Habit):
    def __init__(self, name='', description='', start: datetime.date = '', end='', status='', periodicity='',
                 frequency='', quantity='', unit='', is_quantifiable=''):
        super().__init__(name, description, start, end, status, periodicity, frequency, quantity, unit, is_quantifiable)

    def create(self, name: str, description: str, start: datetime.date, periodicity: str, frequency: int,
               is_quantifiable: int, quantity: float, unit: str = '') -> (int, str):
        """first, collects all necessary info from user to create new habit
               then calls the create method from DBAction class to save the new record to the database
               :rtype: int, str
               :param name: habit name
               :param description: habit description
               :param start: start date of habit
               :param periodicity: str with chosen periodicity
               :param frequency: int, intended frequency of habit completion
               :param is_quantifiable: 1 if habit is quantifiable, 0 if not
               :param quantity: intended quantity if habit is quantifiable, None if not
               :param unit: str, optional user specified unit for quantity, no standards values
               :return: tuple (int, str) number of changed records and return message from DB Action method"""

        # set default values for new habit
        end = date.fromisoformat('2199-12-31')  # Default end date
        status = 1  # Default status

        # calculate cur_per values for initial entry in streaks table
        if periodicity == 'daily':
            cur_per = start
            cur_year = start.year
        elif periodicity == 'weekly':
            cur_per = start.isocalendar()[1]
            cur_year = start.year
        elif periodicity == 'monthly':
            cur_per = start.month
            cur_year = start.year
        elif periodicity == 'yearly':
            cur_per = start.year
            cur_year = start.year
        else:
            cur_per = start
            cur_year = start.year

        # call method to create habit and return DB feedback & generate output about new habit as feedback to user
        row_count, return_message = self.dba.create_habit(name, status, description, is_quantifiable, periodicity,
                                                          frequency, start, end, cur_per, cur_year, quantity, unit)
        return row_count, return_message

    def delete(self, name: str) -> tuple:  # TODO: replace 3 values with 1?
        """ call delete method
        :param name: name of the habit
        :return: tuple of 3 values
        """
        output1, output2, output3 = self.dba.delete_from_db(name=name)

        return output1, output2, output3

    def deactivate(self, name: str, end: str) -> str:
        """deactivate a habit starting from a given date. All data remains, but end date is updated
        :param name: habit name
        :param end: date of deactivation = end date of the habit records
        :return: string with information about successful database actions
        """
        return_message = self.dba.deactivate(name, end)
        return return_message

    def edit(self, name: str, descr: str) -> str:
        """Transfers habit description update information to database method and returns information about successful
        update of database
        :param name: habit name
        :param descr: new habit description
        :return: string with information about successful update"""
        return_message = self.dba.edit_descr(name, descr)
        return return_message

class HabitLog(Habit):
    def __init__(self, name: str = '', description: str = '', start: datetime.date = '', end: datetime.date = '',
                 status: int = '',
                 periodicity: str = '', frequency: int = '', today: str = '', log_date: str = '', quantity='', unit='',
                 is_quantifiable=''):
        super().__init__(name, description, start, end, status, periodicity, frequency, quantity, unit,
                         is_quantifiable)
        self.log_date = log_date

    def set_streak(self, name: str, log_date: datetime.date) -> str:
        """Calculates streak for given habit and log_date and saves it to database. \n
        If possible, streaks are calculated based on previous (existing) streak data. \n
        But if this is not possible, i.e. if streaks were not entered in chronological order leading to a break
        that is unjustified then streak data needs to be cleared calculated again from the start to correct this
        :param name: habit name
        :param log_date: date of logged completion
        :return: string with information about successful DB update"""
        streak = 0
        # first, import information from habit master data, so we know which logic to use
        # also import most current record with information from habit_streaks
        habit_info, habit_streaks = self.get_active_habit_info(habit=name)
        # is_quantifiable = habit_info[3]
        periodicity = habit_info[4]
        frequency = habit_info[5]
        # quantity = habit_info[6]
        start = datetime.date.fromisoformat(habit_info[8])
        # end = habit_info[9]
        cur_streak = habit_streaks[6]
        cur_per = habit_streaks[8]
        try:
            cur_year = (habit_streaks[9])
        except ValueError:
            cur_year = 0
        streak_id = habit_streaks[0]
        streak_per = habit_streaks[10]
        valid_from = habit_streaks[3]
        log_year = str(log_date.year)
        max_log_date = datetime.date.fromisoformat(self.dba.get_latest_log_date(name=name))
        # TODO: is this still needed?
        try:
            streak_date = datetime.date(int(habit_streaks[5][0:4]), int(habit_streaks[5][5:7]),
                                        int(habit_streaks[5][8:10]))
        except TypeError:
            # streak_date = None
            # that means we need the start date of the habit, can use valid_from from streaks table
            streak_date = datetime.date(int(habit_streaks[3][0:4]), int(habit_streaks[3][5:7]),
                                        int(habit_streaks[3][8:10]))

        # fill log period and previous ("last") period dynamically depending on periodicity:
        if periodicity == 'daily':
            log_per = str(log_date)
            last_per = log_date - timedelta(days=1)

        elif periodicity == 'weekly':
            log_week = log_date.isocalendar()[1]
            log_per = str(log_week)
            last_week_d = log_date - timedelta(days=7)
            last_per = last_week_d.isocalendar()[1]

        elif periodicity == 'monthly':
            log_per = str(log_date.month)
            last_month_d = log_date - timedelta(weeks=4)
            last_per = last_month_d.month

        elif periodicity == 'yearly':
            log_per = str(log_date.year)
            last_per = log_date.year - 1

        # now check if a (new) streak was achieved
        # check for each new period (needs the least amount of data), check from start would be possible as well
        dba = DBActions()
        if log_per == cur_per and str(log_year) == cur_year and cur_per != streak_per and log_date >= max_log_date:
            # still the same period and streak has not yet been achieved - check if logged entries match the habit
            # definition: how many completions were logged for this period?
            completion_count = dba.get_habit_completion_by_single_per(name=name, log_per=log_per)
            if completion_count >= frequency:
                cur_streak += 1
                streak_per_n = log_per
            else:
                streak_per_n = 0
            no_change = 0

        elif (str(log_per) == str(cur_per) and str(log_year) == cur_year and str(cur_per) == str(streak_per)
              and log_date >= max_log_date):
            # do nothing because this period already has a streak and user logs a bonus completion
            no_change = 1

        elif str(cur_per) == str(last_per) and str(streak_per) == str(last_per) and log_date >= max_log_date:
            # new period has started -> previous period had a streak, continue counting up checking for new period
            completion_count = dba.get_habit_completion_by_single_per(name=name, log_per=log_per)
            if completion_count >= frequency:
                cur_streak += 1
                streak_per_n = log_per
                no_change = 0
            elif completion_count < frequency == 1:
                # Reset streak - but only if freq = 1 because else new logs can be created and the streak be reached
                val_to = log_date - timedelta(days=1)
                valid_from = log_date
                dba.reset_streak(id=streak_id, name=name, val_to=val_to, val_from=log_date, cur_per=log_per,
                                 cur_year=str(log_year))
                streak_per_n = 0
                cur_streak = 0
                no_change = 1
            else:
                streak_per_n = 0
                no_change = 1

        elif str(cur_per) < str(last_per) and cur_streak != 0 and log_date >= max_log_date:
            # streak has been broken -> end current streak and start new
            # end previous streak on day before streak date and start new streak record, beginning on log_date (initial)
            val_to = log_date - timedelta(days=1)
            valid_from = log_date
            dba.reset_streak(id=streak_id, name=name, val_to=val_to, val_from=log_date, cur_per=log_per,
                             cur_year=str(log_year))
            cur_streak = 0
            # calculate streak based on new record - streak can only be +1 if freq. = 1
            completion_count = dba.get_habit_completion_by_single_per(name=name, log_per=log_per)
            if completion_count >= frequency:
                cur_streak += 1
                streak_per_n = log_per
            else:
                cur_streak = 0
                streak_per_n = 0
            no_change = 0

        else:  # calculate from the beginning only of all else failed
            cur_streak = 0
            #  1. delete streaks data for this habit and recreate initial entry
            if self.dba.clear_streaks(name=name) > 0:
                self.dba.create_initial_streaks_entry(name=name, start=start, cur_per=cur_per, cur_year=str(cur_year))

            rel_pers = []   # list of relevant periods
            rel_date = []
            # 2. calculate streaks from start until all relevant periods are worked through or streak is broken
            # habit_start = datetime.date(int(start[0:4]), int(start[5:7]), int(start[8:10]))
            habit_start = start # = start of habit itself, since it is now calculated from the start
            start_test = start  # = start of habit itself, since it is now calculated from the start
            # create list of all relevant periods
            for day in range(int((max_log_date - habit_start).days) + 1):
                check_date = habit_start + datetime.timedelta(days=day)
                if periodicity == 'daily':
                    check_per = str(check_date.year) + '-' + str(check_date)                   # day
                elif periodicity == 'weekly':
                    check_per = str(check_date.year) + '-' + str(check_date.isocalendar()[1])  # week
                elif periodicity == 'monthly':
                    check_per = str(check_date.year) + '-' + check_date.month                  # month
                elif periodicity == 'yearly':
                    check_per = str(check_date.year) + '-' + check_date.year                   # year

                if check_per not in rel_pers:
                    rel_pers.append(check_per)
                    rel_date.append(str(check_date))
            rel_per_d = {'per': rel_pers, 'date_per': rel_date}
            # create df from dict   # list
            pers_df = pd.DataFrame(data=rel_per_d)  # (rel_pers, columns=['per'])

            log_count = dba.get_habit_logs_df(name=name, log_date=max_log_date)
            streak_base = pers_df.merge(log_count, how='left', on='per')
            # for each in streak_base:
            for row in streak_base.iterrows():
                # check if in each line the count is >= the master frequency, if so streak += 1
                # if int(row[1].item()) >= frequency:
                # if row[1][1] == 'NaN':
                index, series = row
                # start_test = series.get('date_per')   # start_test + datetime.timedelta(days=float(index))
                try:
                    logged_freq = int(series.get('count'))
                except ValueError:
                    logged_freq = 0
                if logged_freq >= frequency:  # int(row[1][1]) >= frequency:
                    cur_streak += 1
                    streak_per_n = str(series.get('log_per'))  # (row[1][2])  # log_per
                    cur_per = str(series.get('log_per'))    # (row[1][2])
                    cur_year = str(series.get('calyear'))  # (row[1][3])
                    streak_date_n = str(series.get('date'))  # (row[1][4])
                    no_change = 0
                else: # habit broken
                    # first, create streak record with last streak value and end date before starting from 0
                    if cur_streak > 0:  # no need to create new record if it is still 0
                        self.dba.update_streak_table(name=name, new_streak=cur_streak,
                                                     new_date=str(streak_date_n), val_from=start_test,
                                                     cur_per=str(streak_per_n), cur_year=str(cur_year),
                                                     streak_per=str(streak_per_n), valid_to=str(streak_date_n))
                        # count start date up
                        start = start + datetime.timedelta(days=1)   # log_date
                        start_test = date.fromisoformat(streak_date_n) + timedelta(days=1) # start of new init
                        cur_streak = 0
                        streak_per_n = 0

                        if periodicity == 'daily':
                            cur_per = start_test
                            cur_year = start_test.year
                        elif periodicity == 'weekly':
                            cur_per = start_test.isocalendar()[1]  # week
                            cur_year = start_test.year
                        elif periodicity == 'monthly':
                            cur_per = start_test.month  # month
                            cur_year = start_test.year
                        elif periodicity == 'yearly':
                            cur_per = start_test.year  # year
                            cur_year = start_test.year
                        # cur_per =   # str(series.get('log_per'))    # (row[1][2])
                        # cur_year =  # str(series.get('calyear'))  # (row[1][3])

                        # except:
                            # cur_per = log_per
                            # cur_year = log_year
                        # create new record starting at 0  val_to = log_date - timedelta(days=1)& valid_from = log_date
                        # valid_from = date.fromisoformat(str(series.get('per'))[5:]) + timedelta(days=1)
                        # valid_to = date.fromisoformat(str(series.get('per'))[5:]) + timedelta(days=1)
                        dba.reset_streak(id=streak_id, name=name, val_to=datetime.date.fromisoformat('2199-12-31'),
                                         val_from=start_test, cur_per=cur_per, cur_year=str(cur_year))
                        no_change = 0
                    else:
                        no_change = 1
            valid_from = start_test

        # finally update streak table
        if no_change == 0:
            dba.update_streak_table(name=name, new_streak=cur_streak, new_date=str(max_log_date), val_from=valid_from,
                                    cur_per=log_per, cur_year=log_year, streak_per=streak_per_n)
        if cur_streak > habit_streaks[6]:
            return_message = ("Well done! Your current streak for habit " + name + " was updated to " + str(cur_streak)
                              + ".")
        else:
            return_message = ("Your current streak for habit " + name + " is " + str(cur_streak) + ".")
        return return_message

    def log_completion(self, name: str, log_date: datetime.date, completed: int, quantity: float = '',
                       partial: float = '') -> tuple:
        """determines additional attributes for log record, calls DB Actions method to log record to DB, calls method
        to calculate and update streak data
        :param name: name of the habit
        :param log_date: date of logged completion
        :param completed: 1 if habit was (fully) completed
        :param quantity: logged completed quantity
        :param partial: relative completion rate
        :return: tuple of strings - (return_message for logging completion, streak_message)
        """
        # determine calendar attributes calyear, calmonth, calweek
        weekday = log_date.weekday()
        week = log_date.isocalendar()[1]
        year = log_date.year
        calyear = str(year)
        month = log_date.month
        if month < 10:
            calmonth = str(calyear) + '-0' + str(month)
        else:
            calmonth = str(calyear) + '-' + str(month)
        if week < 10:
            calweek = str(week)  # str(calyear) + '-0' + str(week)
        else:
            calweek = str(week)  # str(calyear) + '-' + str(week)

        # get periodicity of habit to fill log_per with respective info:
        dba = DBActions()
        periodicity = self.get_periodicity(habit=name, date=log_date)
        if periodicity == 'daily':
            log_per = log_date
        elif periodicity == 'weekly':
            log_per = str(week)
        elif periodicity == 'monthly':
            log_per = str(month)
        elif periodicity == 'yearly':
            log_per = str(year)

        return_message = (
            dba.insert_log(name, log_date, completed, quantity, partial, weekday, week, calweek, month, calmonth, year,
                           calyear, log_per))

        # fill streaks table
        streak_message = self.set_streak(name, log_date)

        return return_message, streak_message
