'use strict';
const TERMS=window.TERMS,KEY='dads-review-178-v1',STATUSES=['未確認','採用','不採用','保留'];
const DATASET='dads-2026-11-07-178';
let state={},filter='すべて',storageOK=true,pendingImport=null;
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function validate(data){
 if(!data||data.dataset!==DATASET||data.version!==1||!data.records||typeof data.records!=='object'||Array.isArray(data.records))throw Error('この178件用のバックアップではありません。');
 const ids=new Set(TERMS.map(t=>t.candidate_id)),result={};
 for(const [id,v] of Object.entries(data.records)){
  if(!ids.has(id)||!v||typeof v!=='object'||!STATUSES.includes(v.status))throw Error('判定または項目IDが正しくありません。');
  for(const k of ['comment','editedReading','editedSurface','updatedAt'])if(typeof v[k]!=='string'||v[k].length>20000)throw Error('記録の形式が正しくありません。');
  result[id]={status:v.status,comment:v.comment,editedReading:v.editedReading,editedSurface:v.editedSurface,updatedAt:v.updatedAt};
 }
 return result;
}
function record(id){return state[id]||{status:'未確認',comment:'',editedReading:'',editedSurface:'',updatedAt:''};}
function envelope(){return {version:1,dataset:DATASET,exportedAt:new Date().toISOString(),records:state};}
try{const saved=localStorage.getItem(KEY);if(saved)state=validate(JSON.parse(saved));}catch(e){storageOK=false;$('save').textContent='保存データを読めません。バックアップを書き出してください';$('save').className='error';}
function save(){
 try{if(!storageOK)throw Error('保存不可');localStorage.setItem(KEY,JSON.stringify(envelope()));$('save').textContent='✓ このブラウザに保存済み';$('save').className='';}
 catch(e){$('save').textContent='自動保存できません。バックアップ保存を使ってください';$('save').className='error';}
}
function update(id,key,value){state[id]={...record(id),[key]:value,updatedAt:new Date().toISOString()};save();}
function counts(){return TERMS.reduce((a,t)=>(a[record(t.candidate_id).status]++,a),Object.fromEntries(STATUSES.map(s=>[s,0])));}
function summary(){const c=counts();document.querySelector('.stats').innerHTML=STATUSES.map(s=>`<div class="stat"><span>${s}</span><strong>${c[s]}</strong></div>`).join('');$('bar').style.width=((178-c.未確認)/178*100)+'%';$('filters').innerHTML=['すべて',...STATUSES].map(s=>`<button data-filter="${s}" aria-pressed="${s===filter}">${s} <span>${s==='すべて'?178:c[s]}</span></button>`).join('');}
function shown(){const q=$('search').value.normalize('NFKC').toLowerCase(),cf=$('confidence').value;return TERMS.filter(t=>{const r=record(t.candidate_id);return (filter==='すべて'||r.status===filter)&&(cf==='all'||t.audit_class===cf)&&[t.surface,t.reading,t.english,r.comment,r.editedSurface,r.editedReading].some(x=>String(x).normalize('NFKC').toLowerCase().includes(q));});}
function render(){summary();const terms=shown();$('count').textContent=`${terms.length} / 178 件`; $('empty').hidden=!!terms.length;
 $('list').innerHTML=terms.map(t=>{const r=record(t.candidate_id),verified=t.audit_class==='verified_miss';return `<article class="card" data-id="${esc(t.candidate_id)}" data-status="${r.status}"><div><div class="meta"><span>${esc(t.candidate_id)}</span><span class="badge ${verified?'verified':''}">${verified?'外部根拠あり':'AI点検・要レビュー'}</span></div><h2 class="term">${esc(t.surface)}</h2><p class="reading">${esc(t.reading)}</p><p class="english">${esc(t.english)}</p><div class="links"><a href="${esc(t.source_url)}" target="_blank" rel="noopener noreferrer">DADSの原典 ↗</a>${t.review_evidence.startsWith('https://')?`<a href="${esc(t.review_evidence)}" target="_blank" rel="noopener noreferrer">確認資料 ↗</a>`:''}</div><details class="edits"><summary>読み・表記の修正／確認メモ</summary><p>${esc(t.note)}</p><div class="editgrid"><label>修正した読み<input data-field="editedReading" aria-label="${esc(t.surface)}の修正読み" value="${esc(r.editedReading)}" placeholder="変更する場合のみ入力"></label><label>修正した表記<input data-field="editedSurface" aria-label="${esc(t.surface)}の修正表記" value="${esc(r.editedSurface)}" placeholder="変更する場合のみ入力"></label></div><p class="warning">修正したものは、辞書にまとめる前に再測定します。</p></details></div><div><div class="decisions" role="group" aria-label="${esc(t.surface)}の判定">${STATUSES.slice(1).map(s=>`<button data-value="${s}" aria-pressed="${r.status===s}">${s}</button>`).join('')}</div><label class="commentlabel" for="comment-${esc(t.candidate_id)}">コメント</label><textarea id="comment-${esc(t.candidate_id)}" data-field="comment" maxlength="20000" placeholder="読みの確認、使い道、保留の理由など">${esc(r.comment)}</textarea><button class="reset" data-value="未確認">未確認に戻す</button></div></article>`;}).join('');}
function toast(text){$('toast').textContent=text;$('toast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').hidden=true,4000);}
$('list').addEventListener('click',e=>{const b=e.target.closest('button[data-value]');if(!b)return;const id=b.closest('[data-id]').dataset.id;update(id,'status',b.dataset.value);render();});
$('list').addEventListener('input',e=>{if(!e.target.dataset.field)return;update(e.target.closest('[data-id]').dataset.id,e.target.dataset.field,e.target.value);});
$('filters').addEventListener('click',e=>{const b=e.target.closest('[data-filter]');if(b){filter=b.dataset.filter;render();}});
$('search').addEventListener('input',render);$('confidence').addEventListener('change',render);
function download(name,text,type){const a=document.createElement('a'),url=URL.createObjectURL(new Blob([text],{type}));a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function cell(value){let s=String(value??'');if(/^[\s]*[=+@-]/.test(s)||/^[\t\r\n]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';}
function csv(selected){const keys=['candidate_id','reading','surface','english','audit_class','source_url','review_evidence','判定','コメント','修正読み','修正表記','更新日時'];const rows=selected.map(t=>{const r=record(t.candidate_id);return {...t,判定:r.status,コメント:r.comment,修正読み:r.editedReading,修正表記:r.editedSurface,更新日時:r.updatedAt};});return '\ufeff'+[keys,...rows.map(r=>keys.map(k=>r[k]))].map(row=>row.map(cell).join(',')).join('\r\n')+'\r\n';}
function date(){return new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Tokyo'}).format(new Date());}
$('export').onclick=()=>{download(`DADS_178件_レビュー_${date()}.csv`,csv(TERMS),'text/csv;charset=utf-8');toast('全178件の判定とコメントを書き出しました');};
$('accepted').onclick=()=>{const selected=TERMS.filter(t=>record(t.candidate_id).status==='採用');if(!selected.length){toast('採用にした候補はまだありません');return;}download(`DADS_採用候補_${date()}.csv`,csv(selected),'text/csv;charset=utf-8');toast(`${selected.length}件の採用候補を書き出しました`);};
$('backup').onclick=()=>{download(`DADS_レビュー保存_${date()}.json`,JSON.stringify(envelope(),null,2),'application/json');toast('判定・コメント・修正内容のバックアップを保存しました');};
$('restore').onclick=()=>$('file').click();$('file').onchange=async e=>{const file=e.target.files[0];e.target.value='';if(!file)return;try{if(file.size>8*1024*1024)throw Error('ファイルが大きすぎます。');pendingImport=validate(JSON.parse(await file.text()));$('importInfo').textContent=`「${file.name}」の${Object.keys(pendingImport).length}件の編集記録を読み込みます。`; $('importDialog').showModal();}catch(err){toast('読み込めません：'+err.message);}};
$('cancelImport').onclick=()=>{pendingImport=null;$('importDialog').close();};$('confirmImport').onclick=()=>{if(!pendingImport)return;state=pendingImport;pendingImport=null;storageOK=true;save();render();$('importDialog').close();toast('バックアップを読み込みました');};
// Another tab's saved changes refresh this tab without silently overwriting them.
window.addEventListener('storage',e=>{if(e.key!==KEY||!e.newValue)return;try{state=validate(JSON.parse(e.newValue));render();$('save').textContent='✓ 別タブの保存内容を反映';}catch(err){toast('別タブの保存内容を読み込めません');}});
render();if(storageOK){$('save').textContent='✓ このブラウザに自動保存';}
