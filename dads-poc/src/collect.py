"""Parse the single official DADS index; never crawl definitions."""
import argparse,csv,datetime,hashlib,json,re,time,urllib.request,urllib.error,urllib.robotparser
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
URL='https://xlinux.nist.gov/dads/'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');a=ap.parse_args()
 p=ROOT/'evidence/index.html';p.parent.mkdir(parents=True,exist_ok=True)
 robots_status=json.loads((ROOT/'data/source.json').read_text()).get('robots_http_status') if (ROOT/'data/source.json').exists() else None
 if not p.exists():
  if not a.fetch:raise RuntimeError('Index cache absent; use --fetch only after reviewing source conditions')
  ua='JapaneseTerminologyDADSPoC/1.0 (single-index research)'
  try:
   with urllib.request.urlopen(urllib.request.Request('https://xlinux.nist.gov/robots.txt',headers={'User-Agent':ua}),timeout=30) as response:robots=response.read(100000).decode();robots_status=response.status
   parser=urllib.robotparser.RobotFileParser();parser.parse(robots.splitlines())
   if not parser.can_fetch(ua,URL):raise RuntimeError('robots disallows index')
   (ROOT/'evidence/robots.txt').write_text(robots)
  except urllib.error.HTTPError as e:
   if e.code not in (404,410):raise
   robots_status=e.code
   (ROOT/'evidence/robots.txt').write_text('HTTP '+str(e.code))
  time.sleep(2)
  with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':ua}),timeout=45) as response:
   raw=response.read(2_000_001)
   if len(raw)>2_000_000:raise ValueError('Index size cap exceeded')
  p.write_bytes(raw)
 raw=p.read_bytes();html=raw.decode('utf-8');rows=[]
 # HTML4 omits closing dt tags; isolate each dt up to next tag before parsing.
 for m in re.finditer(r'<dt\b[^>]*>(.*?)(?=<dt\b|</dl>)',html,re.S|re.I):
  s=BeautifulSoup(m.group(1),'html.parser');a=s.find('a',href=re.compile(r'^HTML/'))
  if not a:continue
  whole=s.get_text(' ',strip=True);target=a.get_text(' ',strip=True)
  alias=bool(re.search(r':\s*see\s',whole));english=re.split(r':\s*see\s',whole)[0].strip() if alias else target
  rows.append(dict(index_id=f'dads-{len(rows)+1:04}',english=english,canonical_english=target,url=urljoin(URL,a['href']),is_alias=alias))
 assert len(rows)>1200 and len({r['english'] for r in rows})==len(rows)
 concepts=[dict(r,concept_id=f'c{i:04}') for i,r in enumerate((x for x in rows if not x['is_alias']),1)]
 (ROOT/'data/concepts.json').write_text(json.dumps(concepts,ensure_ascii=False,indent=2)+'\n')
 (ROOT/'data/index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 meta=dict(url=URL,retrieved_at=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(raw).hexdigest(),index_rows=len(rows),distinct_urls=len({r['url'] for r in rows}),alias_rows=sum(r['is_alias'] for r in rows),robots_http_status=robots_status,scope='Index headings only; no entry definitions downloaded; CRC Press definitions not copied',rights_source='https://catalog.data.gov/dataset/dictionary-of-algorithms-and-data-structures-dads')
 (ROOT/'data/source.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,indent=2))
 with (ROOT/'data/index.tsv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
