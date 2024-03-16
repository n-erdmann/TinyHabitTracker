import TinyCLI


def current_habits():
    """
    Prints a list of all currently tracked habits on the screen
    """
    dba = CLI3.DBActions()
    cur_habits = dba.get_active_habits_list()[1]
    print("These are your currently active habits: ")
    print("---------------------------------------")
    for habit in cur_habits.keys():
        print(habit, ' - ', cur_habits[habit])


def habits_by_periodicity(periodicity: str, current: bool = True):  # TODO: add unit test for this
    """
    returns alle habits with the same periodicity, by default only currently active habits are considered,
    habits are printed on screen
    :param periodicity: the periodicity of choice
    :param current: True if only current habits are to be displayed, False for all habits
    """
    dba = CLI3.DBActions()
    habits = dba.get_habits_by_periodicity(periodicity=periodicity, current=current)
    if current:
        print("These are your currently active habits with periodicity " + periodicity + ":")
        print("-------------------------------------------------------------------------")
    else:
        print("These are your habits with periodicity " + periodicity + ":")
    for habit in habits:
        print(habit)


def longest_streak(name: str = '', current: bool = False):
    dba = CLI3.DBActions()
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


def overview_by_month(calmonth: str):
    pass  # TODO: overview of logged habits in the last month, achieved streaks...


def logs_by_habit(habit: str):
    """Give an overview of logged activity for a chosen habit depending on habit's periodicity"""
    # TODO: Separate output by quantifiable and binary habits
    dba = CLI3.DBActions()
    logs_overview = dba.get_log_overview_by_habit_df(habit)
    import pandas as pd
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 1000)
    print(logs_overview)


def explore_data():  # TODO: Just an idea, is this feasable?
    """
    Lets user explore their data more flexibly by exposing parameter inputs and querying database views with them
    """
    pass

