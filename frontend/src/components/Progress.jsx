export default function Progress({stage}){
  const steps=["Welcome","Stage 1","Stage 2","Writing & Speaking","Result"]
  return <div style={{display:'flex',gap:8, flexWrap:'wrap', marginBottom:16}}>
    {steps.map((s,i)=><div key={i} style={{padding:'6px 12px', borderRadius:20, background: stage>=i ? '#1e3a8a' : '#e2e8f0', color: stage>=i ? '#fff' : '#475569', fontSize:13}}>{i===stage ? '● ':''}{s}</div>)}
  </div>
}
