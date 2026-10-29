import pyarrow.parquet as pq, pyarrow as pa, rf, time, threading, os, io, requests, numpy as np
from concurrent.futures import ThreadPoolExecutor
COLS=["code","product_name","brands","categories_tags","countries_tags","nutriments","serving_quantity","serving_size","nutrition_data_per","lang","quantity","completeness","popularity_key","unique_scans_n","food_groups_tags","obsolete"]
base=rf.RF(); md=pq.ParquetFile(base,buffer_size=0).metadata; N=md.num_row_groups
sizes=[md.row_group(i).num_rows for i in range(N)]; starts=np.concatenate([[0],np.cumsum(sizes)])
df=pq.read_table("pop2.parquet",columns=["code"]).to_pandas()
need=set(open("need_codes.txt").read().split())
idx=np.sort(df.index[df.code.isin(need)].values); print(len(idx),flush=True)
assert md.num_rows==len(df), (md.num_rows,len(df))
groups={}
for g in idx:
    i=int(np.searchsorted(starts,g,side='right')-1); groups.setdefault(i,[]).append(g-starts[i])
os.makedirs("det2",exist_ok=True)
loc=threading.local()
def pf():
    if not hasattr(loc,"pf"):
        r=rf.RF.__new__(rf.RF); io.RawIOBase.__init__(r); r.s=requests.Session(); r.url=base.url; r.real=base.real; r.size=base.size; r.pos=0; r.n=0
        loc.pf=pq.ParquetFile(r,buffer_size=0,metadata=md)
    return loc.pf
keys=sorted(groups)
def one(i):
    fn=f"det2/{i:04d}.parquet"
    if os.path.exists(fn): return
    t=pf().read_row_group(i,columns=COLS).take(pa.array(groups[i]))
    pq.write_table(t,fn)
t=time.time(); done=0
with ThreadPoolExecutor(12) as ex:
    for k,_ in enumerate(ex.map(one,keys)):
        if k%200==0: print("g",k,len(keys),int(time.time()-t),flush=True)
print("done",flush=True)
