import schedule
import time


def job_that_executes_once():
    # Do some work that only needs to happen once...
    print('ran')
    return schedule.CancelJob


schedule.every().day.at('14:41').do(job_that_executes_once)

while True:
    schedule.run_pending()
    time.sleep(1)
