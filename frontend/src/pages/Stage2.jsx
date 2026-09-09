import usePlacement from '../store/usePlacement'
import Progress from '../components/Progress'
import QuestionCard from '../components/QuestionCard'
import { useState } from 'react'
export default function Stage2(){
  const { stage2, stage1, answers, choose, set, estimate } = usePlacement()
  const [err,setErr]=useState("")
  const done = stage2.length>0 && stage2.every(it=> answers[it.id]!==undefined)
  return <div style={{maxWidth:760, margin:'16px auto', padding:'0 16px'}}>
    <Progress stage={2} />
    <h2>Stage 2 — Adaptif (target {estimate?.cefr || '…'})</h2>
    <p style={{color:'#64748b'}}>Skor sementara: {estimate?.score} → {estimate?.cefr} · {estimate?.raw}% raw · n={estimate?.n}</p>
    {stage2.map((it,i)=><QuestionCard key={it.id} item={it} idx={i} chosen={answers[it.id]?.chosen} onChoose={choose} />)}
    {err && <div style={{color:'#dc2626', background:'#fef2f2', padding:8, borderRadius:8}}>{err}</div>}
    <div style={{display:'flex', gap:8, marginTop:12}}>
      <button onClick={()=>set({stage:1})} style={{flex:1, padding:'12px', borderRadius:10, background:'#e2e8f0', border:0, fontWeight:600}}>← Kembali</button>
      <button disabled={!done} onClick={()=>set({stage:3})} style={{flex:2, padding:'12px', borderRadius:10, background: done?'#0d9488':'#94a3b8', color:'#fff', border:0, fontWeight:700}}>
        {done ? 'Lanjut Writing & Speaking →' : `Jawab dulu (${stage2.filter(it=>answers[it.id]).length}/${stage2.length})`}
      </button>
    </div>
  </div>
}
