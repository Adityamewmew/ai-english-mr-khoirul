import { useEffect, useRef, useState } from 'react'
import usePlacement from '../store/usePlacement'
export default function LearnChat(){
  const store=usePlacement()
  const learn=store._learn
  const lesson=learn?.lesson
  const mod=learn?.module
  const grade=store.result?.overall_cefr||'B1'
  const [msgs,setMsgs]=useState([]) // {role, content}
  const [input,setInput]=useState("")
  const [loading,setLoading]=useState(false)
  const [quiz,setQuiz]=useState(null)
  const bottomRef=useRef(null)
  useEffect(()=>{
    if(!lesson) return
    // initial greeting via chat
    setLoading(true)
    fetch('/api/learn/lesson/chat',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({lesson_id:lesson.id, learner_cefr:grade, message:'Halo, mulai pelajaran ini. Sapa aku dan jelaskan singkat modulnya.', history:[]})}).then(r=>r.json()).then(d=>{
      setMsgs([{role:'assistant', content:d.reply}])
      setLoading(false)
    }).catch(()=>{ setMsgs([{role:'assistant', content:`Halo! Kita akan belajar ${lesson.title}. Contoh: ${lesson.exercise} — coba jawab ya!`}]); setLoading(false)})
  },[lesson?.id])
  useEffect(()=>{ bottomRef.current?.scrollIntoView({behavior:'smooth'}) },[msgs])
  const send=async()=>{
    if(!input.trim() || !lesson) return
    const userMsg={role:'user', content:input.trim()}
    const history=[...msgs, userMsg].slice(-10)
    setMsgs(prev=>[...prev, userMsg])
    setInput("")
    setLoading(true)
    try{
      const res=await fetch('/api/learn/lesson/chat',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({lesson_id:lesson.id, learner_cefr:grade, message:userMsg.content, history:msgs})}).then(r=>r.json())
      setMsgs(prev=>[...prev, {role:'assistant', content:res.reply}])
    }catch(e){
      setMsgs(prev=>[...prev, {role:'assistant', content:'[offline] '+e.message}])
    }
    setLoading(false)
  }
  const loadQuiz=async()=>{
    const q=await fetch(`/api/learn/lesson/${lesson.id}/quiz?n=3`).then(r=>r.json())
    setQuiz(q.quiz||[])
  }
  if(!lesson) return <div style={{padding:24}}>Pilih modul dulu di <button onClick={()=>store.set({stage:7})} style={{color:'#2563eb', background:'none', border:0, textDecoration:'underline'}}>Learn</button></div>
  return <div style={{maxWidth:760, margin:'0 auto', display:'flex', flexDirection:'column', height:'calc(100vh - 96px)'}}>
    <div style={{padding:'12px 16px', borderBottom:'1px solid #e2e8f0', background:'#fff', display:'flex', justifyContent:'space-between', alignItems:'center'}}>
      <div>
        <div style={{fontSize:11, color:'#64748b'}}>{mod?.id} · {lesson.cefr}</div>
        <div style={{fontWeight:700}}>{lesson.title}</div>
        <div style={{fontSize:12, color:'#64748b'}}>{lesson.objective} · Kelas {grade}</div>
      </div>
      <div style={{display:'flex', gap:8}}>
        <button onClick={()=>store.set({stage:7})} style={{padding:'8px 12px', borderRadius:8, background:'#f1f5f9', border:'1px solid #e2e8f0', fontSize:12}}>← Modul</button>
        <button onClick={()=>store.set({stage:5})} style={{padding:'8px 12px', borderRadius:8, background:'#e2e8f0', border:0, fontSize:12}}>Dashboard</button>
      </div>
    </div>
    <div style={{flex:1, overflowY:'auto', padding:12, background:'#f8fafc'}}>
      {msgs.map((m,i)=><div key={i} style={{display:'flex', justifyContent: m.role==='user'?'flex-end':'flex-start', marginBottom:8}}>
        <div style={{maxWidth:'78%', padding:'10px 14px', borderRadius: m.role==='user'?'18px 18px 4px 18px':'18px 18px 18px 4px', background: m.role==='user'?'#1e3a8a':'#fff', color: m.role==='user'?'#fff':'#1e293b', border: m.role==='assistant'?'1px solid #e2e8f0':'none', fontSize:14, whiteSpace:'pre-wrap'}}>{m.content}</div>
      </div>)}
      {loading && <div style={{color:'#64748b', fontSize:12}}>Guru AI mengetik...</div>}
      {quiz && <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:12, marginTop:8}}>
        <div style={{fontWeight:700, marginBottom:8}}>Quiz — {lesson.title}</div>
        {quiz.map((q,idx)=><div key={q.id} style={{marginBottom:10}}>
          <div style={{fontSize:13, fontWeight:600}}>{idx+1}. {q.question}</div>
          <div style={{display:'flex', gap:6, flexWrap:'wrap', marginTop:6}}>
            {q.options.map((o,oi)=><button key={oi} onClick={()=>alert(o===q.answer?'Benar!':'Jawaban benar: '+q.answer)} style={{padding:'6px 10px', borderRadius:20, border:'1px solid #e2e8f0', background:'#f8fafc', fontSize:12}}>{o}</button>)}
          </div>
        </div>)}
      </div>}
      <div ref={bottomRef} />
    </div>
    <div style={{padding:10, background:'#fff', borderTop:'1px solid #e2e8f0', display:'flex', gap:8}}>
      <button onClick={loadQuiz} style={{padding:'10px 12px', borderRadius:8, background:'#f1f5f9', border:'1px solid #e2e8f0', fontSize:12}}>📝 Quiz 3Q</button>
      <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder="Ketik jawabanmu... (Enter untuk kirim)" style={{flex:1, padding:'10px 12px', borderRadius:20, border:'1px solid #cbd5e1', fontSize:14}} />
      <button onClick={send} disabled={loading||!input.trim()} style={{padding:'10px 16px', borderRadius:20, background: input.trim()?'#1e3a8a':'#94a3b8', color:'#fff', border:0, fontWeight:700}}>Kirim</button>
    </div>
  </div>
}
