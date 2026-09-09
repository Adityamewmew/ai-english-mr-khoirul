import { useState } from 'react'
export default function AudioCheck({onOk}){
  const [ok, setOk]=useState(false)
  return <div style={{border:'2px dashed #cbd5e1', borderRadius:12, padding:16, textAlign:'center', background:'#fff'}}>
    <h3 style={{margin:'0 0 8px'}}>Cek Audio dan Mic</h3>
    <p style={{color:'#64748b', margin:'0 0 12px'}}>Pastikan listening terdengar dan mic bisa rekam untuk Speaking.</p>
    <audio controls src="/api/listening/audio/L-A1-01" style={{width:'100%'}} />
    <div style={{marginTop:12}}>
      <label style={{display:'inline-flex', gap:8, alignItems:'center'}}><input type="checkbox" checked={ok} onChange={e=>setOk(e.target.checked)}/> Saya sudah cek audio</label>
    </div>
    <button disabled={!ok} onClick={onOk} style={{marginTop:12, padding:'10px 22px', borderRadius:8, background: ok?'#1e3a8a':'#94a3b8', color:'#fff', border:0, fontWeight:600}}>Lanjut ke Stage 1</button>
  </div>
}
