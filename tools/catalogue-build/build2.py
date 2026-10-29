import pyarrow.parquet as pq, pyarrow as pa, re, unicodedata, json, collections, csv
tb=pq.read_table("top10k.parquet").to_pylist()+pq.read_table("top2.parquet").to_pylist()
seen=set(); T=[]
for r in tb:
    if r['code'] in seen: continue
    seen.add(r['code']); T.append(r)
def nut(r):
    return {n['name']:n['100g'] for n in (r['nutriments'] or []) if n['100g'] is not None}
def norm(s):
    s=unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
    s=re.sub(r'\b\d+([.,]\d+)?\s*(g|kg|ml|cl|l|oz|fl oz|pack|x)\b','',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
rows=[];drop=collections.Counter()
for r in T:
    n=nut(r); k,p,c,f=(n.get(x) for x in ('energy-kcal','proteins','carbohydrates','fat'))
    if None in (k,p,c,f): drop['valeurs incomplètes (kcal, prot., gluc. ou lip. absents)']+=1; continue
    names={x['lang']:x['text'].strip() for x in (r['product_name'] or []) if x['text'] and x['text'].strip()}
    main=names.pop('main',None) or next(iter(names.values()),None)
    if not main: drop['sans nom']+=1; continue
    est=4*p+4*c+9*f
    if k>950 or p+c+f>100.5 or min(k,p,c,f)<0 or abs(k-est)>max(40,0.3*est): drop['incohérent (kcal ≠ macros, ou >100 g/100 g)']+=1; continue
    ctry=[x.replace('en:','') for x in (r['countries_tags'] or []) if x!='en:world']
    rows.append(dict(code=r['code'],brand=(r['brands'] or '').split(',')[0].strip(),name=main,names=names,countries=ctry,
      cats=[x for x in (r['categories_tags'] or []) if x.startswith('en:')][-3:],pop=r['popularity_key'] or 0,
      kcal=round(k),p=round(p,1),c=round(c,1),f=round(f,1),
      sug=round(n['sugars'],1) if 'sugars' in n else '',sat=round(n['saturated-fat'],1) if 'saturated-fat' in n else '',
      fib=round(n['fiber'],1) if 'fiber' in n else '',salt=round(n['salt'],2) if 'salt' in n else '',
      per=r['nutrition_data_per'] or '',serv=r['serving_quantity'] or ''))
print("lus",len(T),"gardés",len(rows),dict(drop))
def toks(x): return set(norm(x['name']).split())|{t for v in x['names'].values() for t in norm(v).split()}
g={};byb=collections.defaultdict(list);merged=0
for x in sorted(rows,key=lambda x:-x['pop']):
    key=(norm(x['brand']),norm(x['name']))
    tgt=g.get(key)
    if tgt is None:
        mk=(norm(x['brand']),x['kcal'],x['p'],x['c'],x['f'])
        for y in byb[mk]:
            a,b=toks(x),toks(y)
            if a and b and len(a&b)/len(a|b)>=0.5: tgt=y;break
    if tgt is not None:
        merged+=1; tgt['codes'].append(x['code']); tgt['countries']=sorted(set(tgt['countries'])|set(x['countries']))
        for l,v in x['names'].items(): tgt['names'].setdefault(l,v)
        g.setdefault(key,tgt); continue
    x['codes']=[x['code']]; g[key]=x; byb[(norm(x['brand']),x['kcal'],x['p'],x['c'],x['f'])].append(x)
out={id(v):v for v in g.values()}.values(); out=sorted(out,key=lambda x:-x['pop']); print("doublons fusionnés",merged,"produits uniques",len(out))
cc=collections.Counter(c for x in out for c in x['countries']); print(cc.most_common(20))
json.dump(list(out),open("catalogue.json","w"),ensure_ascii=False)
with open("catalogue.csv","w",newline='',encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["code_barres","autres_codes","marque","nom","noms_par_langue_json","pays","categories_off","kcal_100g","proteines_100g","glucides_100g","sucres_100g","lipides_100g","satures_100g","fibres_100g","sel_100g","portion_g","source","licence"])
    for x in out:
        w.writerow([x['code'],";".join(x['codes'][1:]),x['brand'],x['name'],json.dumps(x['names'],ensure_ascii=False),";".join(x['countries']),";".join(x['cats']),x['kcal'],x['p'],x['c'],x['sug'],x['f'],x['sat'],x['fib'],x['salt'],x['serv'],"Open Food Facts","ODbL 1.0 (base) / DbCL 1.0 (contenus)"])
