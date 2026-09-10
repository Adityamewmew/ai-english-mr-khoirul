import { useEffect, useRef, useState } from 'react'
import usePlacement from '../store/usePlacement'
import VoiceConversation from '../components/VoiceConversation'

const VOICES=[
  {id:'en-US-AriaNeural', label:'Aria (US F)'},
  {id:'en-GB-SoniaNeural', label:'Sonia (UK F)'},
  {id:'en-US-GuyNeural', label:'Guy (US M)'},
  {id:'en-GB-RyanNeural', label:'Ryan (UK M)'},
]

export default function LearnCall(){
  const store=usePlacement()
  const learn=store._learn
  const lesson=learn?.lesson
  const mod=learn?.module
  const grade=store.result?.overall_cefr||'B1'
  const [msgs,setMsgs]=useState([]) // {role, content, audioB64?}
  const [input,setInput]=useState("")
  const [loading,setLoading]=useState(false)
  const [callOn,setCallOn]=useState(true) // telephony mode
  const [voice,setVoice]=useState('en-US-AriaNeural')
  const [muted,setMuted]=useState(false)
  const [listening,setListening]=useState(false)
  const recRef=useRef(null)
  const audioRef=useRef(null)

  // speech recognition
  const startListen=()=>{
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition
    if(!SR){ alert('Browser tidak support SpeechRecognition, ketik manual'); return }
    const r=new SR(); r.lang='en-US'; r.interimResults=false; r.maxAlternatives=1
    r.onstart=()=>setListening(true)
    r.onend=()=>setListening(false)
    r.onresult=e=>{ const t=e.results[0][0].transcript; setInput(prev=> prev? prev+' '+t : t) }
    r.onerror=()=>setListening(false)
    recRef.current=r; r.start()
  }
  const stopListen=()=>{ try{recRef.current?.stop()}catch{}; setListening(false) }

  const playB64=(b64)=>{
    if(!b64||muted) return
    try{
      const blob=new Blob([Uint8Array.from(atob(b64), c=>c.charCodeAt(0))], {type:'audio/mpeg'})
      const url=URL.createObjectURL(blob)
      if(audioRef.current){ audioRef.current.src=url; audioRef.current.play().catch(()=>{}) }
    }catch{}
  }

  // initial greeting via chat-voice
  useEffect(()=>{
    if(!lesson) return
    setLoading(true)
    fetch('/api/learn/lesson/chat-voice',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({lesson_id:lesson.id, learner_cefr:grade, message:'Halo, mulai pelajaran ini. Sapa aku singkat.', history:[], voice})}).then(r=>r.json()).then(d=>{
      setMsgs([{role:'assistant', content:d.reply, audioB64: d.audio_b64}])
      if(d.audio_b64) playB64(d.audio_b64)
      setLoading(false)
    }).catch(()=>{ setMsgs([{role:'assistant', content:`Halo! Kita belajar ${lesson.title}. ${lesson.exercise}`} ]); setLoading(false)})
  },[lesson?.id])

  const send=async()=>{
    const text=input.trim()
    if(!text||!lesson) return
    const userMsg={role:'user', content:text}
    const history=msgs.slice(-8).map(m=>({role:m.role, content:m.content}))
    setMsgs(prev=>[...prev, userMsg])
    setInput("")
    setLoading(true)
    try{
      const res=await fetch('/api/learn/lesson/chat-voice',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({lesson_id:lesson.id, learner_cefr:grade, message:text, history, voice})}).then(r=>r.json())
      const bot={role:'assistant', content:res.reply, audioB64:res.audio_b64}
      setMsgs(prev=>[...prev, bot])
      if(res.audio_b64) playB64(res.audio_b64)
    }catch(e){
      setMsgs(prev=>[...prev,{role:'assistant', content:'(offline) '+e.message}])
    }
    setLoading(false)
  }

  if(!lesson) return <div style={{padding:24}}>Pilih modul di <button onClick={()=>store.set({stage:7})} style={{color:'#2563eb', background:'none', border:0, textDecoration:'underline'}}>Belajar</button></div>

  return <div style={{maxWidth:760, margin:'0 auto', height:'calc(100vh - 72px)', display:'flex', flexDirection:'column', background:callOn?'#0f172a':'#f8fafc'}}>
    {/* phone header */}
    <div style={{background: callOn?'#1e293b':'#fff', color: callOn?'#fff':'#1e293b', padding:'12px 16px', display:'flex', justifyContent:'space-between', alignItems:'center', borderBottom: callOn?'1px solid #334155':'1px solid #e2e8f0'}}>
      <div style={{display:'flex', gap:12, alignItems:'center'}}>
        <div style={{width:40, height:40, borderRadius:'50%', background: callOn?'#22c55e':'#1e3a8a', display:'flex', alignItems:'center', justifyContent:'center', color:'#fff', fontWeight:800}}>{mod?.id?.slice(0,2)||'AI'}</div>
        <div>
          <div style={{fontWeight:700, fontSize:14}}>{callOn?'📞 Guru AI — Telepon': 'Guru AI — Chat'}</div>
          <div style={{fontSize:11, opacity:.7}}>{lesson.title} · {grade} · STT→LLM→TTS loop {callOn?'aktif':'mati'}</div>
        </div>
      </div>
      <div style={{display:'flex', gap:8, alignItems:'center'}}>
        <select value={voice} onChange={e=>setVoice(e.target.value)} style={{padding:'6px 8px', borderRadius:8, border:'1px solid '+(callOn?'#334155':'#e2e8f0'), background: callOn?'#334155':'#fff', color: callOn?'#fff':'#1e293b', fontSize:12}}>
          {VOICES.map(v=><option key={v.id} value={v.id}>{v.label}</option>)}
        </select>
        <button onClick={()=>setCallOn(v=>!v)} style={{padding:'8px 12px', borderRadius:20, background: callOn?'#0ea5e9':'#e2e8f0', color: callOn?'#fff':'#475569', border:0, fontWeight:700, fontSize:12}}>{callOn?'Chat':'Telepon'}</button>
        <button onClick={()=>store.set({stage:7})} style={{padding:'8px 12px', borderRadius:20, background:'#e2e8f0', color:'#475569', border:0, fontSize:12}}>Tutup</button>
      </div>
    </div>

    {/* call controls */}
    {callOn && <div style={{background:'#1e293b', padding:'10px 16px', display:'flex', gap:8, alignItems:'center'}}>
      <button onClick={()=>setMuted(v=>!v)} style={{flex:1, padding:'10px', borderRadius:10, background: muted?'#475569':'#22c55e', color:'#fff', border:0, fontWeight:700, fontSize:13}}>{muted?'🔇 Suara Mati':'🔊 Suara Hidup'}</button>
      <button onClick={muted?()=>setMuted(false):()=>{ if(audioRef.current) audioRef.current.pause() }} style={{padding:'10px 14px', borderRadius:10, background:'#dc2626', color:'#fff', border:0, fontWeight:700}}>Akhiri</button>
      <audio ref={audioRef} controls style={{display:'none'}} />
    </div>}

    {/* voice pipeline panel */}
    <div style={{padding:'10px 12px', background: callOn?'#0f172a':'#f8fafc', borderBottom: callOn?'1px solid #334155':'1px solid #e2e8f0'}}>
      <VoiceConversation
        lessonId={lesson?.id}
        learnerCefr={grade}
        voice={voice}
        history={msgs.map(m=>({role:m.role, content:m.content}))}
        onTranscript={(text)=>{
          setMsgs(prev=>[...prev, {role:'user', content: text}])
        }}
        onReply={(reply, audioB64)=>{
          setMsgs(prev=>[...prev, {role:'assistant', content: reply, audioB64 }])
          // auto play via VoiceConversation already handles audio, but also ensure LearnCall audioRef plays if b64 exists
          if(audioB64 && !muted && audioRef.current){
            try{
              const blob=new Blob([Uint8Array.from(atob(audioB64), c=>c.charCodeAt(0))], {type:'audio/mpeg'})
              const url=URL.createObjectURL(blob)
              audioRef.current.src=url
              audioRef.current.play().catch(()=>{})
            }catch{}
          }
        }}
      />
    </div>

    {/* messages */}
    <div style={{flex:1, overflowY:'auto' , padding:12, background: callOn?'#0f172a':'#f8fafc'}}>
      {msgs.map((m,i)=><div key={i} style={{display:'flex', justifyContent: m.role==='user'?'flex-end':'flex-start', marginBottom:8}}>
        <div style={{maxWidth:'82%', padding:'10px 14px', borderRadius: m.role==='user'?'18px 18px 4px 18px':'18px 18px 18px 4px', background: m.role==='user'? (callOn?'#2563eb':'#1e3a8a'): (callOn?'#1e293b':'#fff'), color: m.role==='user'?'#fff': (callOn?'#e2e8f0':'#1e293b'), border: m.role==='assistant' && !callOn?'1px solid #e2e8f0':'1px solid transparent', fontSize:14, whiteSpace:'pre-wrap', boxShadow: callOn?'0 2px 8px rgba(0,0,0,.3)':'none'}}>
          {m.content}
          {m.audioB64 && <div style={{marginTop:8}}><audio controls src={`data:audio/mpeg;base64,${m.audioB64}`} style={{width:'100%', height:32}} /></div>}
        </div>
      </div>)}
      {loading && <div style={{color: callOn?'#94a3b8':'#64748b', fontSize:12, textAlign:'center', marginTop:8}}>Guru AI mengetik & menyiapkan suara...</div>}
      <div style={{height:8}} />
    </div>

    {/* input bar - telepon style */}
    <div style={{padding:10, background: callOn?'#1e293b':'#fff', borderTop: callOn?'1px solid #334155':'1px solid #e2e8f0', display:'flex', gap:8, alignItems:'center'}}>
      <button onClick={listening?stopListen:startListen} style={{padding:'12px', borderRadius:'50%', background: listening?'#dc2626':'#22c55e', color:'#fff', border:0, width:44, height:44, display:'flex', alignItems:'center', justifyContent:'center', fontSize:16}} title="Mic (bicara → jadi teks)">{listening?'■':'🎙️'}</button>
      <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()} placeholder={callOn?"Bicara atau ketik — Enter kirim (guru akan menjawab dengan suara)":"Ketik jawaban..."} style={{flex:1, padding:'12px 14px', borderRadius:20, border:'1px solid '+(callOn?'#334155':'#cbd5e1'), background: callOn?'#334155':'#fff', color: callOn?'#fff':'#1e293b', fontSize:14}} />
      <button onClick={send} disabled={loading||!input.trim()} style={{padding:'12px 16px', borderRadius:20, background: input.trim()? (callOn?'#0ea5e9':'#1e3a8a'):'#475569', color:'#fff', border:0, fontWeight:700}}>{callOn?'📞':''} Kirim</button>
    </div>

    <audio ref={el=>{ if(el && !audioRef.current) audioRef.current=el }} style={{display:'none'}} />
  </div>
}
