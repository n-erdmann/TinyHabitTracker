import datetime
from datetime import date

import pandas as pd

import TinyCLI

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

def current_habits():
    """
    Prints a list of all currently tracked habits on the screen
    """
    dba = TinyCLI.DBActions()
    cur_habits = dba.get_active_habits_list()[1]
    print("These are your currently active habits: ")
    print("---------------------------------------")
    for habit in cur_habits.keys():
        print(habit, ' - ', cur_habits[habit])


def habits_by_periodicity(periodicity: str, current: bool = True):  # TODO: add unit test for this?
    """
    returns alle habits with the same periodicity, by default only currently active habits are considered,
    habits are printed on screen
    :param periodicity: the periodicity of choice
    :param current: True if only current habits are to be displayed, False for all habits
    """
    dba = TinyCLI.DBActions()
    habits = dba.get_habits_by_periodicity(periodicity=periodicity, current=current)
    if current:
        print("These are your currently active habits with periodicity " + periodicity + ":")
        print("-------------------------------------------------------------------------")
    else:
        print("These are your habits with periodicity " + periodicity + ":")
    for habit in habits:
        print(habit)


def longest_streak(name: str = '', current: bool = False):
    dba = TinyCLI.DBActions()
    habit, streak, streak_date = dba.get_max_streak(name=name, current=current)
    if current:
        if name:
            print("The current streak for " + name + " is " + str(streak) + " and was recorded on " + str(streak_date)
                  + ".")
        else:
            print("The longest current streak of all habits belongs to " + habit + " and is " + str(streak) +
                  " and was recorded on " + str(streak_date) + ".")
    else:
        if name:
            print("The longest streak for " + name + " is " + str(streak) + " and was recorded on " + str(streak_date)
                  + ".")
        else:
            print("The longest streak of all time belongs to " + habit + " and is " + str(streak) +
                  " and was recorded on " + str(streak_date) + ".")


def overview_by_habit(habit: str):
    pass
    # TODO: provide an overview with general info about the habit: start date, how many completions, streaks,
    #  cumulated quantity if quant, logs in the last 2 weeks, most active weekday for this habit...

    # First, collect the data
    dba = TinyCLI.DBActions()

    # habits created or rescheduled
    is_quan = dba.get_quan(name=habit, date_from=date.fromisoformat('1900-01-01'),
                           date_to=date.fromisoformat('2199-12-31'))
    if is_quan:
        sql = ("SELECT start, name as habit, description, periodicity, frequency, quantity, unit from habit_master "
               "where name = " + "'" + str(habit) + "'")
    else:
        sql = ("SELECT start, name as habit, description, periodicity, frequency from habit_master "
               "where name = " + "'" + str(habit) + "'")
    primary_df = dba.execute_analytics_sql(sql=sql, list=False, df=True)

    # log count
    if is_quan:
        sql1 = ("SELECT habit, year, month, week, count(completed) as 'log count', sum(completed) as completions, "
                "avg(partial_completion)*100 as 'completion %)' from habit_log_overview "
                "where habit = " + "'" + str(habit) + "' group by year, month, week")
    else:
        sql1 = ("SELECT habit, year, month, week, count(completed) as 'log count', sum(completed) as completions "
                "from habit_log_overview "
                "where habit = " + "'" + str(habit) + "' group by year, month, week")
    logs_df = dba.execute_analytics_sql(sql=sql1, list=False, df=True)

    sql_count = ("select count(id) from habit_log where name = " + "'" + str(habit) + "'")
    count_of_logs = dba.execute_analytics_sql(sql=sql_count, list=True, df=False)[0]

    # most active weekday
    sql2 = ("SELECT weekday, count(completed) as 'log count' from habit_log_overview "
            "where habit = " + "'" + str(habit) + "' group by weekday order by count(completed) desc ")
    weekday, count = dba.execute_analytics_sql(sql=sql2, list=True, df=False)[0]

    # quantities # TODO

    # all streaks, most current on top
    sql3 = ("""SELECT name as habit, valid_from as 'start', valid_to as 'end', streak_date as 'streak date', 
    cur_streak as streak, cur_per as period FROM habit_streaks WHERE name = """ + "'" + str(habit) +
            "' order by streak_date desc limit 100")

    # max streak (all time)
    streak, streak_date = dba.get_max_streak(name=habit)[1:]

    # Now, print information on screen:

    print("Main Menu -> Analyze Habits -> Overview by habit\n ")
    print("---------------------------------------")
    print(" Here is your overview for " + str(habit) + ":")
    print("---------------------------------------\n ")

    print("\n Primary data: ")
    print("---------------------------------\n ")

    print("\n Log count: ")
    print("---------------------------------\n ")
    # log count
    # most active weekday
    # quantity (avg and cumulated) of quan

    print("\n Streaks: ")
    print("---------------------------------\n ")
    # all streaks

    # some diagram?


def overview_by_month(calmonth: str):
    """provides an overview of all habits within a given month including, created or rescheduled habits, log count
    and achieved streaks"""
    start = calmonth + '-01'
    next_month = date.fromisoformat(start).month + 1
    if 1 < next_month < 10:
        end_iso = str(calmonth[:4] + "-0" + str(next_month) + '-01')
    elif next_month > 10:
        end_iso = str(calmonth[:4] + "-" + str(next_month) + '-01')
    elif next_month == 1:
        next_year = str(int(calmonth[:4]) + 1)
        end_iso = str(next_year + "-" + str(next_month) + '-01')
    end = str(date.fromisoformat(end_iso) - datetime.timedelta(days=1))

    # First, collect the data
    dba = TinyCLI.DBActions()

    # habits created or rescheduled
    sql = ("SELECT start, name as habit, description, periodicity, frequency, quantity, unit from habit_master "
           "where start >= " + "'" + str(start) + "' and start <= " + "'" + str(end) + "'")
    created_df = dba.execute_analytics_sql(sql=sql, list=False, df=True)
    count_habits = len(created_df)

    # count of logs per habit
    sql1 = ("SELECT habit, description, count(completed) as 'log count', sum(completed) as completions, "
            "avg(partial_completion)*100 as 'completion %)' from habit_log_overview "
            "where log_date >= " + "'" + str(start) + "' and log_date <= " + "'" + str(end) + "' group by habit")
    logs_df = dba.execute_analytics_sql(sql=sql1, list=False, df=True)

    sql_count = ("select count(id) from habit_log where date >= " + "'" + str(start) + "' and date <= " + "'" +
                 str(end) + "' ")
    count_of_logs = dba.execute_analytics_sql(sql=sql_count, list=True, df=False)[0]

    # streaks achieved
    # sql2 = ("SELECT MAX (streak_date), name, cur_streak from habit_streaks where cur_streak > 0 and streak_date >= " +
    #         "'" + str(start) + "' and streak_date <= " + "'" + str(end) + "' group by name")
    sql2 = ("SELECT habit, log_date, MAX(cur_streak) as 'highest streak' from habit_log_overview where cur_streak > 0 "
            "and log_date >= " +
            "'" + str(start) + "' and log_date <= " + "'" + str(end) + "' group by habit")
    streaks_df = dba.execute_analytics_sql(sql=sql2, list=False, df=True)
    count_streaks = len(streaks_df)

    # most active weekday:
    sql2 = ("SELECT weekday, count(completed) as 'log count' from habit_log_overview "
            "where log_date >= " + "'" + str(start) + "' and log_date <= " + "'" + str(end) +
            "' group by weekday order by count(completed) desc ")
    weekday, count = dba.execute_analytics_sql(sql=sql2, list=True, df=False)[0]

    # print infos on screen:
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 1000)
    print("Main Menu -> Analyze Habits -> Overview by month\n ")
    print("------------------------------------")
    print(" Here is your overview for " + str(calmonth) + ":")
    print("------------------------------------\n ")

    print("\n Created or rescheduled habits: ")
    print("---------------------------------\n ")
    if count_habits == 0:
        print("You did not create new or reschedule existing habits in " + calmonth + ".\n")
    else:
        print("In " + calmonth + " you created or rescheduled " + str(count_habits) + " habits: \n")
        print(created_df)

    print("\n\n Logged habit completions: ")
    print("---------------------------------\n ")
    if count_of_logs == 0:
        print("You did not log any habit completions in " + calmonth + ".\n")
    else:
        print("In " + calmonth + " you created " + str(count_of_logs) + " log entries: \n")
        print(logs_df)
        print("\n The most active weekday was " + weekday + " with  a total of " + str(count) + " logs.")
        # TODO It can be several days with the same count - implement something for this

    print("\n\n Highest streaks achieved: ")
    print("---------------------------------\n ")
    if count_streaks == 0:
        print("You did not achieve a streak in " + calmonth + ".\n")
    else:
        print("In " + calmonth + " you achieved streaks for " + str(count_streaks) + " habits. \n"
              "These are the highest streaks for those habits in " + calmonth + ":  \n")
        print(streaks_df)


def logs_by_habit(habit: str, limit: int = ''):
    """Give an overview of logged activity for a chosen habit depending on habit's periodicity
    Without limit specification the dba method's limit of 35 records will be returned"""
    dba = TinyCLI.DBActions()
    if limit == '':
        logs_overview = dba.get_log_overview_by_habit_df(habit)
    else:
        logs_overview = dba.get_log_overview_by_habit_df(habit, limit=limit)

    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 1000)
    print(logs_overview)


