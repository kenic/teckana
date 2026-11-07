import collections,json,plistlib,tempfile,unittest
from pathlib import Path
from pipeline import ROOT,readcsv,measure,HIRA,sha
from audit import eligible,normalized
from mecabra_evaluate import classify

class DADSTests(unittest.TestCase):
 def test_index_and_translation_coverage(self):
  idx=json.loads((ROOT/'data/index.json').read_text());c=json.loads((ROOT/'data/concepts.json').read_text());t=readcsv(ROOT/'data/translations.tsv','\t')
  self.assertEqual(len(idx),1306);self.assertEqual(len(c),1123)
  self.assertEqual(sum(r['is_alias'] for r in idx),183)
  self.assertEqual({r['url'] for r in idx},{r['url'] for r in c})
  self.assertEqual({r['concept_id'] for r in c},{r['concept_id'] for r in t})
  self.assertEqual(len(t),len(c));self.assertTrue(all(r['japanese'] for r in t))
 def test_frozen_source_hash(self):
  p=json.loads((ROOT/'data/translation_provenance.json').read_text())
  self.assertEqual(p['concepts_sha256'],sha((ROOT/'data/concepts.json').read_bytes()))
  self.assertEqual(p['index_sha256'],json.loads((ROOT/'data/source.json').read_text())['sha256'])
 def test_unknown_or_missing_engine_not_missing_word(self):
  self.assertEqual(measure(Path('/nonexistent/mecabra'),'にぶんぎ','二分木')['status'],'not_measured')
  self.assertEqual(measure(ROOT/'src/mecabra_candidates','にぶんぎ','二分木',disabled=True)['status'],'not_measured')
 def test_export_gates(self):
  r=dict(audit_class='verified_miss',status='not_observed_exhausted',reading='にぶんぎ',surface='二分木',duplicate_of='')
  self.assertTrue(eligible(r,True));self.assertTrue(eligible(r))
  for status in ['not_measured','not_observed_truncated','top1','beyond_topN']:
   self.assertFalse(eligible(dict(r,status=status),True))
  for cat in ['hold_translation_or_reading','orthography_only','unmeasured','symbol_separate']:
   self.assertFalse(eligible(dict(r,audit_class=cat)))
  self.assertFalse(eligible(dict(r,audit_class='reviewed_miss'),True))
  self.assertFalse(eligible(dict(r,duplicate_of='c0001')))
 def test_exact_reading_filter(self):
  raw=dict(reading='にぶんぎ',candidates=[dict(surface='二分木',analysis_reading='にぶん',dictionary_reading='にぶんぎ',raw_rank=1)],enumeration_exhausted=True,raw_limit=1000,os='',guard='',analysis_flags=0,input_method_type=0,options=0)
  self.assertEqual(classify(raw,'二分木',15)['status'],'not_observed_exhausted')
  raw['candidates'][0]['analysis_reading']='にぶんぎ'
  self.assertEqual(classify(raw,'二分木',15)['status'],'top1')
 def test_orthography_not_semantics(self):
  self.assertEqual(normalized('ベルマン・フォード法'),normalized('ベルマンフォード法'))
  self.assertEqual(normalized('ＧＣＤ'),normalized('gcd'))
  self.assertNotEqual(normalized('B+木'),normalized('B木'))
 def test_real_measurement_links_and_counts(self):
  m=readcsv(ROOT/'outputs/master.csv');e=readcsv(ROOT/'outputs/mecabra_evaluation.csv');s=json.loads((ROOT/'outputs/summary.json').read_text())
  self.assertEqual(len(m),len(e));self.assertEqual(len(m),s['candidates'])
  self.assertEqual(dict(collections.Counter(r['mecabra_status'] for r in m)),s['statuses'])
  for r in e:
   if r['status']!='not_measured':
    ev=json.loads((ROOT/r['evidence_file']).read_text());self.assertEqual(ev['raw']['reading'],r['reading'])
    self.assertEqual(classify(ev['raw'],r['surface'],15)['status'],r['status'])
 def test_plist_provenance_and_duplicates(self):
  rows=readcsv(ROOT/'outputs/candidate_audit.csv');verified=plistlib.loads((ROOT/'outputs/macos_user_dictionary_verified.plist').read_bytes())
  selected=[r for r in rows if r['export_verified']=='True']
  self.assertEqual({(x['phrase'],x['shortcut']) for x in verified},{(r['surface'],r['reading']) for r in selected})
  self.assertEqual(len(verified),len({(x['phrase'],x['shortcut']) for x in verified}))
  for r in selected:
   self.assertTrue(r['review_evidence'].startswith('https://'))
   raw=json.loads((ROOT/r['evidence_file']).read_text())['raw'];self.assertTrue(raw['enumeration_exhausted']);self.assertEqual(raw['raw_limit'],10000)
 def test_abbreviations_and_corrected_readings(self):
  rows=readcsv(ROOT/'outputs/master.csv');pairs={(r['surface'],r['reading']) for r in rows}
  self.assertIn(('二分木','にぶんぎ'),pairs);self.assertIn(('赤黒木','あかくろぎ'),pairs)
  self.assertIn(('AVL','えーぶいえる'),pairs);self.assertIn(('FIFO','ふぁいふぉ'),pairs)
  self.assertIn(('FIFO','えふあいえふおー'),pairs)

if __name__=='__main__':unittest.main()
