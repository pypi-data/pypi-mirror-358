import time
from datetime import datetime
from typing import Callable, Union, List, Dict, Optional
import schedule

class ManagerScheduler:

    @staticmethod
    def parse_schedule_time(schedule_time):
        """
        Parse the schedule time.

        :param schedule_time: The schedule time

        test:
        parse_schedule_time(120)
        parse_schedule_time("08:00")
        parse_schedule_time(["08:00", "12:00", "16:00"])

        parse_schedule_time({1: "08:00", 2: ["08:00", "12:00", "16:00"], 3: 216000, "1": "08:00"})
        """
        if isinstance(schedule_time, int):
            # Handle the number of seconds interval
            print(f"Execute every {schedule_time} seconds")
        elif isinstance(schedule_time, str):
            # Handle the time point
            print(f"Execute every {schedule_time}")
        elif isinstance(schedule_time, list):
            # Handle multiple time points
            for time in schedule_time:
                print(f"Execute every {time} seconds")
        elif isinstance(schedule_time, dict):

            for key, value in schedule_time.items():
                if isinstance(key, int):
                    # Handle specific date
                    print(f"This month {key} day:")
                    ManagerScheduler.parse_schedule_time(value)
                elif isinstance(key, str):
                    # Handle weekday

                    print(f"The schedule for the week {key}:")
                    ManagerScheduler.parse_schedule_time(value)
        else:
            raise ValueError("Invalid schedule_time type.")

    @staticmethod
    def pocwatch(
        job: Callable,
        schedule_time: Union[int, float, str, List[str], Dict[Union[int, str], Union[int, float, str, List[str]]]],
        success_function: Callable,
        failure_function: Callable,
    ) -> None:
        def wrapper():
            try:
                job()
                success_function()
            except Exception as e:
                failure_function()
                raise e

        ManagerScheduler.setup_schedule(wrapper, schedule_time)

        while True:
            schedule.run_pending()
            time.sleep(1)


    @staticmethod
    def setup_schedule(job_wrapper, schedule_time):
        """
        Set up scheduling tasks.

        :param job_wrapper: The wrapped task function
        :param schedule_time: The schedule time
        """
        if isinstance(schedule_time, (int, float)):
            # Execute every specified number of seconds
            schedule.every(schedule_time).seconds.do(job_wrapper)
        elif isinstance(schedule_time, str):
            # Execute once at a specific time each day
            schedule.every().day.at(schedule_time).do(job_wrapper)
        elif isinstance(schedule_time, list):
            # Execute at multiple specific times each day
            for time_point in schedule_time:
                schedule.every().day.at(time_point).do(job_wrapper)
        elif isinstance(schedule_time, dict):
            # Perform complex scheduling based on dictionary key-value pairs
            for key, value in schedule_time.items():
                if isinstance(key, int):
                    # Schedule by date
                    ManagerScheduler.setup_date_schedule(job_wrapper, key, value)
                elif isinstance(key, str):
                    # Schedule by day of the week
                    ManagerScheduler.setup_week_schedule(job_wrapper, key, value)
                else:
                    raise ValueError(f"Invalid schedule key type: {type(key)}")
        else:
            raise ValueError("Invalid schedule_time type.")


    @staticmethod
    def setup_date_schedule(job_wrapper, day, value):
        """
        Schedule tasks by date.

        :param job_wrapper: The wrapped task function
        :param day: Date (1-31)
        :param value: Schedule time, can be a number (seconds), a string ("HH:MM"), a list, or other
        """
        if isinstance(value, (int, float)):
            # On the specified date, execute the task every certain seconds
            def date_wrapper():
                today = datetime.now().day
                if today == day:
                    try:
                        job_wrapper()
                    except Exception as e:
                        # Task failure handling is already in the main scheduler
                        pass

            schedule.every().day.at("00:00").do(date_wrapper).tag(str(day))
        elif isinstance(value, str):
            # Execute once at a specific time on the specified date
            def date_time_wrapper():
                today = datetime.now().day
                if today == day:
                    job_wrapper()

            schedule.every().day.at(value).do(date_time_wrapper).tag(str(day))
        elif isinstance(value, list):
            # Execute at multiple specific times on the specified date
            for time_point in value:

                def date_time_list_wrapper(tp=time_point):
                    today = datetime.now().day
                    if today == day:
                        job_wrapper()

                schedule.every().day.at(time_point).do(date_time_list_wrapper).tag(str(day))
        else:
            raise ValueError(f"Invalid schedule value type: {type(value)}")


    @staticmethod
    def setup_week_schedule(job_wrapper, day_str, value):
        """
        Schedule tasks by day of the week.

        :param job_wrapper: The wrapped task function
        :param day_str: Day of the week string (e.g., "mon", "Monday")
        :param value: Schedule time, can be a number (seconds), a string ("HH:MM"), a list, or other
        """
        day = ManagerScheduler.parse_weekday(day_str)
        if not day:
            raise ValueError(f"Invalid day of week: {day_str}")

        if isinstance(value, (int, float)):
            # Execute every specified number of seconds
            schedule.every().week.do(ManagerScheduler.run_weekly_job, job_wrapper, value).day_of_week = day
        elif isinstance(value, str):
            # Execute once at a specific time each week
            getattr(schedule.every(), day).at(value).do(job_wrapper)
        elif isinstance(value, list):
            # Execute at multiple specific times each week
            for time_point in value:
                getattr(schedule.every(), day).at(time_point).do(job_wrapper)
        else:
            raise ValueError(f"Invalid schedule value type: {type(value)}")


    @staticmethod
    def run_weekly_job(job_wrapper, interval_seconds):
        """
        Execute job_wrapper every interval_seconds during the week.

        :param job_wrapper: The wrapped task function
        :param interval_seconds: Execution interval in seconds
        """
        next_run = time.time()
        while True:
            current_time = time.time()
            if current_time >= next_run:
                try:
                    job_wrapper()
                except Exception as e:
                    pass  # Error handling is already in the main scheduler
                next_run = current_time + interval_seconds
            time.sleep(1)
            if datetime.now().weekday() != datetime.now().weekday():
                # Get the current weekday (0-6, 0 is Monday).
                break


    @staticmethod
    def parse_weekday(day_str):
        """
        Parse the day of week string.

        :param day_str: Day of week string
        :return: schedule library supported day of week method name (e.g., 'monday') or None
        """
        day_str = day_str.strip().lower()
        days = {
            "1": "monday",
            "mon": "monday",
            "monday": "monday",
            "星期一": "monday",
            "周一": "monday",
            "礼拜一": "monday",
            "2": "tuesday",
            "tue": "tuesday",
            "tuesday": "tuesday",
            "星期二": "tuesday",
            "周二": "tuesday",
            "礼拜二": "tuesday",
            "3": "wednesday",
            "wed": "wednesday",
            "wednesday": "wednesday",
            "星期三": "wednesday",
            "周三": "wednesday",
            "礼拜三": "wednesday",
            "4": "thursday",
            "thu": "thursday",
            "thursday": "thursday",
            "星期四": "thursday",
            "周四": "thursday",
            "礼拜四": "thursday",
            "5": "friday",
            "fri": "friday",
            "friday": "friday",
            "星期五": "friday",
            "周五": "friday",
            "礼拜五": "friday",
            "6": "saturday",
            "sat": "saturday",
            "saturday": "saturday",
            "星期六": "saturday",
            "周六": "saturday",
            "礼拜六": "saturday",
            "7": "sunday",
            "sun": "sunday",
            "sunday": "sunday",
            "星期日": "sunday",
            "星期天": "sunday",
            "周日": "sunday",
            "周天": "sunday",
            "礼拜日": "sunday",
            "礼拜天": "sunday",
        }
        return days.get(day_str[:3], None)