"""Recheck all misses, distinguish spelling-only differences, export with review gates."""
import argparse,collections,json,plistlib,re,unicodedata
from pathlib import Path
from pipeline import ROOT,readcsv,writecsv,dump,measure,now,HIRA

def normalized(s):return re.sub(r'[\s・·‐‑–—-]','',unicodedata.normalize('NFKC',s)).casefold()
def eligible(r,strict=False):
 return (r['audit_class'] in (('verified_miss',) if strict else ('verified_miss','reviewed_miss'))
  and r['status']=='not_observed_exhausted' and HIRA.fullmatch(r['reading'] or '')
  and len(r['reading'])<=32 and len(r['surface'])<=64 and not r.get('duplicate_of'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'outputs');ap.add_argument('--no-mecabra',action='store_true');a=ap.parse_args();out=a.output
 master=readcsv(out/'master.csv');ev={r['candidate_id']:r for r in readcsv(out/'mecabra_evaluation.csv')};rows=[]
 for r in master:
  status=r['mecabra_status'];res=ev[r['candidate_id']]
  if status.startswith('not_observed') and not a.no_mecabra:
   res=measure(ROOT/'src/mecabra_candidates',r['reading'],r['surface'],10000)
  if a.no_mecabra:res=dict(status='not_measured',error='Explicit --no-mecabra')
  status=res['status'];equivalent=[];has_verified_sibling=False
  if status=='not_observed_exhausted' and res.get('evidence_file'):
   raw=json.loads((ROOT/res['evidence_file']).read_text())['raw']
   for c in raw['candidates']:
    if c['analysis_reading']==r['reading'] and c['dictionary_reading']==r['reading'] and normalized(c['surface'])==normalized(r['surface']):
     if c['surface'] not in equivalent:equivalent.append(c['surface'])
  if status=='not_measured':kind='unmeasured'
  elif status in ('top1','topN'):kind='already_top15'
  elif status=='beyond_topN':kind='low_rank'
  elif status=='not_observed_truncated':kind='truncated'
  elif equivalent:kind='orthography_only'
  elif r['review_decision']=='accepted_verified' and r['reading_status']=='source_verified' and r['translation_status']=='source_verified':kind='verified_miss'
  elif r['review_decision']=='accepted_review' and r['reading_status']=='assistant_reviewed':kind='reviewed_miss'
  elif r['review_decision']=='symbol_separate':kind='symbol_separate'
  else:kind='hold_translation_or_reading'
  d=dict(candidate_id=r['candidate_id'],concept_id=r['concept_id'],english=r['english'],surface=r['surface'],reading=r['reading'],kind=r['kind'],status=status,audit_class=kind,
         duplicate_of=r['duplicate_of'],reading_status=r['reading_status'],translation_status=r['translation_status'],review_decision=r['review_decision'],note=r['review_note'] or r['translation_note'],source_url=r['url'],review_evidence=r['review_evidence'],
         punctuation_or_case_equivalents=equivalent,raw_count=res.get('raw_count',''),raw_limit=res.get('raw_limit',''),rank=res.get('rank',''),enumeration_exhausted=res.get('enumeration_exhausted',''),evidence_file=res.get('evidence_file',''),error=res.get('error',''))
  d['other_readings_with_hits']=[dict(reading=x['reading'],status=x['mecabra_status'],rank=x['mecabra_rank']) for x in master if x['surface']==r['surface'] and x['reading']!=r['reading'] and x['mecabra_status'] in ('top1','topN','beyond_topN')]
  d['export_verified']=bool(eligible(d,True));d['export_review']=bool(eligible(d));rows.append(d)
  if len(rows)%100==0:print('Audited',len(rows),flush=True)
 writecsv(out/'candidate_audit.csv',rows)
 writecsv(out/'missing_candidates.csv',[r for r in rows if r['audit_class'] in ('verified_miss','reviewed_miss')],list(rows[0]))
 writecsv(out/'held_candidates.csv',[r for r in rows if r['audit_class'] in ('hold_translation_or_reading','unmeasured','symbol_separate','truncated')],list(rows[0]))
 writecsv(out/'orthography_only.csv',[r for r in rows if r['audit_class']=='orthography_only'],list(rows[0]))
 writecsv(out/'low_rank.csv',[r for r in rows if r['audit_class']=='low_rank'],list(rows[0]))
 for label,strict in [('verified',True),('review',False)]:
  chosen=[r for r in rows if eligible(r,strict)]
  writecsv(out/('macos_user_dictionary_'+label+'.csv'),chosen,['reading','surface','candidate_id','audit_class','source_url','review_evidence','other_readings_with_hits'])
  with (out/('macos_user_dictionary_'+label+'.plist')).open('wb') as f:plistlib.dump([dict(phrase=r['surface'],shortcut=r['reading']) for r in chosen],f)
 prior={r['candidate_id']:r for r in readcsv(ROOT/'evidence/pre-review/master.csv')};changes=[]
 for r in master:
  p=prior.get(r['candidate_id'])
  if p and (p['reading']!=r['reading'] or p['surface']!=r['surface']):changes.append(dict(candidate_id=r['candidate_id'],surface=r['surface'],old_surface=p['surface'],old_reading=p['reading'],new_reading=r['reading'],old_status=p['mecabra_status'],new_status=r['mecabra_status']))
 writecsv(out/'reading_corrections.csv',changes)
 unique=[r for r in rows if not r['duplicate_of']]
 summary=dict(generated_at=now(),all_rows=len(rows),unique_pairs=len(unique),audit_classes=dict(collections.Counter(r['audit_class'] for r in rows)),unique_audit_classes=dict(collections.Counter(r['audit_class'] for r in unique)),
  verified_export=sum(eligible(r,True) for r in rows),review_export=sum(eligible(r) for r in rows),reading_or_surface_changes=len(changes),
  verified_misses_with_other_reading_hits=sum(r['audit_class']=='verified_miss' and bool(r['other_readings_with_hits']) for r in unique),
  non_japanese_verified_misses=sum(r['audit_class']=='verified_miss' and r['kind']!='japanese' for r in unique),
  notes='All source headings processed; translations are drafts unless individually verified. Exact engine output, not GUI rank or dictionary membership. Orthographic equivalence is diagnostic only.')
 dump(out/'audit_summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
