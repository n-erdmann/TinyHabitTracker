import sqlite3
import datetime
import pandas as pd


# import pyarrow


class DBActions:
    def __init__(self, db_con='habit_db'):
        """initialize the DBActions class attributes"""
        self.db_con = db_con
        pass

    @staticmethod
    def fetchall_to_list(list_in: list) -> list:
        """This helper method converts the result of a fetchall from the database (list of tuples) to a python list
        :param list_in: a list as it is returned using fetchall
        :return: list with only relevant information
        """
        return_list = []
        for item in list_in:
            return_list.append(item[0])
        return return_list

    def create_tables(self):
        """sets up the necessary db tables for creating and tracking habits
        connection db_con is habit_db by default but can be set to test_db when this method is called by test class"""
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        # create table for primary data: habit_master
        cursor.execute("""CREATE TABLE IF NOT EXISTS habit_master (
            name TEXT NOT NULL,
            status INTEGER NOT NULL,
            description TEXT,
            is_quantifiable INTEGER DEFAULT 0,
            periodicity	TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            quantity REAL,
            unit TEXT,
            start TEXT NOT NULL,
            end	TEXT DEFAULT '2199-12-31',
            PRIMARY KEY (name, start))""")

        # create table for tracking habits: habit_log
        cursor.execute("""CREATE TABLE IF NOT EXISTS habit_log (
            id INTEGER PRIMARY KEY ,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 1,
            quantity REAL,
            partial REAL,
            weekday TEXT NOT NULL,
            week TEXT not null ,
            calweek TEXT NOT NULL,
            month INTEGER NOT NULL ,
            calmonth TEXT NOT NULL,
            year INTEGER NOT NULL,
            calyear TEXT NOT NULL,
            log_per TEXT NOT NULL,
            created_on TEXT, 
            cur_streak INTEGER,
            foreign key (name) REFERENCES habit_master(name))""")

        # create table for logging streaks: habit_streaks
        cursor.execute("""CREATE TABLE IF NOT EXISTS habit_streaks (
                    id INTEGER PRIMARY KEY ,
                    name TEXT NOT NULL,
                    changed_on TEXT NOT NULL,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT NOT NULL,
                    streak_date TEXT ,
                    cur_streak INTEGER NOT NULL DEFAULT 0,
                    avg_quantity REAL NOT NULL,
                    cur_per text not null,
                    cur_year text not null ,
                    streak_per text,
                    status INTEGER NOT NULL DEFAULT 1 ,
                    foreign key (name) REFERENCES habit_master(name))""")

        db.commit()
        row_count = cursor.execute("""SELECT count(name) FROM sqlite_master WHERE type='table';""").fetchone()[0]
        cursor.close()

        if row_count == 3:  # all tables created
            self.create_view()
        return row_count

    def create_view(self):
        """creates view based on DB tables for Analytics module"""
        sql = ("CREATE VIEW IF NOT EXISTS habit_log_overview AS select prim.name as habit, "
               "prim.description as description, prim.periodicity as periodicity,"
               "prim.frequency as frequency, prim.quantity as target_quantity, hl.quantity as completed_quantity,"
               "prim.unit as unit, hl.date as log_date,"
               "hl.weekday, hl.log_per as period, hl.calmonth as month, hl.calweek as week, hl.calyear as year, "
               "hl.completed, hl.partial as partial_completion, hl.cur_streak "
               "from main.habit_master as prim"
               "left join main.habit_log hl on "
               "prim.name = hl.name and prim.start <= hl.date and prim.end >= hl.date")

        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()

    def delete_from_db(self, name: str) -> tuple:
        """deletes habits completely from all 3 DB tables
        :param name: habit name
        :return: 3 strings with return messages about deletion from habit_master, habit_log, habit_streaks
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        self.create_tables()
        cursor.execute("""DELETE FROM habit_master WHERE name = """ + "'" + str(name) + "'")
        if cursor.rowcount > 0:
            db.commit()
            return_message1 = str(cursor.rowcount) + ' row from master data was successfully deleted. \n'
        else:
            return_message1 = 'Nothing was deleted from master data - does the habit exist? \n'

        cursor.execute("""DELETE FROM habit_log WHERE name = """ + "'" + str(name) + "'")
        if cursor.rowcount > 0:
            db.commit()
            return_message2 = str(cursor.rowcount) + ' row(s) from log data were successfully deleted. \n'
        else:
            return_message2 = 'Nothing was deleted from logs. \n'

        cursor.execute("""DELETE FROM habit_streaks WHERE name = """ + "'" + str(name) + "'")
        if cursor.rowcount > 0:
            db.commit()
            return_message3 = str(cursor.rowcount) + ' row(s) from streak data were successfully deleted. \n'
        else:
            return_message3 = 'Nothing was deleted from streaks. \n'

        return return_message1, return_message2, return_message3

    def get_periodicity(self, name: str, date: datetime.date = datetime.date.today()) -> str:
        """returns the periodicity of the habit as of date from master data
        :param name: habit name
        :param date: date that periodicity is looked up for, default is today
        :return: periodicity as string
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        sql = ("SELECT periodicity from habit_master where name = " + "'" + name + "'" + " and start <= " + "'" +
               str(date) + "'" + " AND end >= " + "'" + str(date) + "'")
        periodicity = cursor.execute(sql).fetchone()[0]
        return periodicity

    def create_habit(self, name: str, status: int, description: str, is_quantifiable: int, periodicity: str,
                     frequency: int, start: datetime.date, end: datetime.date, cur_per: str = '',
                     cur_year: datetime.date.year = '', quantity: float = '', unit: str = '') -> tuple:
        """Inserts new records into habit master data table and adds initial record to streaks table
        = creates new habits
        :param name: habit name
        :param status: habit status, default = 1
        :param description: habit description
        :param is_quantifiable: flag to indicate if habit is quantifiable (1) or not (0)
        :param periodicity: habit periodicity
        :param frequency: intended frequency of habit completion
        :param start: start of tracking this habit
        :param end: end of tracking this habit, default 2199-12-31
        :param cur_per: current period of the habit, depending on periodicity and derived from start date
        :param cur_year: the year belonging to the current period, derived from start date
        :param quantity: intended quantity to complete habit, if habit is quantifiable
        :param unit: unit for quantity, optional
        :return: a tuple consisting of number of created rows (int) and return message (str)"""

        self.create_tables()
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        # create primary data record
        parameter = (name, status, description, is_quantifiable, periodicity, frequency, quantity, unit,
                     start, end)
        cursor.execute("""INSERT INTO habit_master('name', 'status', 'description', 'is_quantifiable',
            'periodicity', 'frequency', 'quantity', 'unit', 'start', 'end') 
            VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", parameter)
        rowcount = cursor.rowcount
        db.commit()  # commit master data record

        rowcount = rowcount + self.create_initial_streaks_entry(name=name, start=str(start), end=str(end),
                                                                cur_per=cur_per, cur_year=cur_year)

        # only return success message if both records have been created
        if rowcount == 2:
            db.commit()  # commit initial streak record
            db.close()
            return_message = 'Records were created successfully'

        else:
            return_message = 'Records could not be created.'
            db.close()

        return rowcount, return_message

    def create_initial_streaks_entry(self, name: str, start: str, cur_per: str, cur_year: str,
                                     end: str = '2199-12-31') -> int:
        """(Re)Creates the initial streaks record either during creation of a new habit or in streaks calculation if
        a complete recalculation of streaks from the beginning is necessary
        :param name: habit name
        :param start: start date of habit (= start date in master data)
        :param cur_per: current period derived from start date
        :param cur_year: year belonging to current period, derived from start date
        :param end: end date of validity for the habit, defaults to '2199-12-31'
        :return: rowcount (int)"""
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        # create  initial record in streaks table
        params_streak = (name, datetime.date.today(), start, end, 0, 0, cur_per, cur_year, 0)
        cursor.execute("""INSERT INTO habit_streaks('name', 'changed_on', 'valid_from', 'valid_to',
                   'cur_streak', 'avg_quantity', 'cur_per', 'cur_year', 'streak_per')
                    values(?, ?, ?, ?, ?, ?, ?, ?, ?)""", params_streak)
        if cursor.rowcount > 0:
            db.commit()
        rowcount = cursor.rowcount
        return rowcount

    def clear_streaks(self, name: str) -> int:
        """clears all active records of a given habit from habit_streaks table to recalculate streaks from the start
        :param name: habit name
        :return: rowcount (int)"""

        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        cursor.execute("""DELETE FROM habit_streaks WHERE name = """ + "'" + str(name) + "' and status = 1")
        if cursor.rowcount > 0:
            db.commit()
        rowcount = cursor.rowcount
        return rowcount

    def insert_log(self, name: str, date: datetime.date, completed: int, quantity: float, partial: float, weekday: int,
                   week: int, calweek: str, month: int, calmonth: str, year: int, calyear: str, log_per: str) -> tuple:
        """Inserts new records into habit_log table.
        :param name: habit name
        :param date: log date of completion
        :param completed: whether a habit was completed, always 1 for binary habits, only 1 for quantifiable habits if
            intended quantity was logged
        :param quantity: completed quantity for quantifiable habits
        :param partial: completion rate for quantifiable habits
        :param weekday: weekday of log date
        :param week: week of log date (int)
        :param calweek: calendar week of log date (str)
        :param month: month of log date (int)
        :param calmonth: calendar month of log date (str)
        :param year: year of log date (int)
        :param calyear: year of log date (str)
        :param log_per: relevant period of log date depending on periodicity
        :return: tuple (string with a return message about creation of DB records, row of inserted record)
        """

        self.create_tables()
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        parameter = (name, date, completed, quantity, partial, weekday, week, calweek, month, calmonth, year, calyear,
                     log_per, str(datetime.date.today()), '')
        cursor.execute("""INSERT INTO habit_log('name', 'date', 'completed', 'quantity', 'partial', 'weekday', 
                    'week', 'calweek', 'month', 'calmonth', 'year', 'calyear', 'log_per', 'created_on', 'cur_streak') 
                    VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", parameter)
        if cursor.rowcount > 0:
            db.commit()
            return_message = str(cursor.rowcount) + ' log record was created successfully'
            rowid = cursor.lastrowid
            cursor.close()
            return return_message, rowid
        else:
            cursor.close()
            return 'log record could not be created.', 0

    def update_log(self, name, rowid, streak):
        """Updates the cur_streak value for the habit being currently logged"""
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        cursor.execute("UPDATE habit_log SET cur_streak = " + str(streak) +
                       " WHERE name =  " + "'" + str(name) + "'" + " and rowid = " + "'" + str(rowid) + "'")
        db.commit()
        cursor.close()

    def edit_descr(self, name: str, descr: str) -> str:
        """updates a habit's description
        :param name: habit name
        :param descr: habit description
        :return: string with return message about updated records
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        sql = ("""UPDATE habit_master SET description = """ + "'" + str(descr) + "'" + """ WHERE name = """ + "'"
               + str(name)) + "'"
        cursor.execute(sql)

        if cursor.rowcount > 0:
            db.commit()
            return_message = str(cursor.rowcount) + ' record(s) was updated'
            return return_message
        else:
            return 'Nothing could be updated.'

    def get_active_habit_info(self, name: str, today: datetime.date = datetime.date.today()) -> list:
        """returns all master data about a habit in its currently active state in a list
        :param name: habit name
        :param today: date, default: today's date
        :return: list with all information from master data table
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        # first the currently active record of the habit needs to be read, so it can be "copied"
        sql = ("""SELECT * FROM habit_master WHERE name = """ + "'" + str(name) + "'" + """ AND start <= """ + "'"
               + str(today) + "'" + """ AND end >= """ + "'" + str(today) + "'")
        habit_info = cursor.execute(sql).fetchone()
        return habit_info

    def deactivate(self, name: str, end: str) -> str:
        """Deactivate a given habit
        :param name: str, name of the habit to be deactivated
        :param end: date for deactivation
        :return: string with info on count of updated records
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        sql = ("""UPDATE habit_master SET status = 0, end = """ + "'" + str(
            end) + "'" + """ WHERE name = """ + "'" + str(name)
               + "'")
        cursor.execute(sql)

        sql = ("""UPDATE habit_streaks SET status = 0, valid_to = """ + "'" + str(
            end) + "'" + """ WHERE name = """ + "'" +
               str(name) + "' AND valid_to = '2199-12-31'")
        cursor.execute(sql)

        if cursor.rowcount > 0:
            db.commit()
            return_message = str(cursor.rowcount) + ' record was updated.'
        else:
            return_message = 'Nothing could be updated.'

        return return_message

    def delete_tables(self):
        """deletes DB tables and DB view;
        db_con is habit_db by default but can be set to test_db when this method is called by test class"""
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        # drop table for master data: habit_master
        cursor.execute("""DROP TABLE IF EXISTS habit_master;""")

        # drop table for tracking habits: habit_log
        cursor.execute("""DROP TABLE IF EXISTS habit_log;""")

        # drop table for logging streaks: habit_streaks
        cursor.execute("""DROP TABLE IF EXISTS habit_streaks;""")

        # drop view for analysis
        cursor.execute("""DROP VIEW IF EXISTS habit_log_overview;""")

        db.commit()
        row_count = cursor.execute("""SELECT count(name) FROM sqlite_master WHERE type='table';""").fetchone()[0]
        cursor.close()

        return row_count

    def get_active_habits_list(self, today: datetime.date = datetime.date.today(), is_quan_only: bool = False) -> tuple:
        """Retrieves a list of existing active habits from primary data, can be restricted to only quantifiable habits.
        :param today: Date for selecting active habits, default is today
        :param is_quan_only: flag to indicate whether all or only quantifiable habits should be returned
        :return: tuple (list of habits, dict of habits with description)
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        if is_quan_only:
            sql1 = ("SELECT   DISTINCT name "
                    "  FROM   habit_master "
                    " WHERE status = 1 AND start <= " + "'" + str(today) + "'" + " AND end >= " + "'" + str(today) + "'"
                    + "AND is_quantifiable = 1 ORDER BY name")

            sql2 = ("SELECT   DISTINCT name, description "
                    "  FROM   habit_master "
                    " WHERE status = 1 AND start <= " + "'" + str(today) + "'" + " AND end >= " + "'" + str(today) + "'"
                    + "AND is_quantifiable = 1 ORDER BY name")
        else:
            sql1 = ("SELECT   DISTINCT name "
                    "  FROM   habit_master "
                    " WHERE status = 1 AND start <= " + "'" + str(today) + "'" + " AND end >= " + "'" + str(today) + "'"
                    + " ORDER BY name")

            sql2 = ("SELECT   DISTINCT name, description "
                    "  FROM   habit_master "
                    " WHERE status = 1 AND start <= " + "'" + str(today) + "'" + " AND end >= " + "'" + str(today) + "'"
                    + " ORDER BY name")

        # fill habit_list:
        habit_list = self.fetchall_to_list(cursor.execute(sql1).fetchall())

        # fill dictionary:
        temp_list = cursor.execute(sql2).fetchall()
        descr_list = []
        for item in temp_list:
            descr_list.append([item[0], item[1]])

        habit_dict = {}
        n = 1
        for habit in descr_list:
            habit_dict[habit[0]] = habit[1]

        return habit_list, habit_dict

    def get_habit_completion_by_single_per(self, name: str, log_per: str) -> int:
        """returns count of habit completion in a single log period
        :param name: habit name
        :param log_per: relevant period for logging completions (day, week, month or year)
        :return: sum of logged completions for the habit (int)
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        sql = ("""SELECT SUM(completed) as count FROM habit_log WHERE name = """ + "'" + str(name) +
               "' AND log_per = """ + "'" + str(log_per) + "'")
        habit_count = cursor.execute(sql).fetchone()[0]
        return habit_count

    def get_habit_logs_by_per_int(self, name: str, log_per_f: str, log_per_t: str) -> object:
        """returns count of habit completion in an interval of log periods as dataframe
        :param name:habit name
        :param log_per_f: from value of relevant period for logging completions (day, week, month or year)
        :param log_per_t: to value of relevant period for logging completions
        :return: dataframe of sum of completions per period
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        sql = ("""SELECT SUM(completed) as count, log_per as cur_per FROM habit_log WHERE name = """ + "'" + str(name) +
               "' AND log_per <= """ + "'" + str(log_per_f) + "' AND log_per <= " + "'" + log_per_t +
               "' GROUP BY cur_per ORDER BY cur_per")
        # habit_count = cursor.execute(sql).fetchall()
        # habit_log_df = pd.read_sql_query(sql, db_con)
        query = cursor.execute(sql)
        cols = [column[0] for column in query.description]
        habit_count_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
        return habit_count_df

    def get_habit_logs_df(self, name: str, log_date: datetime.date) -> object:
        """retrieves the count of completions for habit name for dates <= log_date
        :param name: habit name
        :param log_date: max date for habit logs to be evaluated
        :return: dataframe with number of completed habits per relevant period;
            columns: count, per (=concatenated year-log_per), log_per, calyear, date.
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        sql = ("""SELECT SUM(completed) as count, (calyear || '-' || log_per) as per, log_per, calyear, 
        MAX(date) as date, id, cur_streak FROM habit_log where name = """ + "'" + str(name) + "'" """AND date <= """ +
               "'" + str(log_date) + "' AND completed = 1 group by per")
        habit_log = cursor.execute(sql).fetchall()
        # habit_log_df = pd.read_sql_query(sql, db_con)
        query = cursor.execute(sql)
        cols = [column[0] for column in query.description]
        habit_log_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)

        return habit_log_df

    def get_latest_log_date(self, name: str) -> str:
        """retrieves the maximum log date for a habit in iso format
        :param name: habit name
        :return: maximum log date in iso format as a string
        """
        sql = ("""SELECT MAX(date) as max_date FROM habit_log where name = """ + "'" + str(name) + "'""")

        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        max_date = cursor.execute(sql).fetchone()[0]
        return max_date

    def update_streak_table(self, name: str, new_streak: int, new_date: str, val_from: str, cur_per: str, cur_year: str,
                            streak_per: str, today: datetime.date = datetime.date.today(), valid_to: str = '') -> int:
        """
        Updates habits_streak table with new values for current streak, including new date values.
        :param name: Habit name.
        :param new_streak: New streak value
        :param new_date: new streak date
        :param val_from: start of the current streak
        :param cur_per: currently evaluated period
        :param cur_year: year of the currently evaluated period
        :param streak_per: The period in which the streak was last updated
        :param today: current date
        :param valid_to: end date of the current streak
        :return: rowcount (int)
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        if valid_to == '':
            sql = ("UPDATE habit_streaks set cur_streak = " + str(new_streak) + ", streak_date = " + "'" +
                   str(new_date) + "'" + ", changed_on = " + "'" + str(today) + "'" + ", cur_per = " + "'" +
                   str(cur_per) + "'" + ", cur_year = " + "'" + str(cur_year) + "'" + ", streak_per = " + "'" +
                   str(streak_per) + "' where name = " + "'" + str(name) + "' and valid_from = " + "'" +
                   str(val_from) + "'")
        else:
            sql = ("UPDATE habit_streaks set cur_streak = " + str(new_streak) + ", streak_date = " + "'" +
                   str(new_date) + "'" + ", changed_on = " + "'" + str(today) + "'" + ", cur_per = " + "'" +
                   str(cur_per) + "'" + ", cur_year = " + "'" + str(cur_year) + "'" + ", streak_per = " + "'" +
                   str(streak_per) + "', valid_to = " + "'" + str(valid_to) + "' where name = " + "'" + str(name) +
                   "' and valid_from = " + "'" + str(val_from) + "'")
        cursor.execute(sql)
        rowcount = cursor.rowcount
        db.commit()
        return rowcount

    def reset_streak(self, id: int, name: str, val_to: datetime.date, val_from: datetime.date, cur_per: str,
                     cur_year: str) -> int:
        """
        Resets streak records after current streak has been broken: ends the current streak on the val_to value and
        starts a new streak from the val_from value with initial streak = 0
        :param name: habit name
        :param val_to: end if validity of streak record after broken streak
        :param val_from: start if validity of new streak record after broken streak
        :param cur_per: current period of the starting new streak record
        :param cur_year: year of the current period of new streak record
        :return: rowcount (int)
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        end = ("UPDATE habit_streaks set valid_to = " + "'" + str(val_to) + "' where id = " + str(id) +
               " AND name = " + "'" + str(name) + "' and valid_to = '2199-12-31'")
        cursor.execute(end)

        params_start = (name, datetime.date.today(), val_from, "2199-12-31", 0, 0, cur_per, cur_year, None)
        cursor.execute("""INSERT INTO habit_streaks('name', 'changed_on', 'valid_from', 'valid_to',
            'cur_streak', 'avg_quantity', 'cur_per', 'cur_year', 'streak_per')
             values(?, ?, ?, ?, ?, ?, ?, ?, ?)""", params_start)
        rowcount = cursor.rowcount
        db.commit()
        return rowcount

    def get_habits_by_periodicity(self, periodicity: str, current: bool = True):
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        today = datetime.date.today()
        if current:
            sql = ("SELECT   DISTINCT name "
                   "  FROM   habit_master "
                   " WHERE status = 1 AND start <= " + "'" + str(today) + "'" + " AND end >= " + "'" + str(today) + "'"
                   + "AND periodicity = " + "'" + str(periodicity) + "' ORDER BY name")
        else:
            sql = ("SELECT   DISTINCT name "
                   "  FROM   habit_master "
                   " WHERE start <= " + "'" + str(today) + "'" + " AND end >= " + "'" + str(today) + "'"
                   + "AND periodicity = " + "'" + str(periodicity) + "' ORDER BY name")

        return_list = self.fetchall_to_list(cursor.execute(sql).fetchall())
        return return_list

    def get_max_streak(self, name: str = '', current: bool = False) -> tuple:
        """
        returns max streak for the given habit and the date this streak occurred
        :param name: habit name
        :param current: True of only habits valid today should be considered, default: False
        :return: tuple with 3 values (habit, streak, streak_date)
        """
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        today = datetime.date.today()
        if current:
            if name:
                sql = ("SELECT name, MAX(cur_streak), streak_date as streak "
                       "  FROM   habit_streaks "
                       " WHERE valid_from <= " + "'" + str(today) + "'" + " AND valid_to >= " + "'" + str(today) + "'"
                       + "AND name = " + "'" + str(name) + "'")
            else:
                sql = ("SELECT name, MAX(cur_streak), streak_date as streak "
                       "  FROM   habit_streaks "
                       " WHERE valid_from <= " + "'" + str(today) + "'" + " AND valid_to >= " + "'" + str(today) + "'")
        else:
            if name:
                sql = ("SELECT name, MAX(cur_streak), streak_date as streak "
                       "  FROM   habit_streaks "
                       " WHERE name = " + "'" + str(name) + "'")
            else:
                sql = ("SELECT name, MAX(cur_streak), streak_date as streak "
                       "  FROM   habit_streaks ")

        habit_streak = (
            cursor.execute(sql).fetchone())
        # descr_list = (cursor.execute(sql).fetchall())
        # since habit_list contains a list of tuples a regular list needs to be created:
        habit = habit_streak[0]
        streak = habit_streak[1]
        streak_date = habit_streak[2]
        return habit, streak, streak_date

    def count_logs(self):
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        sql = ("SELECT count(id) FROM habit_log")
        log_count = (cursor.execute(sql).fetchone())[0]
        return log_count

    def get_active_habit_streak(self, name: str) -> list:
        """returns most current streak data for a habit in a list"""
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        sql = ("""SELECT * FROM habit_streaks WHERE name = """ + "'" + str(name) + "'" +
               """ AND valid_to = '2199-12-31'""")
        habit_streaks = cursor.execute(sql).fetchone()
        return habit_streaks

    def get_row_count_by_habit(self, name: str, table: str, col: str) -> int:
        """returns most current streak data for a habit in a list"""
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        sql = ("""SELECT count(""" + "'" + str(col) + "'" + """) FROM """ + "'" + str(table) + "'" +
               """ WHERE name = """ + "'" + str(name) + "'")
        row_count = cursor.execute(sql).fetchone()[0]
        return row_count

    def get_quan(self, name: str, date_from: datetime.date, date_to: datetime.date) -> bool:
        """Returns True if habit was defined as quantifiable in the given date range, else False"""
        sql = ("SELECT MAX(is_quantifiable) as is_quan FROM habit_master where name = " + "'" + str(name) + "'" +
               " and end >= " + "'" + str(date_from) + "'")

        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        is_quan = cursor.execute(sql).fetchone()[0]

        if is_quan == 0:
            return False
        else:
            return True

    def get_log_overview_by_habit_df(self, name: str, limit: int = 35) -> object:
        """returns overview of one habit's logs and streaks as dataframe"""
        period = self.get_periodicity(name)

        if period == 'daily':
            date_from = datetime.date.today() - datetime.timedelta(days=35)
            is_quan = self.get_quan(name, date_from=date_from, date_to=datetime.date.today())
            if is_quan:
                sql = ("SELECT log_date as 'log date', sum(completed) as completed, "
                       "avg(completed_quantity) as 'avg quantity',"
                       "(avg(partial_completion)*100 ||'%') as 'avg completion (%)', weekday, week, month, "
                       "cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))
            else:
                sql = ("SELECT log_date as 'log date', sum(completed) as completed, weekday, week, month, "
                       "cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))

        elif period == 'weekly':
            date_from = datetime.date.today() - datetime.timedelta(weeks=35)
            is_quan = self.get_quan(name, date_from=date_from, date_to=datetime.date.today())
            if is_quan:
                sql = ("SELECT period, log_date as 'log date', sum(completed) as completed, "
                       "avg(completed_quantity) as 'avg quantity',"
                       "(avg(partial_completion)*100 ||'%') as 'avg completion (%)', weekday, week, month, "
                       "cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))
            else:
                sql = ("SELECT period, log_date as 'log date', weekday, week, month, cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))

        elif period == 'monthly':
            date_from = datetime.date.today() - datetime.timedelta(weeks=140)
            is_quan = self.get_quan(name, date_from=date_from, date_to=datetime.date.today())
            if is_quan:
                sql = ("SELECT period, log_date as 'log date', sum(completed) as completed, "
                       "avg(completed_quantity) as 'avg quantity',"
                       "(avg(partial_completion)*100 ||'%') as 'avg completion (%)', weekday, week, month, "
                       "cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))
            else:
                sql = ("SELECT period, log_date as 'log date', weekday, week, month, cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))

        elif period == 'yearly':
            date_from = datetime.date.today() - datetime.timedelta(weeks=260)
            is_quan = self.get_quan(name, date_from=date_from, date_to=datetime.date.today())
            if is_quan:
                sql = ("SELECT period, log_date as 'log date', sum(completed) as completed, "
                       "avg(completed_quantity) as 'avg quantity',"
                       "(avg(partial_completion)*100 ||'%') as 'avg completion (%)', cur_streak as streak "
                       "FROM habit_log_overview WHERE habit = " + "'" + str(name) +
                       "'" + " GROUP BY log_date ORDER by log_date desc LIMIT " + str(limit))
            else:
                sql = ("SELECT period, log_date as 'log date', cur_streak as streak FROM habit_log_overview "
                       "WHERE habit = " + "'" + str(name) + "'" + " GROUP BY log_date ORDER by log_date desc LIMIT "
                       + str(limit))

        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()

        query = cursor.execute(sql)
        cols = [column[0] for column in query.description]
        habit_overview_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)

        return habit_overview_df

    def execute_analytics_sql(self, sql, list: bool, df: bool):
        db = sqlite3.connect(self.db_con)
        cursor = db.cursor()
        if df:
            query = cursor.execute(sql)
            cols = [column[0] for column in query.description]
            result_df = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
            return result_df
        elif list:
            result_list = cursor.execute(sql).fetchall()
            return result_list

