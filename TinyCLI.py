# Import the necessary packages
import datetime
import os
from datetime import date

# from pynput import keyboard
import questionary
from prompt_toolkit.output.win32 import NoConsoleScreenBufferError

import Analyze
from DBActions import DBActions
from Habit import Habit, HabitMaster, HabitLog


class CLI:
    # TODO: option to return to submenu from any point?
    def __init__(self, dba=DBActions(), h=Habit(), hm=HabitMaster(), hl=HabitLog()):
        self.dba = dba
        self.hm = hm
        self.hl = hl
        self.h = h
        self.main_menu_l = ["Log Habit", "Manage Habits", "Analyze Habits", "About Tiny Habit Tracker", 'Exit']
        self.main_menu_d = {1: "Log Habit",
                            2: "Manage Habits",
                            3: "Analyze Habits",
                            4: "About Tiny Habit Tracker",
                            0: 'Exit'}
        self.sub_man_d = {1: "Create a new Habit",
                          2: "Edit Habit Description",
                          3: "Reschedule Habit",
                          4: "Deactivate Habit",
                          5: "Delete Habit",
                          0: "Return to Main Menu"}
        self.sub_man_l = ["Create a new Habit", "Edit Habit Description", "Reschedule Habit", "Deactivate Habit",
                          "Return to Main Menu"]
        self.sub_ana_d = {1: "List all currently tracked habits",
                          2: "Habits by periodicity",
                          3: "Longest streak of all habits",
                          4: "Longest streak for a given habit",
                          5: "Overview of a given habit",
                          6: "Overview by month",
                          7: "View logs by habit",
                          0: "Return to Main Menu"}
        self.sub_ana_l = ["List all currently tracked habits",
                          "Habits by periodicity",
                          "Longest streak of all habits",
                          "Longest streak for a given habit",
                          "Overview of a given habit",
                          "Overview by month",
                          "View logs by habit",
                          "Return to Main Menu"]

    @staticmethod
    def clear_screen():
        """clears the screen after completion of user actions"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def you_are_here(here: str):
        """prints a two line header to indicate to the user where in the menu they are right now
        ---
        here: string of what should be printed
        ---
        call this method from submenus and option methods"""
        if here != '':
            print(here.title())
            print()

    @staticmethod
    def show_menu_from_dict(options: dict, subtitle: str, here: str = '') -> int:
        """prints the respective menu on user's screen
        options: represents the menu to be printed
        subtitle: subtitle to be printed, i.e. the submenu name
        here: optional, to be passed to you_are_here_function
        :param options: dictionary of options with int as keys and string as values
        :param subtitle: string to be written above the options
        :param here: optional string to be passed to you_are_here, representing the menu the user is currently in
        """
        for option in options.keys():
            print(option, ' - ', options[option])
        selection = ''
        try:
            selection = int(input("Please choose among these options by entering their number! ->"))
        except ValueError:
            print('Wrong input. Please enter a number from the menu list!')
        return selection

    def print_header(self, here: str = '', subtitle: str = ''):
        self.clear_screen()
        print("Tiny Habit Tracker")
        print("~ ~ ~ Improve your habits one step at a time :) ~ ~ ~")
        print()
        self.you_are_here(here)
        print(subtitle)

    def print_menu(self, options_dict: dict, options_list: list, here: str = '', subtitle: str = '',
                   message: str = "Please choose among the following options"):
        self.print_header(here=here, subtitle=subtitle)

        try:
            sub_q = questionary.select(message=message, choices=options_list)
            sub_selection = sub_q.ask()
            here = here + " -> " + sub_selection
        except NoConsoleScreenBufferError:
            sub_selection = self.show_menu_from_dict(options=options_dict, subtitle=subtitle)
            here = here + " -> " + options_dict.get(sub_selection)
        return sub_selection, here

    def main_menu(self) -> None:
        """Creates the main menu for the habit tracker - options are represented in the local dictionary 'main' that
        can be extended easily with new options. Exit should always remain 0 to make it user-friendly
        This menu method has no return, it calls specified methods or submenus depending on user input"""

        subtitle = "Main Menu"
        # print main menu to screen
        selection, here = self.print_menu(options_dict=self.main_menu_d, options_list=self.main_menu_l,
                                          subtitle=subtitle)

        if selection == 1 or selection == "Log Habit":
            self.log_input()
        elif selection == 2 or selection == "Manage Habits":
            self.sub_manage()
        elif selection == 3 or selection == "Analyze Habits":
            self.sub_analyze()
        elif selection == 4 or selection == "About Tiny Habit Tracker":
            print("Dummy: About Tiny Habit Tracker")
            # TODO!!! create an info page about the logic of THT
            #  (things like week = calendar week, starting on Monday... or tips for using the app)
        elif selection == 0 or selection == 'Exit':
            self.clear_screen()
            print("Exiting...\n")
            print("I hope you enjoyed using Tiny Habit Tracker \n")
            print("Have a nice day!")
            exit()

    def sub_manage(self):
        """creates the 'manage habits' submenu - options are represented in the local dictionary 'sub_man' that
        can be extended easily with new options. Exit=return to the main menu should always remain 0 to make it
        user-friendly. \n
        This menu method has no return, it calls specified methods depending on user input"""

        subtitle = "Manage Habits"
        here = "Main Menu -> Manage Habits"
        # print main menu to screen
        sub_selection, here = self.print_menu(options_dict=self.sub_man_d, options_list=self.sub_man_l,
                                              subtitle=subtitle, here=here)

        self.clear_screen()
        self.you_are_here(here=here)

        if sub_selection == 1 or sub_selection == "Create a new Habit":  # create habit
            return_message = self.create_input()
            print(return_message)
            input("Press enter to return to the submenu")
            # call submenu again = return to submenu after finishing
            self.sub_manage()

        elif sub_selection == 2 or sub_selection == "Edit Habit Description":  # edit description
            return_message = self.edit_input()
            print(return_message)
            input("Press enter to return to the submenu")
            # call submenu again = return to submenu after finishing
            self.sub_manage()

        elif sub_selection == 3 or sub_selection == "Reschedule Habit":  # reschedule habit
            return_message = self.reschedule_input()
            print(return_message)
            input('Press enter to return to the previous menu ')
            # call submenu again = return to submenu after finishing
            self.sub_manage()

        elif sub_selection == 4 or sub_selection == "Deactivate Habit":  # deactivate habit
            return_message = self.deactivate_input()
            print(return_message)
            input('Press enter to return to the previous menu ')
            # call submenu again = return to submenu after finishing
            self.sub_manage()

        elif sub_selection == 5 or sub_selection == "Delete Habit":  # delete habit
            return_message = self.delete_input()
            print(return_message)
            input('Press enter to return to the previous menu ')
            # call submenu again = return to submenu after finishing
            self.sub_manage()

        elif sub_selection == 0 or sub_selection == "Return to Main Menu":  # return to main menu
            dummy = 1
            return dummy

    def log_input(self) -> None:
        """
        Collects user input for logging completion and displays message about successful creation of log entry
        """
        here = "Main Menu -> Log Habit"
        self.you_are_here(here=here)

        habit = self.choose_habit(message='Please choose which habit you want to log: ')

        log_date = self.choose_date(message="Please indicate the day you want to log (YYY-MM-DD) or leave blank "
                                            "to log today ->")

        habit_info = self.h.get_active_habit_info(habit, streaks=False)

        if habit_info[3] == 1:
            text = "The habit '" + habit + "' is quantifiable. How many " + habit_info[7] + " do you want to log?"
            quantity = input(text)
            try:
                quantity = float(quantity)
            except ValueError:
                quantity = input("Sorry, this is not a number. Please try again with an integer or decimal")
                quantity = float(quantity)

            partial = quantity / habit_info[6]
            if quantity >= habit_info[6]:
                completed = 1
            else:
                completed = 0
        else:
            quantity = partial = None
            completed = 1

        print(self.hl.log_completion(name=habit, log_date=log_date, completed=completed, quantity=quantity,
                                     partial=partial))
        print()
        input("Press any key to continue...")

    def create_input(self) -> str:
        """Collects all the inputs needed from the user to create new habit
        These variables are then transferred to create habit method from habit class. Feedback about the
        creation of records is forwarded to calling class in a string.

        :return: string """

        # name & description
        habit_name = input("Enter Habit Name: ")
        description = input("Enter Habit Description: ")

        # start and end dates, status
        start = self.choose_date(message="Enter Habit Start Date (YYYY-MM-DD) or leave blank to start today: ")
        print("Great! Your habit starts on " + start.strftime('%Y-%m-%d') + "!")

        # periodicity and frequency
        periodicity = self.choose_periodicity()
        period = periodicity.rstrip('ly')
        if period == 'dai':
            period = 'day'
        try:
            frequency = int(input("Choose the frequency per " + period + ": "))
        except ValueError:
            print("Invalid input, only integer numbers are allowed here. Please try again.")
            # frequency = None
            frequency = int(input("Choose the frequency per " + period + ": "))

        # is_quantifiable, quantity and unit
        try:
            quant = questionary.confirm(message="Does your habit include achieving a given quantity "
                                                "(such as 8 glasses of water or running 2 km)?", default=False).ask()
            if quant:
                is_quantifiable = 1
            else:
                is_quantifiable = 0

        except NoConsoleScreenBufferError:
            print('Does your habit include achieving a given quantity (such as 8 glasses of water or running 2 km)?')
            quant = input('Please indicate Yes or No: ')
            quant = quant.upper()
            if quant == "YES" or quant == "Y":
                is_quantifiable = 1
            else:
                is_quantifiable = 0

        if is_quantifiable == 1:
            try:
                quantity = float(input("Please specify the quantity: "))
            except ValueError:
                print("Invalid input, only numbers and decimals are allowed here. Please try again.")
                quantity = None
                quantity = float(input("Please specify the quantity: "))
            unit = input("please specify the unit (optional): ")
        else:
            quantity = None
            unit = None

        row_count, return_hm = self.hm.create(habit_name, description, start, periodicity, frequency,
                                              is_quantifiable, quantity, unit)

        # fill habit overview text line as feedback for the user
        habit_fb = ("\n \n Habit '" + habit_name + "' - '" + description + "' starts on " + str(start) +
                    " and you plan to complete it " + periodicity + " with a frequency of " + str(frequency) + ". \n")
        if row_count == 2:  # records could be created -> return habit info
            if is_quantifiable != 1:
                return_message = habit_fb
            else:
                return_message = habit_fb + ("The quantifiable goal is " + str(quantity) + " " + unit + ". \n")
        else:  # no record created -> return return_message
            return_message = return_hm

        return return_message

    def reschedule_input(self):
        habit = self.choose_habit()
        habit_info = self.h.get_active_habit_info(habit=habit, info=True, streaks=False)
        edit_descr = input("Do you want to enter a new description of the habit " + habit + "? (y/n)").lower()
        try:
            if edit_descr == "y" or edit_descr == "n":
                pass
            else:
                raise ValueError("Invalid input: " + edit_descr + " Please try again!")
        except ValueError:
            print("Invalid input: " + edit_descr + " Please try again!")
            edit_descr = input("Do you want to enter a new description of the habit " + habit + "? (y/n)").lower()

        if edit_descr == "y":
            description = input("Please enter the new habit description: ")
        elif edit_descr == "n":
            description = habit_info[2]

        start = self.choose_date(message='Please choose the start date for the new periodicity or leave blank '
                                         'to start today: ')
        periodicity = self.choose_periodicity(message='Please choose the new periodicity: ')
        period = periodicity.rstrip('ly')
        if period == 'dai':
            period = 'day'
        try:
            frequency = int(input("Choose the new frequency per " + period + ": "))
        except ValueError:
            print("Invalid input, only integer numbers are allowed here. Please try again.")
            frequency = int(input("Choose the new frequency per " + period + ": "))

        # quantifiable?
        # is_quantifiable, quantity and unit
        try:
            change_quant = questionary.confirm(message="Do you want to change the quantity of your habit?",
                                               default=False).ask()

            if change_quant:
                quant = questionary.confirm(message="Does your habit include achieving a given quantity "
                                                    "(such as 8 glasses of water or running 2 km)?",
                                            default=False).ask()
                if quant:
                    is_quantifiable = 1
                else:
                    is_quantifiable = 0
            else:
                is_quantifiable = habit_info[3]
                no_change = True
        except NoConsoleScreenBufferError:
            change_quant = input('Do you want to change the quantity of your habit? y/n: ').lower()
            if change_quant == 'y':
                no_change = False
                print(
                    'Does your habit include achieving a given quantity (such as 8 glasses of water or running '
                    '2 km)?')
                quant = input('Please indicate Yes or No: ')
                quant = quant.upper()
                if quant == "YES" or quant == "Y":
                    is_quantifiable = 1
                else:
                    is_quantifiable = 0
            else:
                is_quantifiable = habit_info[3]
                no_change = True

        if not no_change and is_quantifiable == 1:
            try:
                quantity = float(input("Please specify the quantity: "))
            except ValueError:
                print("Invalid input, only numbers and decimals are allowed here. Please try again.")
                quantity = None
                quantity = float(input("Please specify the quantity: "))
            unit = input("please specify the unit (optional): ")
        elif not no_change and is_quantifiable == 0:
            quantity = None
            unit = None
        elif no_change and is_quantifiable == 1:
            quantity = habit_info[6]
            unit = habit_info[7]
        elif no_change and is_quantifiable == 0:
            quantity = None
            unit = None

        # call habit method to reschedule, transfer habit, date, periodicity, frequency, is_quan, quantity, unit
        ret = self.hm.reschedule(name=habit, description=description, periodicity=periodicity, start=start,
                                 frequency=frequency, is_quan=is_quantifiable, quantity=quantity, unit=unit)
        return ret

    def delete_input(self) -> str:
        """Collects user input for deletion functionality and calls method to delete habit
        It creates a return message with info about the number of deleted habits
        :return: string (will print as 3 lines)
        """
        # let user choose existing active habit
        habit = self.choose_habit(message='Please choose the habit you want to delete: ')

        # User confirmation
        print('Deleting habit ' + habit + ' will delete all master data, logged data and streaks.')
        print('You can also deactivate a habit to stop logging it but keep its data.')
        print('Are you sure you want to delete the habit ' + habit + '? ')
        confirmation = input('Please indicate Yes or No: ')
        if confirmation.upper() != 'YES' and confirmation.upper() != 'Y':
            return_message = (habit + ' was not deleted.')
            # TODO: possibly integrate option to jump to pause habit method?
        else:
            # call delete method
            output1, output2, output3 = self.hm.delete(habit)
            return_message = "\n" + output1 + "\n" + output2 + "\n" + output3
        return return_message

    def choose_habit(self, message: str = 'Please choose one of those habits: ') -> str:
        """produces a selection menu with active habits and returns user's selection
        :return: string containing name of an existing habit
        """
        # first import list of active habits
        habit_list = list(self.dba.get_active_habits_list())[0]
        try:
            habit_q = questionary.select(message=message, choices=habit_list)
            habit = habit_q.ask()
        except NoConsoleScreenBufferError:
            # create dict from habit list
            habit_dict = {}
            n = 1
            for habit in habit_list:
                habit_dict[n] = habit
                n += 1
            selection = self.show_menu_from_dict(options=habit_dict, subtitle=message)
            sel = int(selection)
            habit = habit_dict.get(sel)
        return habit

    def choose_periodicity(self, message: str = 'Choose a periodicity ') -> str:
        per_list, per_dict = self.h.get_periodicity_range
        try:
            periodicity_q = questionary.select(message=message, choices=per_list)
            periodicity = periodicity_q.ask()
        except NoConsoleScreenBufferError:
            selection = self.show_menu_from_dict(options=per_dict, subtitle=message + 'by entering its number: ')
            sel = int(selection)
            periodicity = per_dict.get(sel)
        return periodicity

    @staticmethod
    def choose_date(message: str = 'Please choose a date or leave blank to choose today: ') -> datetime.date:
        """asks the user to enter a date or leave blank to choose the current date
        :param message: the message to be displayed for the input
        :return: a date in datetime.date format """
        sel_date = input(message)
        if sel_date == '':
            sel_date = date.today()
        else:
            try:
                sel_date = date.fromisoformat(sel_date)
            except ValueError:
                print("Invalid date entry. Please enter you start in format YYYY-MM-DD!")
                sel_date = input(message)
                if sel_date == '':
                    sel_date = date.today()
                else:
                    sel_date = date.fromisoformat(sel_date)
        return sel_date

    def edit_input(self) -> str:
        """collects user input for editing the habit description
        :return: string containing information about successful change of DB records
        """

        # let user choose existing active habit
        habit = self.choose_habit(message='Please choose the habit you want to edit: ')

        new_descr = input("Enter new description for habit '" + habit + "': ")

        return_message = self.hm.edit(name=habit, descr=new_descr)

        return return_message

    def deactivate_input(self) -> str:
        """collects user information to deactivate an existing habit
        :return: string with information bout successful deactivation
        """
        # let user choose existing active habit
        habit = self.choose_habit(message='Please choose the habit you want to deactivate: ')

        # deactivation date
        end = self.choose_date(message="Please specify the date for deactivation in the format YYYY-MM-DD or leave "
                                       "blank to deactivate today: ")

        return_message = self.hm.deactivate(habit, str(end))
        return return_message

    def sub_analyze(self):
        """submenu with options for analyzing the user's habits"""
        # sub_man is a dictionary with the menu options for submenu of Manage Habits

        subtitle = "Analyze Habits"
        here = "Main Menu -> Analyze Habits"

        # print main menu to screen
        sub_selection, here = self.print_menu(options_dict=self.sub_ana_d, options_list=self.sub_ana_l,
                                              subtitle=subtitle, here=here)

        self.clear_screen()
        self.you_are_here(here=here)

        if sub_selection == 1 or sub_selection == "List all currently tracked habits":  # currently tracked habits
            Analyze.current_habits()
            input("\n Press enter to return to Analyze Habits submenu.")
            # call submenu again = return to submenu after finishing
            self.sub_analyze()

        elif sub_selection == 2 or sub_selection == "Habits by periodicity":  # Habits by periodicity
            # let user choose periodicity:
            periodicity = self.choose_periodicity()
            Analyze.habits_by_periodicity(periodicity)
            input("\n Press enter to return to Analyze Habits submenu.")
            # call submenu again = return to submenu after finishing
            self.sub_analyze()

        elif sub_selection == 3 or sub_selection == "Longest streak of all habits":  # longest streak of all
            Analyze.longest_streak()
            input("\n Press enter to return to Analyze Habits submenu.")
            # call submenu again = return to submenu after finishing
            self.sub_analyze()

        elif sub_selection == 4 or sub_selection == "Longest streak for a given habit":  # longest streak by habit
            habit = self.choose_habit()
            Analyze.longest_streak(habit)
            input("\n Press enter to return to Analyze Habits submenu.")
            # call submenu again = return to submenu after finishing
            self.sub_analyze()

        elif sub_selection == 5 or sub_selection == "Overview of a given habit":  # # TODO overview by habit
            pass

        elif sub_selection == 6 or sub_selection == "Overview by month":
            try:
                month = input("Please choose the month you want to analyze in format YYYY-MM: ")
                check = datetime.date.fromisoformat(str(month + '-01'))
            except ValueError:
                print("The input is not a valid month of format YYYY-MM. Please try again!")
                month = input("Please choose the month you want to analyze in format YYYY-MM: ")
                check = datetime.date.fromisoformat(str(month + '-01'))
            self.clear_screen()
            Analyze.overview_by_month(calmonth=month)
            input("\n Press enter to return to Analyze Habits submenu.")
            # call submenu again = return to submenu after finishing
            self.sub_analyze()

        elif sub_selection == 7 or sub_selection == "View logs by habit":  # logs overview
            # let user choose habit
            habit = self.choose_habit()
            try:
                limit = int(input("Specify how many logs you would like to see (optional): "))
            except ValueError:
                print("Invalid input.\n Please try again or leave blank to continue.")
                limit = int(input("Specify how many logs you would like to see (optional): "))
            if limit == '' or limit == 0:
                Analyze.logs_by_habit(habit)
            else:
                Analyze.logs_by_habit(habit=habit,limit=limit)

            input("\n Press enter to return to Analyze Habits submenu.")

            # call submenu again = return to submenu after finishing
            self.sub_analyze()

        elif sub_selection == 0 or sub_selection == "Return to Main Menu":  # back to main menu
            self.main_menu()

    def about_tht(self):
        """display information about the habit tracker and the logic it uses including tips for the user"""
        pass
