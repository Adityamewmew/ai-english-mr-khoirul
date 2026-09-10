import { useEffect, useRef, useState, useCallback } from 'react'

// States: idle | requesting_permission | listening | transcribing | thinking | speaking | error | stopped
const STATES={
  idle: {label:'Idle', icon:'⚪', color:'#64748b'},
  requesting_permission: {label:'Meminta izin mic', icon:'🎤', color:'#eab308'},
  listening: {label:'Listening', sub:'Bicara sekarang...', icon:'🎙️', color:'#22c55e'},
  transcribing: {label:'Transcribing', sub:'Mengubah suara jadi teks...', icon:'⏳', color:'#eab308'},
  thinking: {label:'Thinking', sub:'AI memproses...', icon:'🧠', color:'#0ea5e9'},
  speaking: {label:'Speaking', sub:'AI berbicara...', icon:'🔊', color:'#8b5cf6'},
  error: {label:'Error', icon:'⚠️', color:'#ef4444'},
  stopped: {label:'Stopped', icon:'⏹️', color:'#64748b'},
}

export default function VoiceConversation({lessonId, learnerCefr='B1', voice='en-US-AriaNeural', history=[], onTranscript, onReply}){
  const [state,setState]=useState('idle')
  const [err,setErr]=useState('')
  const [continuous,setContinuous]=useState(true) // loop
  const [muted,setMuted]=useState(false)
  const recRef=useRef(null)
  const audioRef=useRef(null)
  const stateRef=useRef(state)
  const transcriptRef=useRef('')

  useEffect(()=>{ stateRef.current=state },[state])

  const setError=(msg)=>{
    setState('error'); setErr(msg)
  }

  const requestPermission=async()=>{
    setState('requesting_permission')
    try{
      const stream=await navigator.mediaDevices.getUserMedia({audio:true})
      stream.getTracks().forEach(t=>t.stop())
      return true
    }catch(e){
      setError('Microphone permission is required. '+e.message)
      return false
    }
  }

  const startListening=useCallback(async()=>{
    const ok=await requestPermission()
    if(!ok) return
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition
    if(!SR){
      setError("Browser tidak support SpeechRecognition. Gunakan Chrome/Edge.")
      return
    }
    setErr(''); setState('listening')
    const rec=new SR()
    rec.lang='en-US'
    rec.interimResults=false
    rec.maxAlternatives=1
    rec.continuous=false
    rec.onresult=(e)=>{
      const text=e.results[0][0].transcript.trim()
      transcriptRef.current=text
      setState('transcribing')
      if(onTranscript) onTranscript(text)
      setTimeout(()=>{ handleTranscript(text) }, 400)
    }
    rec.onerror=(e)=>{
      if(e.error==='no-speech'){ setError("Couldn't understand your speech. Coba lagi."); setTimeout(()=>{ if(continuous && stateRef.current!=='stopped') startListening() }, 1200); return }
      if(e.error==='not-allowed'){ setError('Microphone permission denied.'); return }
      setError('STT error: '+e.error)
    }
    rec.onend=()=>{
      if(stateRef.current==='listening'){
        // no result -> error
        // handled via no-speech above, but fallback
      }
    }
    recRef.current=rec
    try{ rec.start() }catch(err){ setError(err.message) }
  },[continuous, onTranscript])

  const handleTranscript=async(text)=>{
    if(!text) { setState('listening'); return }
    setState('thinking')
    try{
      const res=await fetch('/api/learn/lesson/chat-voice',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({lesson_id: lessonId, learner_cefr: learnerCefr, message: text, history: history||[], voice})
      }).then(r=>{
        if(!r.ok) throw new Error('LLM error '+r.status)
        return r.json()
      })
      const reply=res.reply||''
      if(onReply) onReply(reply, res.audio_b64)
      if(!res.audio_b64){
        // TTS fallback: show text only
        setState(continuous?'listening':'idle')
        if(continuous) setTimeout(()=>startListening(), 800)
        return
      }
      // speaking
      setState('speaking')
      if(muted){
        setState(continuous?'listening':'idle')
        if(continuous) setTimeout(()=>startListening(), 500)
        return
      }
      const audio=new Audio(`data:audio/mpeg;base64,${res.audio_b64}`)
      audioRef.current=audio
      audio.onended=()=>{
        if(continuous && stateRef.current!=='stopped' && stateRef.current!=='error'){
          setTimeout(()=>startListening(), 600)
        } else {
          setState('idle')
        }
      }
      audio.onerror=()=>{
        // TTS error -> fallback text already shown via history
        setError('TTS failed, menampilkan teks saja.')
        if(continuous) setTimeout(()=>startListening(), 800)
      }
      try{ await audio.play() }catch(e){ setError('Audio play blocked: '+e.message) }
    }catch(e){
      setError('Something went wrong: '+(e.message||e))
    }
  }

  const stop=()=>{
    setState('stopped')
    try{ recRef.current?.stop() }catch{}
    try{ audioRef.current?.pause(); audioRef.current=null }catch{}
  }

  const s=STATES[state]||STATES.idle

  return <div style={{border: state==='error'?'1px solid #fecaca':'1px solid #e2e8f0', borderRadius:16, padding:16, background:'#fff', textAlign:'center'}}>
    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:10}}>
      <div style={{fontWeight:700, fontSize:13, color:'#1e293b'}}>Voice Conversation</div>
      <label style={{fontSize:12, color:'#64748b', display:'flex', gap:6, alignItems:'center'}}><input type="checkbox" checked={continuous} onChange={e=>setContinuous(e.target.checked)}/> Loop</label>
    </div>

    <div style={{background: state==='speaking'?'#f5f3ff': state==='listening'?'#f0fdf4' : '#f8fafc', borderRadius:12, padding:14, minHeight:88, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', border: `2px solid ${s.color}20`}}>
      <div style={{fontSize:28}}>{s.icon}</div>
      <div style={{fontWeight:800, color: s.color, marginTop:4}}>{s.label}</div>
      {s.sub && <div style={{fontSize:12, color:'#64748b'}}>{s.sub}</div>}
      {err && state==='error' && <div style={{fontSize:12, color:'#dc2626', background:'#fef2f2', padding:'8px 10px', borderRadius:8, marginTop:8, maxWidth:'100%', wordBreak:'break-word'}}>{err}</div>}
    </div>

    <div style={{display:'flex', gap:8, marginTop:12, justifyContent:'center'}}>
      {state==='idle' || state==='stopped' || state==='error' ? (
        <button onClick={startListening} style={{flex:1, padding:'12px', borderRadius:10, background:'#22c55e', color:'#fff', border:0, fontWeight:800}}>🎙️ Start Voice Conversation</button>
      ) : state==='listening' ? (
        <button onClick={stop} style={{flex:1, padding:'12px', borderRadius:10, background:'#e2e8f0', color:'#475569', border:0, fontWeight:700}}>Stop Listening</button>
      ) : state==='speaking' ? (
        <button onClick={()=>{ try{audioRef.current?.pause()}catch{}; if(continuous) startListening(); else setState('idle') }} style={{flex:1, padding:'12px', borderRadius:10, background:'#e2e8f0', color:'#475569', border:0, fontWeight:700}}>⏭️ Skip</button>
      ) : (
        <button onClick={stop} style={{flex:1, padding:'12px', borderRadius:10, background:'#f1f5f9', color:'#64748b', border:'1px solid #e2e8f0', fontWeight:600}}>■ Stop</button>
      )}
      <button onClick={()=>setMuted(v=>!v)} style={{padding:'12px 14px', borderRadius:10, background: muted?'#475569':'#f1f5f9', color: muted?'#fff':'#475569', border:'1px solid #e2e8f0', fontSize:12}}>{muted?'🔇':'🔊'}</button>
      <button onClick={stop} style={{padding:'12px 14px', borderRadius:10, background:'#dc2626', color:'#fff', border:0, fontWeight:700}}>End</button>
    </div>

    <div style={{marginTop:8, fontSize:11, color:'#94a3b8', textAlign:'center'}}>
      {state==='listening' && '🎙️ Listening → AI menunggu suara'}
      {state==='thinking' && '⏳ Thinking → AI memproses'}
      {state==='speaking' && '🔊 Speaking → AI berbicara'}
      {state==='error' && '⚠️ Error → coba lagi'}
      {(state==='idle'||state==='stopped') && 'Klik Start untuk mulai loop: Listening → Transcribing → Thinking → Speaking → Listening...'}
    </div>
  </div>
}
