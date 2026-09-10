import React from 'react'
import ReactDOM from 'react-dom/client'
import usePlacement from './store/usePlacement'
import Welcome from './pages/Welcome'
import Stage1 from './pages/Stage1'
import Stage2 from './pages/Stage2'
import WritingSpeaking from './pages/WritingSpeaking'
import Result from './pages/Result'
import Dashboard from './pages/Dashboard'
import Learn from './pages/Learn'
import LearnChat from './pages/LearnChat'
import LearnCall from './pages/LearnCall'

function Gate(){
  const stage = usePlacement(s=>s.stage)
  const init = usePlacement(s=>s.init)
  React.useEffect(()=>{ init() },[])
  if(stage===0) return <Welcome/>
  if(stage===1) return <Stage1/>
  if(stage===2) return <Stage2/>
  if(stage===3) return <WritingSpeaking/>
  if(stage===4) return <Result/>
  if(stage===6) return <LearnChat/>
  if(stage===7) return <Learn/>
  if(stage===8) return <LearnCall/>
  return <Dashboard/>
}
function App(){
  const stage = usePlacement(s=>s.stage)
  return <div>
    <div style={{background:'#fff', borderBottom:'1px solid #e2e8f0', padding:'10px 16px', display:'flex', justifyContent:'space-between', alignItems:'center', position:'sticky', top:0, zIndex:10}}>
      <div style={{fontWeight:800, color:'#1e3a8a'}}>AI English — Mr Khoirul</div>
      <div style={{display:'flex', gap:12, alignItems:'center'}}>
        <button onClick={()=>usePlacement.getState().set({stage:5})} style={{fontSize:12, background: stage===5?'#1e3a8a':'#f1f5f9', color: stage===5?'#fff':'#475569', border:'1px solid #e2e8f0', borderRadius:20, padding:'6px 12px', display: stage<5?'none':''}}>Dashboard</button>
        <button onClick={()=>usePlacement.getState().set({stage:7})} style={{fontSize:12, background: stage===7?'#1e3a8a':'#f1f5f9', color: stage===7?'#fff':'#475569', border:'1px solid #e2e8f0', borderRadius:20, padding:'6px 12px', display: stage<5 && stage!==7?'none':''}}>Belajar</button>
        <div style={{fontSize:12, color:'#64748b'}}>CEFR A1-C2</div>
      </div>
    </div>
    <Gate/>
    <div style={{textAlign:'center', color:'#94a3b8', fontSize:12, padding:'16px 0 24px'}}>© Mr Khoirul · CEFR Companion 2020 · IELTS/TOEFL 2026 mapping</div>
  </div>
}
ReactDOM.createRoot(document.getElementById('root')).render(<App/>)
