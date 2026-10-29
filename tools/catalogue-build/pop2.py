import pyarrow.parquet as pq, pyarrow as pa, rf, time, threading, os, io, requests
from concurrent.futures import ThreadPoolExecutor
COLS=["code","popularity_key","unique_scans_n","obsolete","no_nutrition_data"]
base=rf.RF(); md=pq.ParquetFile(base,buffer_size=0).metadata; N=md.num_row_groups
os.makedirs("part",exist_ok=True)
loc=threading.local()
def pf():
    if not hasattr(loc,"pf"):
        r=rf.RF.__new__(rf.RF); io.RawIOBase.__init__(r); r.s=requests.Session(); r.url=base.url; r.real=base.real; r.size=base.size; r.pos=0; r.n=0
        loc.pf=pq.ParquetFile(r,buffer_size=0,metadata=md)
    return loc.pf
def chunk(c):
    fn=f"part/{c:03d}.parquet"
    if os.path.exists(fn): return
    ts=[pf().read_row_group(i,columns=COLS) for i in range(c*100,min(N,(c+1)*100))]
    pq.write_table(pa.concat_tables(ts),fn); print("chunk",c,flush=True)
t=time.time()
with ThreadPoolExecutor(12) as ex: list(ex.map(chunk,range((N+99)//100)))
print("done",time.time()-t,flush=True)
