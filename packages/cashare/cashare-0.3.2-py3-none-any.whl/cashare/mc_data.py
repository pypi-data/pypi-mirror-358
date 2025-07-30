
from cashare.common.dname import url1
import pandas as pd
import datetime

from cashare.common.var_token import get_token
from cashare.common.get_data import _retry_get
#获取单个股票市值
def mark_c_data(ca_code,start_date,end_date=str(datetime.date.today().strftime('%Y-%m-%d'))):
    if start_date > (datetime.date.today().strftime('%Y-%m-%d')):
        return "start_date大于现在时间"
    elif start_date > end_date:
        return "start_date大于end_date"
    elif end_date > (datetime.date.today().strftime('%Y-%m-%d')):
        end_date = datetime.date.today().strftime('%Y-%m-%d')
    else:
        pass

    li = hg(ca_code=ca_code, start_date=start_date, end_date=end_date, token=get_token(),)
    r = _retry_get(li, timeout=100)
    if type(r) == str:
        return r
    else:
        # print(r)
        if r.empty:
            return r
        else:
            r["date"] = pd.to_datetime(r["date"], unit='ms')
            return r


def hg(ca_code,start_date,end_date,token):


    g_url = url1 + '/mc/' + ca_code + '/' + start_date + '/' + end_date + '/' + token

    return g_url


if __name__ == '__main__':
    import cashare as ca
    ca.set_token('you_token')
    df=ca.mark_c_data(ca_code='A',start_date='1990-09-05',end_date='2025-09-09')
    print(df)
    # # pass



