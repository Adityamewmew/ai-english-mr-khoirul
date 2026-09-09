import { useState } from 'react'
import AudioCheck from '../components/AudioCheck'
import usePlacement from '../store/usePlacement'
import { getStage1 } from '../api/client'
export default function Welcome(){
  const { set } = usePlacement()
  const [loading,setLoading]=useState(false)
  const [err,setErr]=useState("")
  const [checked,setChecked]=useState(false)
  const start=async()=>{
    setLoading(true); setErr("")
    try{
      const data=await getStage1(10)
      set({stage1:data.items, stage:1})
    }catch(e){ setErr(e.message || "Gagal load stage1. Pastikan backend jalan di :8000") }
    setLoading(false)
  }
  return <div style={{maxWidth:720, margin:'24px auto', padding:'0 16px'}}>
    <h1 style={{margin:'0 0 6px'}}>AI English Mr Khoirul</h1>
    <p style={{color:'#64748b', margin:'0 0 16px'}}>Placement test 35-45 menit: Listening + Reading + Speaking + Writing → CEFR A1-C2 (IELTS/TOEFL setara)</p>
    {!checked ? <AudioCheck onOk={()=>setChecked(true)} /> : <>
      <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginTop:12}}>
        <h3 style={{margin:'0 0 8px'}}>Siap mulai?</h3>
        <ul style={{color:'#475569', fontSize:14, margin:'0 0 12px 18px'}}>
          <li>Stage 1: 10 soal campur A1-B1 (5 menit)</li>
          <li>Stage 2: adaptif 10 soal sesuai skor kamu</li>
          <li>Writing + Speaking direkam/diketik, dinilai AI</li>
        </ul>
        {err && <div style={{color:'#dc2626', background:'#fef2f2', padding:8, borderRadius:8, marginBottom:8}}>{err}</div>}
        <button onClick={start} disabled={loading} style={{padding:'12px 24px', borderRadius:10, background:'#1e3a8a', color:'#fff', border:0, fontWeight:700, width:'100%'}}>
          {loading ? 'Memuat...' : 'Mulai Stage 1 → 10 Soal'}
        </button>
        <div style={{marginTop:10, fontSize:12, color:'#94a3b8', textAlign:'center'}}>Backend: /health, /placement/stage1, /grade</div>
      </div>
    </>}
  </div>
}
