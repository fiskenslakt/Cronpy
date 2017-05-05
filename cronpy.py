#!/usr/bin/env python

import sys

from collections import OrderedDict

from crontab import CronTab


class InvalidOptionError(Exception):
    """Raised when the user gives an invalid option"""


class CronJob:
    def __init__(self, user=None):
        self.user = user
        if self.user:
            self.cron = CronTab(user=self.user)
        else:
            self.cron = CronTab(user=True)

        self.activeJobs = dict(enumerate([job for job in self.cron if job.is_enabled()], 1))
        self.inactiveJobs = dict(enumerate([job for job in self.cron if not job.is_enabled()], 1))

        self.schedule = OrderedDict([('m','*'),('h','*'),('dom','*'),('mon','*'),('dow','*')])

    def list_jobs(self):
        """Display all active and inactive jobs in a list format."""
        print 'Active Jobs:'
        for pos, job in sorted(self.activeJobs.items()):
            print '{}. {}'.format(pos, job)

        print '\nInactive Jobs:'
        for pos, job in sorted(self.inactiveJobs.items()):
            print '{}. {}'.format(pos, job)

        print '{}{}{}'.format('\n', '*'*60, '\n')

    def write_changes_to_cron(self):
        """Writes all changes to the user's crontab file"""
        self.cron.write()

    def add_job(self, command, comment):
        """Adds a job to the user's crontab if the job is valid"""
        job = self.cron.new(command=command, comment=comment)
        job.setall(' '.join(self.schedule.values()))
        if job.is_valid():
            self.write_changes_to_cron()
        else:
            print 'Error: Failed to add job, invalid syntax\n'

    def create_schedule(self):
        scheduleType = raw_input('Specify time restriction:\n1. Specific Date\n2. Recurring task\n>')
        if scheduleType == '1':
            self.schedule['mon'] = raw_input('Month (1-12): ')
            self.schedule['dom'] = raw_input('Day of Month (1-31): ')
            time = raw_input('Time in 24hr format (HH:MM): ')
            hour, minute = time.split(':')
            self.schedule['h'] = hour
            self.schedule['m'] = minute

        elif scheduleType == '2':
            print 'Do you want this cronjob to run:'

            while True:
                dow = raw_input('Every day of the week? [Y/n]: ')
                if dow.lower() in ('y', ''):
                    self.schedule['dow'] = '*'
                    break
                elif dow.lower() == 'n':
                    print "Days of the week: (0) Sunday (1) Monday (2) Tuesday (3) Wednesday (4) Thursday (5) Friday (6) Saturday\n\
You can specify which days of the week in the following ways:\n\
 - A range of days (eg. 1-5 runs mon-fri)\n\
 - A list of days (eg. 1,3,5 runs on mon,wed,fri)\n\
 - A range with a specified interval (eg. 0-6/2 is every 2 days, 0-4/2 is every 2 days from sun-thursday)\n\
 - Lastly if it's only one day of the week, just enter the number corresponding with that day"
                    self.schedule["dow"] = raw_input(">")
                    break
                else:
                    'Please answer y or n'

            while True:
                mon = raw_input('Every month? [Y/n]: ')
                if mon.lower() in ('y', ''):
                    self.schedule['mon'] = '*'
                    break
                elif mon.lower() == 'n':
                    print "Months: (1) January (2) February (3) March (4) April (5) May (6) June\n\
        (7) July (8) August (9) September (10) October (11) November (12) December\n\
You can specify which months in the following ways:\n\
 - A range of months (eg. 2-5)\n\
 - A list of months (eg. 1,3,5,8,11)\n\
 - A range with a specified interval (eg. 1-12/2 is every 2 months, 1-6/2 is every 2 months for the first 6 months)\n\
 - Lastly if it's only one month, just enter the number corresponding with that month"
                    self.schedule['mon'] = raw_input('>')
                    break
                else:
                    print 'Please answer y or n\n'

            while True:
                dom = raw_input('Every day of the month? [Y/n]: ')
                if dom.lower() in ('y', ''):
                    self.schedule['dom'] = '*'
                    break
                elif dom.lower() == 'n':
                    print "Valid days are 1-31\n\
You can specify which days in the following ways:\n\
 - A range of days (eg. 2-5)\n\
 - A list of days (eg. 1,3,5,8,13,21)\n\
 - A range with a specified interval (eg. 1-31/2 is every 2 days, 1-10/2 is every 2 days for the first 10 days)\n\
 - Lastly if it's only one day, just enter the number corresponding with that day"
                    self.schedule['dom'] = raw_input('>')
                    break
                else:
                    'Please answer y or n\n'

            while True:
                hour = raw_input('Every hour? [Y/n]: ')
                if hour.lower() in ('y', ''):
                    self.schedule['h'] = '*'
                    break
                elif hour.lower() == 'n':
                    print "Valid hours are 0-23 (24hr time)\n\
You can specify which hours in the following ways:\n\
 - A range of hours (eg. 2-5)\n\
 - A list of hours (eg. 1,3,5,8,13,21)\n\
 - A range with a specified interval (eg. 0-23/2 is every 2 hours, 0-10/2 is every 2 hours for the first 10 hours)\n\
 - Lastly if it's a specific hour of the day, just enter the number corresponding with that hour"
                    self.schedule['h'] = raw_input('>')
                    break
                else:
                    'Please answer y or n'

            while True:
                minute = raw_input('Every minute? [Y/n]: ')
                if minute.lower() in ('y', ''):
                    self.schedule['m'] = '*'
                    break
                elif minute.lower() == 'n':
                    print "Valid minutes are 0-59\n\
You can specify which minutes in the following ways:\n\
 - A range of minutes (eg. 0-5 runs each min for the first five minutes of the hour)\n\
 - A list of minutes (eg. 1,3,5,8,13,21)\n\
 - A range with a specified interval (eg. 0-59/2 is every 2 minutes, 0-10/2 is every 2 minutes for the first 10 minutes of the hour)\n\
 - Lastly if it's a specific minute of the day, just enter the number corresponding with that minute"
                    self.schedule["m"] = raw_input(">")
                    break
                else:
                    'Please answer y or n\n'


def get_user_action():
    """Displays menu options and then takes
    input from the user to determine what
    action to execute.
    """
    print '1. Add job\n\
2. Remove job\n\
3. Modify job\n\
\nType (q)uit to exit\n'
    action = raw_input('> ')
    return action
    

user = CronJob()
while True:
    user.list_jobs()
    userAction = get_user_action()

    try:
        if userAction.lower() in ('q', 'quit', 'exit'):
            raise SystemExit
        elif userAction.lower() in ('1', 'add'):
            jobCommand = raw_input('Command for new job: ')
            jobHasComment = raw_input('\nDo you want to add a comment to the cronjob? [y/N]: ')
            while True:
                if jobHasComment.lower() == 'y':
                    jobComment = raw_input('\nType the comment you want for the cronjob\n>')
                    break
                elif jobHasComment.lower() in ('n', ''):
                    jobComment = None
                    break
                else:
                    print 'Please type y or n\n'
            user.add_job(jobCommand, jobComment)

        elif userAction.lower() in ('2', 'remove', 'delete', 'del'):
            pass

        elif userAction.lower() in ('3', 'modify', 'mod'):
            pass

        else:
            raise InvalidOptionError
    except InvalidOptionError:
        print 'Invalid option\n'
        raw_input('Press [Enter] to continue')
