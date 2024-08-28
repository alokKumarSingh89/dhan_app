import pandas as pd
import time
from jobs.fyers_option_chain import pull_option_chain
def getTimeSeries(min):
    current_date = pd.Timestamp.now()
    startTime = pd.Timestamp(hour=9,minute=15,second=0,year=current_date.year, month=current_date.month, day=current_date.day)
    endTime = pd.Timestamp(hour=15,minute=30,second=0,year=current_date.year, month=current_date.month, day=current_date.day)
    total_min_count = int((endTime-startTime).seconds/(60*min))+1
    range = pd.date_range("9:15", periods=total_min_count, freq=f'{min} min')
    return [f'{item.hour}:{item.minute}' for item in range]

def startOptionJob():
    times = getTimeSeries(5)
    current_date = pd.Timestamp.now()
    c_time = f'{current_date.hour}:{current_date.minute}'
    if c_time not in times:
        if current_date.hour > 15:
            print("Can't Process, Time up")
        else:
            print("sleep for time")
            time.sleep(60);
            startOptionJob()
    else:
        if current_date.hour == 15 and current_date.minute == 30:
            print('Done for date');
        else:
            pull_option_chain(c_time)
            time.sleep(60);
            startOptionJob()