import usePlacement from '../store/usePlacement'
import Progress from '../components/Progress'
import QuestionCard from '../components/QuestionCard'
import { postStage2 } from '../api/client'
import { useState } from 'react'
export default function Stage1(){
  const { stage1, answers, choose, set } = usePlacement()
  const [loading,setLoading]=useState(false)
  const [err,setErr]=useState("")
  const done = stage1.length>0 && stage1.every(it=> answers[it.id]!==undefined)
  const submit=async()=>{
    setLoading(true); setErr("")
    try{
      const ansArr = stage1.map(it=> ({cefr_tag:it.cefr, is_correct: answers[it.id]?.is_correct || false}))
      const exclude = stage1.map(it=>it.id)
      const data=await postStage2(ansArr, exclude, 10)
      set({estimate:data.estimate, stage2:data.items, stage:2})
    }catch(e){ setErr(e.message||"stage2 fail")}
    setLoading(false)
  }
  return <div style={{maxWidth:760, margin:'16px auto', padding:'0 16px'}}>
    <Progress stage={1} />
    <h2>Stage 1 — 10 Soal (A1-B1 campur)</h2>
    <p style={{color:'#64748b'}}>Jawab semua, lalu lanjut adaptif.</p>
    {stage1.map((it,i)=><QuestionCard key={it.id} item={it} idx={i} chosen={answers[it.id]?.chosen} onChoose={choose} />)}
    {err && <div style={{color:'#dc2626', background:'#fef2f2', padding:8, borderRadius:8, marginBottom:8}}>{err}</div>}
    <button disabled={!done || loading} onClick={submit} style={{padding:'12px 24px', borderRadius:10, background: done?'#1e3a8a':'#94a3b8', color:'#fff', border:0, fontWeight:700, width:'100%', marginTop:8}}>
      {loading ? 'Menghitung...' : done ? 'Submit Stage 1 → Stage 2 (adaptif)' : `Jawab dulu (${Object.keys(answers).length}/${stage1.length})`}
    </button>
  </div>
}
