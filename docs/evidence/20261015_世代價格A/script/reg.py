import numpy as np, datetime as dt
def yr(d): 
    y,m,dd=map(int,d.split('-')); return dt.date(y,m,dd).toordinal()/365.25
def fit(pts,w,start=None,end=None):
    X=[];Y=[]
    for d,i,o in pts:
        if start and d<start: continue
        if end and d>end: continue
        X.append(yr(d)); Y.append(np.log((w*i+(1-w)*o)))
    b=np.polyfit(X,Y,1)[0]; return np.exp(b)-1,len(X)
E_stated=[('2023-03-14',30,60),('2023-11-06',10,30),('2024-05-13',5,15),('2024-08-06',2.5,10),('2025-04-14',2,8),('2025-08-07',1.25,10),('2025-12-11',1.75,14),('2026-03-05',2.5,15),('2026-07-09',2,12),('2026-09-22',2,10),('2026-09-29',2,10)]
if __name__=='__main__':
  for name,w in [('8:1 (ref req ISL16384/OSL2048)',8/9),('3:1',0.75)]:
    print(name)
    for lab,s,e in [('2023-2026.8',None,'2026-08-31'),('2024.3-2026.8','2024-03-01','2026-08-31'),('2025-2026.8','2025-01-01','2026-08-31'),('all',None,None)]:
        print(' ',lab,fit(E_stated,w,s,e))
