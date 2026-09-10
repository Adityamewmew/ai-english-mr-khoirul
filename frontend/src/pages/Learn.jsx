import { useEffect, useState } from 'react'
import usePlacement from '../store/usePlacement'
import { useNavigate } from 'react-router-dom'
const API="/api"
export default function Learn(){
  const { result } = usePlacement()
  const grade = result?.overall_cefr || 'B1'
  const [mods,setMods]=useState([])
  const [loading,setLoading]=useState(true)
  useEffect(()=>{
    fetch(`/api/learn/modules?grade=${grade}`).then(r=>r.json()).then(d=>{ setMods(d.modules||[]); setLoading(false)}).catch(()=>setLoading(false))
  },[grade])
  if(loading) return <div style={{padding:24, textAlign:'center'}}>Memuat modul {grade}...</div>
  return <div style={{maxWidth:900, margin:'16px auto', padding:'0 16px'}}>
    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
      <h2 style={{margin:0}}>Modul Belajar — Kelas {grade}</h2>
      <a href="/dashboard" onClick={e=>{e.preventDefault(); usePlacement.getState().set({stage:5})}} style={{fontSize:13, color:'#2563eb'}}>← Dashboard</a>
    </div>
    <p style={{color:'#64748b', fontSize:13}}>Pilih modul, ngobrol langsung dengan Guru AI (chat). {mods.length} modul terbuka untuk kelas ini.</p>
    <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(260px,1fr))', gap:12}}>
      {mods.map(m=><ModCard key={m.id} m={m} />)}
    </div>
    {mods.length===0 && <div style={{color:'#64748b', textAlign:'center', marginTop:12}}>Belum ada modul untuk {grade}. Coba ganti grade.</div>}
  </div>
}
function ModCard({m}){
  const go=()=>{
    const id=m.id
    // open chat via stage 6 with lesson param
    const prog=usePlacement.getState()
    fetch(`/api/learn/lessons?module_id=${id}`).then(r=>r.json()).then(d=>{
      const first=d.lessons?.[0]
      if(first) prog.set({stage:6, _learn:{module:m, lesson:first}})
      else alert('Belum ada lesson untuk modul ini')
    })
  }
  return <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:14}}>
    <div style={{fontSize:11, color:'#64748b'}}>{m.id} · {m.cefr} · {m.group}</div>
    <div style={{fontWeight:700, margin:'4px 0'}}>{m.title}</div>
    <div style={{fontSize:13, color:'#475569'}}>{m.objective}</div>
    <div style={{fontSize:11, color:'#64748b', marginTop:6}}>{m.points?.slice(0,3).join(' • ')}</div>
    <div style={{fontSize:11, color:'#64748b'}}>Tests: {m.tests?.join(', ')}</div>
    <button onClick={go} style={{marginTop:10, width:'100%', padding:'10px', borderRadius:8, background:'#1e3a8a', color:'#fff', border:0, fontWeight:700}}>Ngobrol dengan Guru AI →</button>
  </div>
}
