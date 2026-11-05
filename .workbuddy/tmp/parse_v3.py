# -*- coding: utf-8 -*-
"""OCR 文本 → 三项参数（同前逻辑，输出到 spec_params_v3.json）"""
import json, re
ROOT="/Users/zhanghao/WorkBuddy/新大地五金网站-v2"
mapping=json.load(open('/tmp/ocr3_map.json'))
raw=open('/tmp/ocr3.txt').read()

parts=re.split(r'#{5,}\s*/tmp/ocr3/(\d+)\.png\s*#{5,}', raw)
it=iter(parts[1:]); blocks={int(i):b for i,b in zip(it,it)}

LBL_SIZE=r'(总\s*的\s*来\s*说|总\s*的|Overall|OVERALL|产品\s*尺寸|外形尺寸|Size|尺寸)'
LBL_PACK=r'(套\s*餐|餐\s*[:：]|Package|PACKAGE|包装\s*尺寸|包装|Packing)'
LBL_QTY =r'(数\s*量|Qty|QTY|装\s*箱\s*量|集装箱的数量|装柜数\s*量|装柜数量)'
NUM=r'(\d{1,5}(?:[.,]\d+)?)'
UNIT=r'(mm|MM|毫米|inch|INCH|Inch|in|IN|英寸)'
NUM3=r'(\d{1,5}(?:[.,]\d+)?(?:~\d{1,5}(?:[.,]\d+)?)?)'
TRIPLE=re.compile(NUM+r'\s*[WDHLwdh"”]?\s*[x×*X]\s*'+NUM+r'\s*[WDHLwdh]?\s*[x×*X]\s*'+NUM3+r'\s*[WDHLwdh]?\s*'+UNIT)
TRIPLE_IN=re.compile(NUM+r'\s*["”]\s*[WDHLwdh]?\s*[x×*X]\s*'+NUM+r'\s*["”]\s*[WDHLwdh]?\s*[x×*X]\s*'+NUM+r'\s*["”]\s*[WDHLwdh]?')
TRIPLE_BARE=re.compile(NUM+r'\s*[x×*X]\s*'+NUM+r'\s*[x×*X]\s*'+NUM+r'(?![\d"”])')
QTY=re.compile(r'(\d{1,5})\s*(?:件|[Pp][Cc][Ss])?\s*[/|l1]\s*40\s*H\s*Q', re.I)

def norm(t):
    t=t.replace('，',',').replace('：',':').replace('（','(').replace('）',')')
    t=t.replace('毫米','mm').replace('英寸','inch')
    return re.sub(r'\s+',' ',t)

def fmt(nums,unit):
    a,b,c=[n.replace(',','.').rstrip('.') for n in nums]
    u='mm' if unit.lower() in ('mm','毫米') else 'in'
    return f"{a} × {b} × {c} {u}", u

def nums_of(s): return [float(x) for x in re.findall(r'\d+(?:\.\d+)?', s)[:3]]
def consistent(mm_s,in_s):
    a,b=nums_of(mm_s),nums_of(in_s)
    if len(a)<3 or len(b)<3: return False
    return all(abs(x/25.4-y)<=max(1.2,x/25.4*0.04) for x,y in zip(a,b))

out={}
for m in mapping:
    t=norm(blocks.get(m['idx'],''))
    trip=[]
    for mt in TRIPLE.finditer(t):
        nums=(mt.group(1),mt.group(2),mt.group(3))
        try: vals=[float(n.replace(',','.')) for n in nums]
        except ValueError: continue
        if not all(4<=v<=6000 for v in vals): continue
        s,u=fmt(nums,mt.group(4)); trip.append((mt.start(),s,u))
    for mt in TRIPLE_IN.finditer(t):
        nums=(mt.group(1),mt.group(2),mt.group(3))
        try: vals=[float(n.replace(',','.')) for n in nums]
        except ValueError: continue
        if not all(4<=v<=240 for v in vals): continue
        trip.append((mt.start(), f"{nums[0]} × {nums[1]} × {nums[2]} in", 'in'))
    z={}
    for name,pat in (('size',LBL_SIZE),('pack',LBL_PACK),('qty',LBL_QTY)):
        mt=re.search(pat,t,re.I); z[name]=mt.start() if mt else None
    if not trip and z['size'] is not None:
        for mt in TRIPLE_BARE.finditer(t):
            trip.append((mt.start(), f"{mt.group(1)} × {mt.group(2)} × {mt.group(3)} mm", 'mm'))

    def pick(lo,hi,unit):
        r=[(pos,s) for pos,s,u in trip if u==unit and (lo is None or pos>=lo) and (hi is None or pos<=hi)]
        r.sort(); return [s for _,s in r]

    hi = z['pack'] if (z['size'] is not None and z['pack'] is not None and z['pack']>z['size']) else None
    size_mm=pick(z['size'],hi,'mm'); size_in=pick(z['size'],hi,'in')
    pack_mm=pick(z['pack'],None,'mm') if z['pack'] is not None else []
    pack_in=pick(z['pack'],None,'in') if z['pack'] is not None else []
    if not size_mm and not size_in:
        allmm=[s for _,s,u in trip if u=='mm']; allin=[s for _,s,u in trip if u=='in']
        size_mm=allmm[:1]; size_in=allin[:1]
        pack_mm=pack_mm or allmm[1:2]; pack_in=pack_in or allin[1:2]
    if not pack_mm and z['pack'] is not None:
        before=[(p,s) for p,s,u in trip if u=='mm' and p<z['pack'] and s!=(size_mm[0] if size_mm else None)]
        if before: pack_mm=[before[-1][1]]
    if not pack_in and z['pack'] is not None:
        after=[(p,s) for p,s,u in trip if u=='in' and p>z['pack']]
        if after: pack_in=[after[0][1]]

    q=QTY.search(t)
    if not q:
        mm2=re.search(r'(装柜数\s*量|装箱量|装柜数量)\s*[:：]?\s*(\d{2,5})',t)
        q=re.match(r'.*?(\d+)',mm2.group(2)) if mm2 else None
    qty=f"{q.group(1)} pcs / 40HQ" if q else ''

    sm,si=size_mm[0] if size_mm else '', size_in[0] if size_in else ''
    pm,pi=pack_mm[0] if pack_mm else '', pack_in[0] if pack_in else ''
    if sm and si and not consistent(sm,si): si=''
    if pm and pi and not consistent(pm,pi): pi=''
    out[m['slug']]=dict(size_mm=sm,size_in=si,pack_mm=pm,pack_in=pi,qty=qty)


# 个别规格表 OCR 断行严重（如 AC41C 的 "686~1092 m / m"），按原图人工核对后写死
OVERRIDE = {
 'ac41c': dict(size_mm='439 × 673 × 686~1092 mm', size_in='17.3 × 26.5 × 27~43 in',
               pack_mm='408 × 650 × 270 mm', pack_in='16.1 × 25.6 × 10.6 in', qty='864 pcs / 40HQ'),
}
out.update(OVERRIDE)

json.dump(out, open(f"{ROOT}/.workbuddy/tmp/spec_params_v3.json",'w'), ensure_ascii=False, indent=1)
full=sum(1 for v in out.values() if (v['size_mm'] or v['size_in']) and (v['pack_mm'] or v['pack_in']) and v['qty'])
print(f"{len(out)} 款：有尺寸 {sum(1 for v in out.values() if v['size_mm'] or v['size_in'])}，三项齐全 {full}，全空 {sum(1 for v in out.values() if not (v['size_mm'] or v['size_in']))}")
