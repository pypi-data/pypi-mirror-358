from datetime import date, datetime, timedelta as td
from dateutil.relativedelta import relativedelta

class DateUts():
    date = None
    str_format = 'sql'

    def __init__(self,date):
        self.date = date

    def is_weekend(self):
        return self.date.weekday() in [5, 6]
    
    def weekday(self):
        return self.date.weekday()

    def __repr__(self):
        return f"<DateUts {self.date.strftime('%Y-%m-%d %H:%M:%S')}>"

    def format(self,fmt):
        fmt= fmt if not fmt else getFmt(fmt)

        return DateUts(self.date.date) if not fmt else self.date.strftime(fmt) 

    def toSql(self):
        return self.fmt('sql')
    
    def add(self,qtd:int,unit:str="day",fmt=None):
        return dateAdd(self.date,qtd,unit,fmt)
    
    def __str__(self):
        return self.fmt(self.str_format) 


# output: True (2023-04-22 is a Saturday)


#========= USAGE ============
#Ex1:
# > sqlToDate('yyyy-MM-dd')
# > <datetime>

def sqlToDate(date_str:str):
    return DateUts(datetime.strptime(date_str,"%Y-%m-%d"))

#========= USAGE ============
#Ex1:
# > dateToSql(<datetime>)
# > 'yyyy-MM-dd'

def dateToSql(dt:date):
    return DateUts(dt.strftime(dt,"%Y-%m-%d"))

#========= USAGE ============
#Ex1:
# > now()  ,  now(fmt='%Y-%m-%d')   ,   now(fmt='sql')
# > <datetime>, 'yyyy-MM-dd',  'yyyy-MM-dd'

def now(fmt=None):
    v =  datetime.now()
    return fmtDate(v,fmt)

#========= USAGE ============
#Ex1:
# > today()  ,  today(fmt='%Y-%m-%d')   ,   today(fmt='sql')
# > <datetime>, 'yyyy-MM-dd',  'yyyy-MM-dd'

def today(fmt=None,addDays=0):
    v =  datetime.now().date()
    v =  v if not addDays else dateAdd(today(),addDays,'day')
    return fmtDate(v,fmt)

#========= USAGE ============
#Ex1:
# > yesterday()  ,  yesterday(fmt='%Y-%m-%d')   ,   yesterday(fmt='sql')
# > <datetime>, 'yyyy-MM-dd',  'yyyy-MM-dd'

def yesterday(fmt=None):
    v = today().date - td(1)
    return fmtDate(v,fmt)

def tomorrow(fmt=None):
    v = today().date + td(1)
    return fmtDate(v,fmt)

#========= USAGE ============
#Ex1:
# > start,end = <date:2022-05-23>,<date:2022-05-24>
# > dateRange(start,end) ,  dateRange('2022-05-23',1,'day',fmt='%Y-%m-%d')   ,   dateRange('2022-05-23',1,'day',fmt='sql')
# > [<datetime>,<datetime>], ['2022-05-23','2022-05-24'],  ['2022-05-23','2022-05-24']

def dateRange(start:date,end:date,fmt=None,filter_lbd:callable=None):
    start = start.date if isinstance(start,DateUts) else start
    end   = end.date if isinstance(end,DateUts) else end

    if start > end:
        dates = [dateAdd(start,x*-1) for x in range(0, (start-end).days + 1)]
    else:
        dates = [dateAdd(start,x) for x in range(0, (end-start).days + 1)]
    
    if filter_lbd:
        dates = list(filter(filter_lbd,dates))
    if fmt:
        dates = [fmtDate(x,fmt) for x in dates]
    
    return dates

#========= USAGE ============
#Ex1:
# > dateAdd('2022-05-23',1,'day') ,  dateAdd('2022-05-23',1,'day',fmt='%Y-%m-%d')   ,   dateAdd('2022-05-23',1,'day',fmt='sql')
# > <datetime>, '2022-05-24',  '2022-05-24'
#Ex2:
# > dateAdd('2022-05-23',-1,'day') ,  dateAdd('2022-05-23',-1,'day',fmt='%Y-%m-%d')   ,   dateAdd('2022-05-23',-1,'day',fmt='sql')
# > <datetime>, '2022-05-22',  '2022-05-22'

def dateAdd(date:date,qtd:int,unit:str="day",fmt=None):
    date = date.date if isinstance(date,DateUts) else date
    if unit == 'day':
        v = date + td(qtd) if qtd > 0 else date - td(abs(qtd))
    elif unit == 'year':
        v = date.replace(year = date.year + qtd)
    elif unit == 'hour':
        v = date + td(hours=qtd)
    elif unit == 'minute':
        v = date + td(minutes=qtd)
    elif unit == 'second':
        v = date + td(seconds=qtd)
    elif unit == 'month':
        v = date + relativedelta(months=qtd)



    return fmtDate(v,fmt)

#========= USAGE ============ 
#Obs: Today is "2022-05-23"
#Ex1:
# > lastWorkingDate()  ,  lastWorkingDate(fmt='%Y-%m-%d')   ,   lastWorkingDate(fmt='sql')
# > <datetime>, '2022-05-20',  '2022-05-20'
#Ex2:
# > lastWorkingDate(ref=<date:'2022-03-24'>)  ,  lastWorkingDate(ref=<date:'2022-03-24'>,fmt='%Y-%m-%d')   ,   lastWorkingDate(ref=<date:'2022-03-24'>,fmt='sql')
# > <datetime>, '2022-05-23',  '2022-05-23'

def lastWorkingDate(ref:date=None,fmt=None,allow_saturday=False,allow_sunday=False,num_days=1,holidays=[]): #IGNORE SATURDAY AND SUNDAY
    num_days     = abs(num_days)
    current_date = today() if not ref else ref
    to_ignore    = [y for x,y in zip([allow_saturday,allow_sunday],[5,6]) if not x]
    
    while num_days:
        current_date = dateAdd(current_date,-1,'day')

        if current_date.weekday() in to_ignore: continue
        if current_date.format('sql') in holidays: continue

        num_days -= 1

    return fmtDate(current_date,fmt)


#holidays ['yyyy-mm-dd']
def nextWorkingDate(ref:date=None,fmt=None,allow_saturday=False,allow_sunday=False,num_days=1,holidays=[]): #IGNORE SATURDAY AND SUNDAY
    num_days     = abs(num_days)
    current_date = today() if not ref else ref
    to_ignore    = [y for x,y in zip([allow_saturday,allow_sunday],[5,6]) if not x]
    
    while num_days:
        current_date = dateAdd(current_date,1,'day')

        if current_date.weekday() in to_ignore: continue
        if current_date.format('sql') in holidays: continue

        num_days -= 1

    return fmtDate(current_date,fmt)


#========= USAGE ============
#Ex1:
# > today()  ,  today(fmt='%Y-%m-%d')   ,   today(fmt='sql')
# > <datetime>, 'yyyy-MM-dd',  'yyyy-MM-dd'

def fmtDate(dt:date,fmt:str):
    # fmt= fmt if not fmt else ("%Y-%m-%d" if fmt == "sql" else fmt)
    fmt= fmt if not fmt else getFmt(fmt)
    dt = dt.date if isinstance(dt,DateUts) else dt

    return DateUts(dt) if not fmt else dt.strftime(fmt)

def getFmt(fmt:str):
    fmts = {
        "sql":"%Y-%m-%d",
        "sql+hr":"%Y-%m-%d %H:%M:%S",
        "sql+Thr":"%Y-%m-%dT%H:%M:%S",
        "brz":"%d/%m/%Y",
        "brz+hr":"%d/%m/%Y %H:%M:%S",
        "brz+Thr":"%d/%m/%YT%H:%M:%S",
        "usa":"%m/%d/%Y",
        "usa+hr":"%m/%d/%Y %H:%M:%S",
        "usa+Thr":"%m/%d/%YT%H:%M:%S"
    }
    return fmts[fmt] if fmt in fmts else fmt

def dateMatch(dt:str,fmt:str):
    # fmt = "%Y-%m-%d" if fmt == "sql" else fmt
    fmt = getFmt(fmt)

    try:
        datetime.strptime(dt,fmt)
    except ValueError:
        return False

    return True 

def firstDay(sql_dte:date,fmt:str=None):
    dte = sql_dte if isinstance(sql_dte,date) or isinstance(sql_dte,DateUts) else sqlToDate(sql_dte)
    dte = fmtDate(dte,"%Y-%m-01")
    firstDay = sqlToDate(dte)
    return fmtDate(firstDay,fmt)

def lastDay(sql_dte:date,fmt:str=None):
    dte = sql_dte if isinstance(sql_dte,date) or isinstance(sql_dte,DateUts) else sqlToDate(sql_dte)
    dte = sqlToDate(dateAdd(dte,1,"month",fmt="%Y-%m-01"))
    dte = dateAdd(dte,-1,"day")
    return fmtDate(dte,fmt)

def interval(dte_start:date,dte_end:date,in_years=False,in_days=False,in_hours=False,in_minutes=False,in_seconds=False,in_microseconds=False):
    date_s = dte_start.date if isinstance(dte_start,DateUts) else dte_start
    date_e = dte_end.date if isinstance(dte_end,DateUts) else dte_end
    duration = date_e - date_s
    duration_in_s = duration.total_seconds()

    if in_years: return divmod(duration_in_s, 31536000)[0]
    if in_days: return divmod(duration_in_s, 86400)[0]
    if in_hours: return divmod(duration_in_s, 3600)[0]
    if in_minutes: return divmod(duration_in_s, 60)[0]
    if in_seconds: return duration_in_s
    if in_microseconds: return duration.microseconds

    return divmod(duration_in_s, 86400)[0]
    

    

Fnc_noWeekends = lambda dt:dt.weekday() not in [5,6]


