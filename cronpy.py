#!/usr/bin/env python

from collections import OrderedDict

from crontab import CronTab


class InvalidOptionError(Exception):
    """Raised when the user gives an invalid option"""


class CronJob:
    def __init__(self):
        """Initializes user and fetches cron data."""
        self.cron = CronTab(user=True)
        self.update_cron_data()

    def update_cron_data(self):
        """Update user instance with current cron data and resets schedule."""
        activeJobs = enumerate([job for job in self.cron if job.is_enabled()], 1) # Create list of jobs if enabled and number them
        self.activeJobs = dict(map(lambda (pos, job): (str(pos),job), activeJobs)) # Convert numbers to strings and converts list to dict

        inactiveJobs = enumerate([job for job in self.cron if not job.is_enabled()], 1)
        self.inactiveJobs = dict(map(lambda (pos, job): (str(pos),job), inactiveJobs))

        self.jobCount = len(self.activeJobs) + len(self.inactiveJobs)
        self.schedule = OrderedDict([('m', None), ('h', None), ('dom', None), ('mon', None), ('dow', None)])

    def list_jobs(self):
        """Display all active and inactive jobs in a list format."""
        print 'Active Jobs:'
        if self.activeJobs:
            for pos, job in sorted(self.activeJobs.items(), key=lambda (pos,job): int(pos)):
                print '{}. {}'.format(pos, job)
        else:
            print 'no active jobs'

        print '\nInactive Jobs:'
        if self.inactiveJobs:
            for pos, job in sorted(self.inactiveJobs.items(), key=lambda (pos,job): int(pos)):
                print '{}. {}'.format(pos, job)
        else:
            print 'no inactive jobs'

        print '{}{}{}'.format('\n', '-'*60, '\n')

    def write_changes_to_cron(self):
        """Writes all changes to the user's crontab file
        and then updates the user's cron data.
        """
        self.cron.write()
        self.update_cron_data()

    def select_job(self, jobNumber, jobState):
        """Returns a specific job object for executing an action on."""
        if jobState == '1':
            return self.activeJobs.get(jobNumber)
        else:
            return self.inactiveJobs.get(jobNumber)

    def search_job(self, searchTerm):
        """Returns a numbered list of jobs based on a search query.
        Will search by command and by comment and combine results
        into a single list.
        """
        foundJobs = (
            list(self.cron.find_command(searchTerm)) +
            list(self.cron.find_comment(searchTerm))
        )
        return dict([(str(pos),job) for pos, job in enumerate(foundJobs, 1)])

    def add_job(self, command, comment):
        """Adds a job to the user's crontab if the job is valid."""
        job = self.cron.new(command=command, comment=comment)
        if isinstance(self.schedule, str): # self.schedule is one of the special cases
            job.setall(self.schedule)
        else:
            job.setall(' '.join(self.schedule.values()))
        if job.is_valid():
            self.write_changes_to_cron()
        else:
            print 'Error: Failed to add job, invalid syntax\n'

    def delete_job(self, job):
        """Removes a single job from the user's crontab."""
        self.cron.remove(job)
        self.write_changes_to_cron()

    def modify_job(self, action, job):
        """Modifies a job in the users's crontab."""
        if action == '1':       # enable/disable
            if job.is_enabled():
                job.enable(False)
            else:
                job.enable()
        elif action == '2':     # edit command
            newCommand = raw_input('New command for job: ')
            job.set_command(newCommand)
        elif action == '3':     # edit schedule
            self.create_schedule()
            if isinstance(self.schedule, str): # self.schedule is one of the special cases
                job.setall(self.schedule)
            else:
                job.setall(' '.join(self.schedule.values()))
        elif action == '4':     # edit comment
            print 'Note: Type nothing to remove a comment'
            newComment = raw_input('New comment for job: ')
            job.set_comment(newComment)

    def confirm_action(self, action, job):
        """Forces user to confirm action before it's executed."""
        print 'Are you sure you want to {} the following job:\n({})'.format(action, job),
        while True:
            answer = raw_input('[y/n]: ')
            if answer.lower() in ('y', 'n'):
                break
            else:
                print 'You must answer y or n ',
        return True if answer.lower() == 'y' else False

    def create_schedule(self):
        """Creates a schedule to be used for the creation
        or modification of a job in the user's crontab.
        """
        scheduleType = raw_input('Options:\n1. Specific Date\n2. Recurring task\n> ')
        if scheduleType == '1':
            self.schedule['dow'] = '*'
            self.schedule['mon'] = raw_input('Month (1-12): ')
            self.schedule['dom'] = raw_input('Day of Month (1-31): ')
            time = raw_input('Time in 24hr format (HH:MM): ')
            hour, minute = time.split(':')
            self.schedule['h'] = hour
            self.schedule['m'] = minute

        elif scheduleType == '2':
            print 'Options:\n\
1. Run every boot\n\
2. Run hourly\n\
3. Run daily\n\
4. Run weekly\n\
5. Run monthly\n\
6. Run yearly\n\
7. Custom schedule\n'
            userOption = raw_input('> ')
            if userOption in map(str, range(1,7)): # options 1-6
                specialCases = {
                    '1': '@reboot',
                    '2': '@hourly',
                    '3': '@daily',
                    '4': '@weekly',
                    '5': '@monthly',
                    '6': '@yearly',
                }
                self.schedule = specialCases[userOption]
                return
            elif userOption == '7':
                pass
            else:
                raise InvalidOptionError

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
                    self.schedule['dow'] = raw_input('> ')
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
                    self.schedule['mon'] = raw_input('> ')
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
                    self.schedule['dom'] = raw_input('> ')
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
                    self.schedule['h'] = raw_input('> ')
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


def find_job_menu(user):
    """Provides user with menu tree to select
    job for executing an action on and then
    returns the job object.
    """
    userAction = raw_input('1. Select job\n2. Search for job\n> ')
    if userAction == '1':
        jobState = raw_input('Is the job (1) active or (0) inactive?\n> ')
        if jobState not in ('1', '0'):
            raise InvalidOptionError
        job = raw_input('Type the number corresponding with the job you want:\n> ')
        return user.select_job(job, jobState)
    elif userAction == '2':
        print 'Type the command or comment of the job'
        searchTerm = raw_input('Search: ')
        jobs = user.search_job(searchTerm)
        if jobs:
            print 'Search query found {} job(s):'.format(len(jobs))
            if len(jobs) > 1:
                for pos, job in sorted(jobs.items(), key=lambda (pos,job): int(pos)):
                    print '{}. {}'.format(pos, job)
                jobNumber = raw_input("Type the number corresponding with the job you want\n> ")
            else:
                print '1. {}'.format(jobs['1'])
                jobNumber = '1'

            if jobNumber in jobs.keys():
                return jobs[jobNumber]
            else:
                raise InvalidOptionError
        else:
            print 'No jobs found for query: "{}"'.format(searchTerm)
    else:
        raise InvalidOptionError

def get_user_action(menu):
    """Displays menu options and then takes
    input from the user to determine what
    action to execute.
    """
    if menu == 'main':
        print 'Menu:\n\
1. Add job\n\
2. Remove job\n\
3. Modify job\n\
\nType (q)uit to exit\n'
    elif menu == 'modify':
        print 'Options:\n\
1. Enable/Disable job\n\
2. Edit command for job\n\
3. Edit schedule for job\n\
4. Edit comment for job\n\
\nOtherwise type \'c\' to cancel'

    action = raw_input('> ')
    return action
    

user = CronJob()       # Open's the default users's crontab for modification
while True:
    # Display user's crontab data (current user, number of jobs, job list)
    print 'User: {}'.format(user.cron.user)
    print 'Job Count: {}'.format(user.jobCount)
    user.list_jobs()
    
    try:
        userAction = get_user_action('main')

        if userAction.lower() in ('q', 'quit', 'exit'):
            raise SystemExit

        elif userAction.lower() in ('1', 'add', 'a'):
            jobCommand = raw_input('Command for new job: ')
            user.create_schedule()
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

        elif userAction.lower() in ('2', 'remove', 'delete', 'del', 'r'):
            if user.jobCount == 0:
                print 'There are no jobs'
                raise InvalidOptionError

            job = find_job_menu(user)
            if user.confirm_action('delete', job):
                user.delete_job(job)

        elif userAction.lower() in ('3', 'modify', 'mod', 'm'):
            if user.jobCount == 0:
                print 'There are no jobs'
                raise InvalidOptionError
            userAction = get_user_action('modify')
            if userAction in ('1', '2', '3', '4'):
                job = find_job_menu(user)
                if job:
                    user.modify_job(userAction, job)
                    if userAction == '1' and job.is_enabled(): # job was just enabled but changes haven't been written to crontab yet
                        if user.confirm_action('enable', job):
                            user.write_changes_to_cron()
                    elif userAction == '1' and not job.is_enabled(): # job was just disabled but changes haven't been written to crontab yet
                        if user.confirm_action('disable', job):
                            user.write_changes_to_cron()
                    elif userAction == '2':
                        if user.confirm_action('save the command for', job):
                            user.write_changes_to_cron()
                    elif userAction == '3':
                        if user.confirm_action('save the schedule for', job):
                            user.write_changes_to_cron()
                    elif userAction == '4':
                        if job.comment:
                            if user.confirm_action('save the comment for', job):
                                user.write_changes_to_cron()
                        else:
                            if user.confirm_action('remove the comment for', job):
                                user.write_changes_to_cron()
                    user.__init__()

                else:
                    raise InvalidOptionError
            elif userAction in ('c', 'cancel'):
                pass
            else:
                raise InvalidOptionError

        else:
            raise InvalidOptionError
    except InvalidOptionError:
        print 'Invalid option\n'
        raw_input('Press [Enter] to continue')

    except KeyboardInterrupt:   # if user hits keyboard interrupt key, exit program gracefully
        print
        raise SystemExit
