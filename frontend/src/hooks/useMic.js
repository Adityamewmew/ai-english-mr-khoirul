import { useState, useRef } from 'react'
export default function useMic(){
  const [rec, setRec]=useState(false)
  const [transcript, setTranscript]=useState("")
  const recRef=useRef(null)
  const start=async()=>{
    const Speech = window.SpeechRecognition || window.webkitSpeechRecognition
    if(!Speech){ setTranscript(""); alert("Browser tidak support SpeechRecognition, ketik manual"); return }
    const r=new Speech(); r.lang='en-US'; r.interimResults=false; r.maxAlternatives=1
    r.onresult=e=>setTranscript(e.results[0][0].transcript)
    r.onend=()=>setRec(false)
    r.start(); recRef.current=r; setRec(true)
  }
  const stop=()=>{ try{recRef.current?.stop()}catch{}; setRec(false)}
  return {rec, transcript, setTranscript, start, stop}
}
