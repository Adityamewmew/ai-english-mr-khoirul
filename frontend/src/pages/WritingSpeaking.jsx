import usePlacement from '../store/usePlacement'
import Progress from '../components/Progress'
import useMic from '../hooks/useMic'
import { postGrade } from '../api/client'
import { useState } from 'react'
export default function WritingSpeaking(){
  const { answers, stage1, stage2, writing, speaking, set } = usePlacement()
  const { rec, transcript, setTranscript, start, stop } = useMic()
  const [loading,setLoading]=useState(false)
  const [err,setErr]=useState("")
  const submit=async()=>{
    if((writing||"").split(/\s+/).filter(Boolean).length < 20){
      setErr("Writing minimal 20 kata (sekarang "+(writing||"").split(/\s+/).filter(Boolean).length+")")
      return
    }
    const spoken = speaking || transcript
    if((spoken||"").split(/\s+/).filter(Boolean).length < 8){
      setErr("Speaking minimal ~8 kata (pakai mic atau ketik)")
      return
    }
    setLoading(true); setErr("")
    try{
      const all = [...stage1, ...stage2]
      const listening_items = all.filter(it=>it.skill==='listening').map(it=> ({skill:'listening', cefr_tag:it.cefr, is_correct: !!answers[it.id]?.is_correct}))
      const reading_items = all.filter(it=>it.skill!=='listening').map(it=> ({skill:'reading', cefr_tag:it.cefr, is_correct: !!answers[it.id]?.is_correct}))
      const payload={ listening_items, reading_items, writing_text: writing, speaking_transcript: spoken }
      const res=await postGrade(payload)
      set({result:res, stage:4})
    }catch(e){
      setErr(e.response?.data?.detail ? JSON.stringify(e.response.data.detail) : (e.message||"grade fail"))
    }
    setLoading(false)
  }
  return <div style={{maxWidth:760, margin:'16px auto', padding:'0 16px'}}>
    <Progress stage={3} />
    <h2>Writing & Speaking</h2>
    <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginBottom:12}}>
      <h3 style={{margin:'0 0 8px'}}>Writing (150-250 kata)</h3>
      <p style={{color:'#64748b', fontSize:13, margin:'0 0 8px'}}>Prompt: <i>Do you think online learning is effective? Give reasons and examples (min 20 kata untuk dinilai).</i></p>
      <textarea value={writing} onChange={e=>set({writing:e.target.value})} rows={7} placeholder="Tulis essay di sini... minimal 20 kata. Contoh B2 pakai although/however/therefore..." style={{width:'100%', padding:10, borderRadius:8, border:'1px solid #cbd5e1', fontSize:14}} />
      <div style={{fontSize:12, color:'#64748b', marginTop:4}}>{(writing||"").split(/\s+/).filter(Boolean).length} kata</div>
    </div>
    <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginBottom:12}}>
      <h3 style={{margin:'0 0 8px'}}>Speaking (60-90 detik)</h3>
      <p style={{color:'#64748b', fontSize:13}}>Prompt: <i>Talk about working from home — advantages and disadvantages. Or click mic and speak in English.</i></p>
      <div style={{display:'flex', gap:8, marginBottom:8}}>
        <button onClick={rec?stop:start} style={{padding:'10px 16px', borderRadius:8, background: rec?'#dc2626':'#2563eb', color:'#fff', border:0, fontWeight:700}}>{rec? '■ Stop':'🎙️ Start Mic'}</button>
        <button onClick={()=>setTranscript("")} style={{padding:'10px 16px', borderRadius:8, background:'#e2e8f0', border:0}}>Clear</button>
      </div>
      <textarea value={speaking || transcript} onChange={e=>{ set({speaking:e.target.value}); setTranscript(e.target.value)}} rows={4} placeholder="Hasil mic muncul di sini, atau ketik manual..." style={{width:'100%', padding:10, borderRadius:8, border:'1px solid #cbd5e1', fontSize:14}} />
      <div style={{fontSize:12, color:'#64748b', marginTop:4}}>{((speaking||transcript||"").split(/\s+/).filter(Boolean).length)} kata · mic: {rec?'recording':'idle'}</div>
    </div>
    {err && <div style={{color:'#dc2626', background:'#fef2f2', padding:10, borderRadius:8, marginBottom:8}}>{err}</div>}
    <div style={{display:'flex', gap:8}}>
      <button onClick={()=>set({stage:2})} style={{flex:1, padding:'12px', borderRadius:10, background:'#e2e8f0', border:0, fontWeight:600}}>← Stage 2</button>
      <button disabled={loading} onClick={submit} style={{flex:2, padding:'12px', borderRadius:10, background:'#1e3a8a', color:'#fff', border:0, fontWeight:700}}>{loading?'Menilai...':'Submit & Lihat Hasil →'}</button>
    </div>
  </div>
}
