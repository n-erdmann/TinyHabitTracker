# Tiny Habit Tracker
Version: Alpha 1

## About
Tiny Habit Tracker is a lightweight app to help build strong good habits by keeping track of completing them.
It enables the creation of daily, weekly, monthly and yearly habits with a chosen frequency and optionally also a 
quantity and features a variety of analysis options including current and longest streaks of the user's habits. 

## Installation
Tiny Habit tracker works on Windows and Linux (possibly also macOS) on Python 3.9.

pip install -r requirements.txt


## Usage (Tips)
Using Tiny Habit Tracker is designed to be as intuitive as possible. 
First, the user chooses between different options in the main menu:

`Main Menu` \
`1  -  Log Habit`\
`2  -  Manage Habits`\
`3  -  Analyze Habits`\
`4  -  About Tiny Habit Tracker`\
`0  -  Exit`


**Logging Habit Completion**

In the Main Menu the first entry "Log Habit" needs to be selected. The user chooses which habit is to be logged and 
then can enter a date for the log. If the log is for the current day, nothing needs to be entered.
This makes logging habits easy and fast.

Note that a habit needs to be created before it can be logged.


**Submenu Manage Habits**\
This Submenu provides the following options:

`Manage Habits`\
`1  -  Create an new Habit`\
`2  -  Edit Habit Description`\
`3  -  Reschedule Habit`\
`4  -  Deactivate Habit`\
`5  -  Delete Habit`\
`0  -  Return to Main Menu`


_**Creating a new habit**_\
In the submenu "Manage Habits" the user needs to choose the first option "Create a new Habit"
Tiny Habit Tracker then offers prompts to guide the user through the necessary steps for creating a habit. 
The following information is needed:
* Habit name & description
* Start date (default is today)
* periodicity (daily, weekly, monthly, yearly)
* frequency
* whether it is quantifiable or not\
For quantifiable habits users are asked to specify a quantity for their habit, such as a distance they want to complete while 
running regularly. The unit for this distance can be chosen freely.
For quantifiable habits a relative completion rate is provided and even if they are not completed the relative performance can be analyzed.

**Tips for creating habits**\
Especially for daily habits it is worth considering whether a habit is to be created as to be completed several times 
per day or once per day with a certain frequency. 
The habit "drinking eight glasses of water a day" can be taken as an example.
* If it is created as daily habit with frequency of 8 this means that the user will have to log 8 times that they drank 
1 glass of water every day. 
* If it is created as a daily habit with frequency of 1 and quantity of 8 glasses the user will need to log completion 
only once a day and, since it is quantifiable, the user can log less than 8 glasses and analyse how for away from the 
target they were. 

Generally, it is recommended to create daily habits that occur more than once or twice as quantifiable habits. 


_**Deleting or deactivating a habit**_

Deleting a habit removes all data of the habit from the underlying database, including the habits logs and streaks. 
An alternative to deleting a habit is deactivating it. This means that new logs can no longer be created but the current 
data of the habit is preserved and can still be viewed. Streaks are conserved.
Both actions are accessed in the submenu "Manage Habits".

_**Changing a Habit**_

A habit's description can be edited, choosing the second option "Edit Habit Description" in the submenu "Manage Habits".

To change a habit's periodicity, choose "Reschedule Habit" in the same submenu instead. Rescheduling a habit will reset 
its streak to 0 since the base for streak calculation changes. (The last streak with the old periodicity will be kept 
on the database, but it won't "count" for the new periodicity.)

**Submenu Analyze Habits**

All options for analyzing a user's habits can be found in this menu.
This includes longest streaks, currently tracked habits, habits by periodicity, habit overview, overview by month and 
individual habit's logs.

## Testing Tiny Habit Tracker Functionality
The test suite FuncTest can be used to test functionality. 

It includes 
* the generation of the underlying database, 
* the logging of habits and 
* the calculation of streaks and streak dates. 

Furthermore, some analysis functions are tested 
as well. After all tests are completed, the testdata is automatically removed again.