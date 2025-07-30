#TEST FILE
from datetime import datetime as dt
from dotenv import load_dotenv
import sys
import os
sys.path.append("./dateUts")
from dateUts import *
load_dotenv()



print(interval(today(),tomorrow().date,in_seconds=True))
a = nextWorkingDate()
a = fmtDate("202306","%Y%m")
a = dateRange(firstDay(today()).date,lastDay(today()).date,filter_lbd = Fnc_noWeekends)
a[0].weekday()
a = DateUts(dt.now())
print(a)
a = lastWorkingDate(fmt="%Y-%m-%d")
rng = dateRange(sqlToDate("2022-05-01"),sqlToDate("2022-05-10"))
rng = dateRange(sqlToDate("2022-05-10"),sqlToDate("2022-05-01"))
a=1


pass


