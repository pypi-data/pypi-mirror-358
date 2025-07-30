from cashare.common.dname import url1
import pandas as pd
from cashare.common.get_data import _retry_get
from cashare.common.var_token import get_token
def income_data(ca_code,period='annual'):
    li = handle_url(ca_code=ca_code,period=period,token=get_token())
    r =_retry_get(li,timeout=100)
    if type(r) == str:
        return r
    else:
        if r.empty:
            return r
        else:
            r["date"] = pd.to_datetime(r["date"], unit='ms')
            return r

def handle_url(ca_code,period,token):

    if period == 'annual':
        return url1 + '/income/' + ca_code + '/' + 'FY' + '/' + token
    else:
        return url1 + '/income/' + ca_code + '/' + 'Q' + '/' + token
if __name__ == '__main__':
    import cashare as ca
    ca.set_token('')
    df = ca.income_data(ca_code='Aapl',period='quarter',)
    print(df)

    pass




