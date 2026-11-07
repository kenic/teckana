"""DADS concept/alias -> reviewed translation draft -> readings -> actual Mecabra."""
import argparse,collections,csv,datetime,hashlib,importlib.metadata,json,os,platform,plistlib,re,subprocess,unicodedata
from pathlib import Path
import fugashi,unidic_lite
from sudachipy import dictionary,tokenizer
from mecabra_evaluate import classify
ROOT=Path(__file__).resolve().parents[1]
HIRA=re.compile(r'^[ぁ-ゖー]+$')
LETTERS=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ','えー びー しー でぃー いー えふ じー えいち あい じぇー けー える えむ えぬ おー ぴー きゅー あーる えす てぃー ゆー ぶい だぶりゅー えっくす わい ぜっと'.split()))
SPECIAL={'HyperLogLog':'はいぱーろぐろぐ','Soundex':'さうんでっくす','SSTable':'えすえすてーぶる','NIST':'にすと','ANSI':'あんしー'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def sha(b):return hashlib.sha256(b).hexdigest()
def hira(s):return ''.join(chr(ord(c)-96) if 'ァ'<=c<='ヶ' else c for c in s)
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def writecsv(p,rows,fields=None):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),extrasaction='ignore');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def readcsv(p,delimiter=','):
 with p.open(encoding='utf-8-sig') as f:return list(csv.DictReader(f,delimiter=delimiter))
def infer(surface,tagger,sudachi):
 # No dictionary success is used to choose pronunciation.
 chunks=re.findall(r'[A-Za-z]+|[^A-Za-z]+',surface);u=[];ss=[];unknown=[]
 for c in chunks:
  if re.fullmatch('[A-Za-z]+',c):
   if c in SPECIAL:r=SPECIAL[c]
   elif (len(c)<=12 and (c.isupper() or len(c)==1 or c in ('qm','st','skd','hB','kmp'))):r=''.join(LETTERS[a.upper()] for a in c)
   else:unknown.append(c);r=''
   u.append(r);ss.append(r)
  else:
   c=c.replace('・','').replace('-','').replace('_','').replace(' ','')
   if any(x in c for x in '0123456789²+*()αρ∼ωΩΘ'):unknown.append(c);continue
   for w in tagger(c):
    k=w.feature.kana
    if w.is_unk or not k:
     if re.fullmatch(r'[ぁ-ゖァ-ヶー]+',w.surface):k=w.surface
     else:unknown.append(w.surface);k=''
    u.append(hira(k))
   ms=sudachi.tokenize(c,tokenizer.Tokenizer.SplitMode.C)
   ss.extend(hira(m.reading_form()) for m in ms)
 r=''.join(u);s=''.join(ss)
 return r if not unknown and HIRA.fullmatch(r) else '',s,unknown

def measure(binary,reading,target,raw_limit=1000,disabled=False):
 if disabled:return dict(status='not_measured',error='Explicit --no-mecabra')
 if not binary.is_file():return dict(status='not_measured',error='CLI unavailable')
 fingerprint=sha(binary.read_bytes());key=sha(json.dumps([reading,fingerprint,platform.platform(),raw_limit,os.environ.get('MECABRA_ALREADY_SANDBOXED','')]).encode());path=ROOT/'evidence/mecabra'/(key+'.json')
 try:
  if path.exists():saved=json.loads(path.read_text())
  else:
   p=subprocess.run([str(binary),reading,str(raw_limit)],capture_output=True,text=True,timeout=35)
   if p.returncode:return dict(status='not_measured',error=f'CLI exit {p.returncode}: {p.stderr[-500:]}')
   raw=json.loads(p.stdout)
   if raw['reading']!=reading:raise ValueError('Input mismatch')
   saved=dict(raw=raw,measured_at=now(),binary_sha256=fingerprint);dump(path,saved)
  return dict(classify(saved['raw'],target,15),measured_at=saved['measured_at'],binary_sha256=fingerprint,evidence_file=str(path.relative_to(ROOT)))
 except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as e:return dict(status='not_measured',error=str(e))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--no-mecabra',action='store_true');ap.add_argument('--output',type=Path,default=ROOT/'outputs');a=ap.parse_args();out=a.output;out.mkdir(exist_ok=True,parents=True)
 concepts=json.loads((ROOT/'data/concepts.json').read_text());index=json.loads((ROOT/'data/index.json').read_text());source=json.loads((ROOT/'data/source.json').read_text())
 provenance=json.loads((ROOT/'data/translation_provenance.json').read_text())
 if provenance['index_sha256']!=source['sha256'] or provenance['concepts_sha256']!=sha((ROOT/'data/concepts.json').read_bytes()):raise ValueError('Source changed; review concept-to-translation alignment before continuing')
 translation_rows=readcsv(ROOT/'data/translations.tsv','\t');tr={r['concept_id']:r for r in translation_rows}
 assert len(tr)==len(translation_rows) and set(tr)=={r['concept_id'] for r in concepts}
 reviews={r['candidate_id']:r for r in readcsv(ROOT/'data/reviews.csv')} if (ROOT/'data/reviews.csv').exists() else {}
 tagger=fugashi.Tagger('-d "'+unidic_lite.DICDIR+'"');sudachi=dictionary.Dictionary(dict='core').create()
 candidates=[];urlmap={r['url']:r for r in concepts}
 for c in concepts:
  t=tr[c['concept_id']];s=t['japanese'];note=t.get('note') or ''
  kind='latin_or_mixed' if re.search('[A-Za-z]',s) else 'symbol' if not re.search('[一-龯ぁ-んァ-ヶ]',s) else 'japanese'
  candidates.append(dict(candidate_id=c['concept_id'],concept_id=c['concept_id'],english=c['english'],surface=s,url=c['url'],kind=kind,translation_note=note,translation_status='assistant_draft'))
 # Include uppercase alias spellings explicitly, separate from Japanese rendering.
 for i in index:
  en=i['english'];c=urlmap[i['url']]
  if i['is_alias'] and re.fullmatch(r'[A-Z][A-Z0-9-]{1,12}',en):
   candidates.append(dict(candidate_id=i['index_id']+'-abbr',concept_id=c['concept_id'],english=en,surface=en,url=i['url'],kind='abbreviation',translation_note='索引の略称。日本語対訳と別に英字出力を測定',translation_status='original_abbreviation'))
 # Acronyms within DADS headings, e.g. AVL in AVL tree, are useful outputs too.
 existing={c['surface'] for c in candidates}
 for c in concepts:
  for abbr in re.findall(r'(?<![A-Za-z])[A-Z][A-Z0-9]{1,11}(?![A-Za-z])',c['english']):
   if abbr in existing:continue
   existing.add(abbr)
   candidates.append(dict(candidate_id=c['concept_id']+'-abbr',concept_id=c['concept_id'],english=abbr,surface=abbr,url=c['url'],kind='abbreviation',translation_note='原典見出し中の略称を独立入力として評価',translation_status='original_abbreviation'))
 # Explicit alternate readings, never selected because they make the target appear.
 for s,r in [('ANSI','えーえぬえすあい'),('NIST','えぬあいえすてぃー'),('FIFO','ふぁいふぉ'),('LIFO','らいふぉ'),('DAG','だぐ'),('CORDIC','こーでぃっく'),('NYSIIS','ないしーす'),('ANSI','あんじー')]:
  c=next(c for c in candidates if c['surface']==s)
  candidates.append(dict(c, candidate_id=c['candidate_id']+('-spelled' if r in ('えーえぬえすあい','えぬあいえすてぃー') else '-alternate'),reading_override=r,translation_note=c['translation_note']+'; 別読み候補'))
 rows=[];ev=[]
 for c in candidates:
  d=dict(c);s=d['surface'];r,second,unknown=infer(s,tagger,sudachi);estimated=r
  rev=reviews.get(d['candidate_id'],{});r=rev.get('reading') or d.pop('reading_override','') or r
  status='assistant_estimated' if r else 'unknown';accept='not_reviewed'
  if rev:
   if rev.get('surface') and rev['surface']!=s:raise ValueError('Review surface mismatch')
   status=rev['reading_status'];accept=rev['decision'];d['translation_status']=rev.get('translation_status') or d['translation_status']
  if r and not HIRA.fullmatch(r):raise ValueError('Invalid kana '+d['candidate_id'])
  d.update(reading=r,initial_reading=estimated,sudachi_reading=second,dictionary_agreement=estimated==second and bool(estimated),unknown_segments=unknown,reading_status=status,review_decision=accept,review_note=rev.get('note',''),review_evidence=rev.get('evidence',''),retrieved_at=source['retrieved_at'],source_rights='NIST public-domain index headings; CRC Press definitions excluded; see SOURCE_POLICY.md',source_license_evidence=source['rights_source'],index_sha256=source['sha256'])
  if not r:res=dict(status='not_measured',error='Reading unresolved')
  else:res=measure(ROOT/'src/mecabra_candidates',r,s,disabled=a.no_mecabra)
  d.update(mecabra_status=res['status'],mecabra_rank=res.get('rank'),duplicate_of='')
  ev.append(dict(candidate_id=d['candidate_id'],surface=s,reading=r,**{k:v for k,v in res.items() if k!='reading'}));rows.append(d)
  if len(rows)%100==0:print('Evaluated',len(rows),flush=True)
 seen={}
 for r in rows:
  key=(r['surface'],r['reading'])
  if key in seen:r['duplicate_of']=seen[key]
  else:seen[key]=r['candidate_id']
 fields=list(dict.fromkeys(k for r in rows for k in r));writecsv(out/'master.csv',rows,fields)
 writecsv(out/'mecabra_evaluation.csv',ev,list(dict.fromkeys(k for r in ev for k in r)))
 by={r['concept_id']:r for r in rows if r['candidate_id']==r['concept_id']}
 indexrows=[]
 for i in index:
  r=by[urlmap[i['url']]['concept_id']]
  indexrows.append(dict(**i,concept_id=r['concept_id'],japanese=r['surface'],reading=r['reading'],translation_status=r['translation_status'],translation_note=r['translation_note'],mecabra_status=r['mecabra_status'],mapping_note='別名を参照先概念の訳語に正規化' if i['is_alias'] else '主見出し',retrieved_at=source['retrieved_at'],index_sha256=source['sha256'],license_evidence=source['rights_source']))
 writecsv(out/'index_master.csv',indexrows)
 writecsv(out/'needs_review.csv',[r for r in rows if r['mecabra_status'] not in ('top1','topN')],fields)
 writecsv(out/'latin_and_abbreviations.csv',[r for r in rows if r['kind'] in ('latin_or_mixed','abbreviation')],fields)
 summary=dict(generated_at=now(),index_rows=len(index),concepts=len(concepts),candidates=len(rows),unique_surface_reading_pairs=len(seen),statuses=dict(collections.Counter(r['mecabra_status'] for r in rows)),reading_disagreements=sum(not r['dictionary_agreement'] for r in rows),input_sha256=sha((ROOT/'data/translations.tsv').read_bytes()),platform=platform.platform(),software={k:importlib.metadata.version(k) for k in ['fugashi','unidic-lite','sudachipy','sudachidict_core']})
 dump(out/'summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
