import requests, io, time
U="https://huggingface.co/datasets/openfoodfacts/product-database/resolve/main/food.parquet"
class RF(io.RawIOBase):
    def __init__(s,url=U):
        s.s=requests.Session(); s.url=url; s.pos=0; s.n=0
        s.resolve()
    def resolve(s):
        for a in range(15):
            try:
                r=s.s.get(s.url,headers={"Range":"bytes=0-0"},stream=True,allow_redirects=True,timeout=60)
                s.real=r.url; s.size=int(r.headers["Content-Range"].split("/")[1]); r.close(); return
            except Exception as e:
                time.sleep(1)
        raise RuntimeError("resolve failed")
    def readable(s): return True
    def seekable(s): return True
    def tell(s): return s.pos
    def seek(s,o,w=0):
        s.pos = o if w==0 else (s.pos+o if w==1 else s.size+o); return s.pos
    def read(s,n=-1):
        if n<0 or s.pos+n>s.size: n=s.size-s.pos
        if n<=0: return b""
        for a in range(8):
            try:
                r=s.s.get(s.real,headers={"Range":f"bytes={s.pos}-{s.pos+n-1}"},timeout=120); r.raise_for_status(); break
            except Exception as e:
                if a==7: raise
                time.sleep(1); s.resolve()
        s.pos+=len(r.content); s.n+=len(r.content); return r.content
    def readinto(s,b):
        d=s.read(len(b)); b[:len(d)]=d; return len(d)
