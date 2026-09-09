import usePlacement from '../store/usePlacement'
import Progress from '../components/Progress'
function Bar({label, score, cefr}){
  const pct=Math.max(5, Math.min(100, score))
  const color= score<20?'#ef4444':score<40?'#f59e0b':score<60?'#eab308':score<80?'#22c55e':score<93?'#06b6d4':'#8b5cf6'
  return <div style={{marginBottom:10}}>
    <div style={{display:'flex', justifyContent:'space-between', fontSize:13}}><span style={{fontWeight:600}}>{label}</span><span>{cefr} · {score}/100</span></div>
    <div style={{height:14, background:'#e2e8f0', borderRadius:20, overflow:'hidden'}}><div style={{width:pct+'%', height:'100%', background:color, transition:'width .5s'}} /></div>
  </div>
}
export default function Result(){
  const { result, set, reset } = usePlacement()
  if(!result) return <div style={{padding:24, textAlign:'center'}}>Belum ada hasil. <button onClick={()=>set({stage:0})} style={{color:'#2563eb', background:'none', border:0, textDecoration:'underline'}}>Mulai lagi</button></div>
  const { overall_cefr, overall_score, skills, uneven_profile, equivalent, feedback_id } = result
  return <div style={{maxWidth:760, margin:'16px auto', padding:'0 16px'}}>
    <Progress stage={4} />
    <div style={{background:'linear-gradient(135deg,#1e3a8a,#0d9488)', color:'#fff', borderRadius:16, padding:20, textAlign:'center'}}>
      <div style={{fontSize:12, opacity:.8}}>LEVEL KAMU</div>
      <div style={{fontSize:48, fontWeight:900}}>{overall_cefr}</div>
      <div style={{fontSize:16}}>{equivalent?.label} — {equivalent?.group}</div>
      <div style={{marginTop:8, fontSize:13, background:'rgba(255,255,255,.15)', display:'inline-block', padding:'6px 12px', borderRadius:20}}>{overall_score}/100 · IELTS {equivalent?.ielts} · TOEFL {equivalent?.toefl_1_6}</div>
      {uneven_profile && <div style={{marginTop:10, fontSize:12, background:'#fef3c7', color:'#92400e', padding:'8px', borderRadius:8}}>⚠️ Profil tidak merata — ada skill gap &gt;1 level. Fokus skill terlemah.</div>}
    </div>
    <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginTop:12}}>
      <h3 style={{margin:'0 0 12px'}}>Radar Per Skill</h3>
      {Object.entries(skills||{}).map(([k,v])=> <Bar key={k} label={k.toUpperCase()} score={v.score_0_100} cefr={v.cefr} />)}
      {!skills || Object.keys(skills).length===0 ? <div style={{color:'#64748b'}}>Tidak ada detail skill</div> : null}
    </div>
    <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginTop:12}}>
      <h3 style={{margin:'0 0 8px'}}>Feedback</h3>
      <p style={{margin:0, color:'#334155'}}>{feedback_id}</p>
      {skills?.writing?.detail?.next_level_hint ? <p style={{color:'#64748b', fontSize:13}}>Next: {skills.writing.detail.next_level_hint}</p> : null}
      {skills?.speaking?.detail?.next_level_hint ? <p style={{color:'#64748b', fontSize:13}}>Speaking: {skills.speaking.detail.next_level_hint}</p> : null}
    </div>
    <div style={{display:'flex', gap:8, marginTop:12}}>
      <button onClick={()=>{ reset(); }} style={{flex:1, padding:'12px', borderRadius:10, background:'#1e3a8a', color:'#fff', border:0, fontWeight:700}}>🔄 Ulang Test</button>
      <button onClick={()=>window.print()} style={{padding:'12px 16px', borderRadius:10, background:'#e2e8f0', border:0}}>🖨️ Print</button>
    </div>
    <details style={{marginTop:12, fontSize:12, color:'#64748b'}}>
      <summary>Raw JSON (debug)</summary>
      <pre style={{whiteSpace:'pre-wrap', background:'#f1f5f9', padding:10, borderRadius:8, overflowX:'auto'}}>{JSON.stringify(result,null,2)}</pre>
    </details>
  </div>
}
