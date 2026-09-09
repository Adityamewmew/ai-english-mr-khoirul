import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import usePlacement from './store/usePlacement'
import Welcome from './pages/Welcome'
import Stage1 from './pages/Stage1'
import Stage2 from './pages/Stage2'
import WritingSpeaking from './pages/WritingSpeaking'
import Result from './pages/Result'

function Gate(){
  const { stage } = usePlacement()
  // simple stage router
  if(stage===0) return <Welcome/>
  if(stage===1) return <Stage1/>
  if(stage===2) return <Stage2/>
  if(stage===3) return <WritingSpeaking/>
  return <Result/>
}
function App(){
  return <div>
    <div style={{background:'#fff', borderBottom:'1px solid #e2e8f0', padding:'10px 16px', display:'flex', justifyContent:'space-between', alignItems:'center', position:'sticky', top:0, zIndex:10}}>
      <div style={{fontWeight:800, color:'#1e3a8a'}}>AI English — Mr Khoirul</div>
      <div style={{fontSize:12, color:'#64748b'}}>CEFR A1-C2 · 4 skills</div>
    </div>
    <Gate/>
    <div style={{textAlign:'center', color:'#94a3b8', fontSize:12, padding:'16px 0 24px'}}>© Mr Khoirul · CEFR Companion 2020 · IELTS/TOEFL 2026 mapping</div>
  </div>
}
ReactDOM.createRoot(document.getElementById('root')).render(<App/>)
