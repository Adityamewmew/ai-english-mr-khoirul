export default function QuestionCard({item, idx, chosen, onChoose}){
  const audioId = item.id.replace(/-Q\d+/, '')
  const hasAudio = item.audio_hint
  return <div style={{border:'1px solid #e2e8f0', borderRadius:12, padding:16, background:'#fff', marginBottom:12}}>
    <div style={{fontSize:12, color:'#64748b'}}>{item.skill} | {item.cefr} {hasAudio ? '| audio' : ''} | {item.id}</div>
    <div style={{fontWeight:600, margin:'8px 0'}}>{idx+1}. {item.question}</div>
    {item.passage ? <div style={{background:'#f1f5f9', padding:10, borderRadius:8, fontSize:13, whiteSpace:'pre-wrap', marginBottom:8}}>{item.passage}</div> : null}
    {hasAudio ? <audio controls src={`/api/listening/audio/${audioId}`} style={{width:'100%', marginBottom:8}} /> : null}
    {item.options ? item.options.map((o,i)=>
      <label key={i} style={{display:'flex', gap:10, padding:'8px 10px', borderRadius:8, background: chosen===i ? '#dbeafe' : '#f8fafc', border:'1px solid '+(chosen===i ? '#3b82f6' : '#e2e8f0'), marginBottom:6, cursor:'pointer'}}>
        <input type="radio" checked={chosen===i} onChange={()=>onChoose(item.id, item, i)} />
        <span>{o}</span>
      </label>
    ) : <div style={{color:'#64748b', fontSize:13}}>Jawaban terbuka</div>}
  </div>
}
