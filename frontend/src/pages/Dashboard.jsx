import usePlacement from '../store/usePlacement'
const GROUP = {
  A1:{group:'A', label:'Basic — Beginner', color:'#0ea5e9', next:'A2', desc:'Fokus kosakata harian, perkenalan diri, kalimat sederhana lambat & jelas.'},
  A2:{group:'A', label:'Basic — Elementary', color:'#38bdf8', next:'B1', desc:'Kalimat sehari-hari: keluarga, belanja, lingkungan. Announcement & menu.'},
  B1:{group:'B', label:'Independent — Intermediate', color:'#22c55e', next:'B2', desc:'Komunikasi mandiri: liburan, kerja, teks sederhana, opini & alasan.'},
  B2:{group:'B', label:'Independent — Upper-Intermediate', color:'#16a34a', next:'C1', desc:'Lancar diskusi berat/teknis, native tanpa kaku, artikel & laporan.'},
  C1:{group:'C', label:'Proficient — Advanced', color:'#8b5cf6', next:'C2', desc:'Teks panjang rumit, spontan tanpa berpikir, akademis/profesional fleksibel.'},
  C2:{group:'C', label:'Proficient — Mastery', color:'#6d28d9', next:null, desc:'Setara native: memahami hampir semua dengar/baca dengan mudah.'},
}
const PATHS = {
  A: [{title:'Starter: Kenalan & Daily', items:['Greetings & self-intro','Numbers, time, prices','Direction & shopping'], cta:'Mulai Modul A1-1'},{title:'Basic Listening & Reading', items:['Slow dialog hotel/cafe','Notices & menus','Family & town'], cta:'Lanjut Audio A2'}],
  B: [{title:'Independent Path', items:['Travel & culture','Work & opinion essays','News & reports'], cta:'Mulai Modul B1-1'},{title:'Fluency Builder', items:['Debate & discussion','Podcast & lectures','Writing reports'], cta:'Lanjut B2 Lab'}],
  C: [{title:'Proficient Mastery', items:['Academic papers','Panel & ethics','Idiomatic & nuance'], cta:'Mulai Modul C1-1'},{title:'Mastery Challenge', items:['Unstructured speech','Abstract texts','Native-level tasks'], cta:'Challenge C2'}],
}
export default function Dashboard(){
  const { result, set, reset } = usePlacement()
  if(!result){
    return <div style={{maxWidth:760, margin:'24px auto', padding:'0 16px', textAlign:'center'}}>
      <h2>Belum ada grade</h2>
      <p style={{color:'#64748b'}}>Selesaikan placement test dulu untuk menentukan kelas.</p>
      <button onClick={()=>set({stage:0})} style={{padding:'12px 20px', borderRadius:10, background:'#1e3a8a', color:'#fff', border:0, fontWeight:700}}>Mulai Tes →</button>
    </div>
  }
  const g=GROUP[result.overall_cefr]||GROUP.B1
  const paths=PATHS[g.group]
  const weakest = Object.entries(result.skills||{}).sort((a,b)=>a[1].score_0_100-b[1].score_0_100)[0]
  return <div style={{maxWidth:900, margin:'16px auto', padding:'0 16px'}}>
    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12}}>
      <div>
        <div style={{fontSize:12, color:'#64748b', textTransform:'uppercase', letterSpacing:.5}}>Dashboard Kelas</div>
        <div style={{fontSize:22, fontWeight:800}}><span style={{background:g.color, color:'#fff', padding:'4px 10px', borderRadius:20, fontSize:14, marginRight:8}}>{result.overall_cefr}</span>{g.label}</div>
      </div>
      <button onClick={()=>set({stage:4})} style={{fontSize:12, background:'#f1f5f9', border:'1px solid #e2e8f0', borderRadius:8, padding:'8px 12px'}}>Lihat Hasil Tes</button>
    </div>

    <div style={{display:'grid', gridTemplateColumns:'1fr 340px', gap:12}}>
      <div>
        <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16}}>
          <h3 style={{margin:'0 0 8px'}}>Kelas Kamu: Grade {g.group} → {result.overall_cefr}</h3>
          <p style={{margin:'0 0 10px', color:'#475569', fontSize:14}}>{g.desc}</p>
          <div style={{background:'#f8fafc', border:'1px solid #e2e8f0', borderRadius:10, padding:10, fontSize:13}}>
            <div><b>Skor</b>: {result.overall_score}/100 — IELTS {result.equivalent?.ielts} — TOEFL {result.equivalent?.toefl_1_6}</div>
            {weakest && <div style={{marginTop:6, color:'#b45309'}}>Fokus dulu: <b>{weakest[0].toUpperCase()}</b> ({weakest[1].cefr} {weakest[1].score_0_100}/100) — materi akan adaptif ke sini.</div>}
            {result.uneven_profile && <div style={{marginTop:6, fontSize:12, color:'#92400e'}}>Profil tidak merata — dashboard prioritaskan skill terlemah.</div>}
          </div>
          <div style={{display:'flex', gap:8, marginTop:12, flexWrap:'wrap'}}>
            {paths.map((p,i)=><div key={i} style={{flex:'1 1 260px', background:'#f8fafc', border:'1px solid #e2e8f0', borderRadius:10, padding:12}}>
              <div style={{fontWeight:700}}>{p.title}</div>
              <ul style={{margin:'8px 0 10px 18px', color:'#475569', fontSize:13}}>{p.items.map(x=><li key={x}>{x}</li>)}</ul>
              <button style={{width:'100%', padding:'10px', borderRadius:8, background:'#1e3a8a', color:'#fff', border:0, fontWeight:700}} onClick={()=>alert('Mulai: '+p.cta+' — hubungkan ke LMS modul')}>{p.cta} →</button>
            </div>)}
          </div>
        </div>

        <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginTop:12}}>
          <h3 style={{margin:0}}>Progress Kelas {result.overall_cefr}</h3>
          <div style={{display:'flex', gap:8, marginTop:10}}>
            {['Listening','Reading','Speaking','Writing'].map(s=>{
              const v=result.skills?.[s.toLowerCase()]; const pct=v?Math.min(100, v.score_0_100):0
              return <div key={s} style={{flex:1, textAlign:'center'}}>
                <div style={{fontSize:11, color:'#64748b'}}>{s}</div>
                <div style={{height:8, background:'#e2e8f0', borderRadius:10, margin:'6px 0', overflow:'hidden'}}><div style={{width:pct+'%', height:'100%', background:g.color}} /></div>
                <div style={{fontSize:11}}>{v? `${v.cefr} ${pct}%` : '—'}</div>
              </div>
            })}
          </div>
          <div style={{marginTop:10, fontSize:12, color:'#64748b'}}>Materi adaptif berdasarkan Can-Do CEFR Companion 2020. Naik level otomatis saat skor rerata &gt; batas.</div>
        </div>
      </div>

      <div>
        <div style={{background:g.color, color:'#fff', borderRadius:12, padding:16}}>
          <div style={{fontWeight:800}}>Apa Selanjutnya?</div>
          <ol style={{margin:'8px 0 0 18px', fontSize:13, lineHeight:1.6}}>
            <li>Mulai modul pertama di kiri</li>
            <li>Selesaikan 3 latihan → unlock next</li>
            <li>Level up: {result.overall_cefr} → {g.next||'Mastery Complete 🎉'}</li>
          </ol>
        </div>
        <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:12, marginTop:12}}>
          <div style={{fontWeight:700, marginBottom:6}}>Aksi</div>
          <button style={{width:'100%', padding:'10px', borderRadius:8, background:'#f1f5f9', border:'1px solid #e2e8f0', marginBottom:6}} onClick={()=>alert('Chat tutor — hubungkan ke /chat API')}>💬 Chat Tutor</button>
          <button style={{width:'100%', padding:'10px', borderRadius:8, background:'#f1f5f9', border:'1px solid #e2e8f0'}} onClick={()=>alert('Simpan progress — integrasi DB nanti')}>⬇️ Unduh Sertifikat Level</button>
          <div style={{marginTop:10, fontSize:11, color:'#94a3b8', textAlign:'center'}}>
            Tes sudah selesai — tidak perlu ulang. Jika ingin retake, hubungi pengajar.
            <div><button onClick={()=>{ if(confirm('Retake akan hapus progress kelas. Lanjut?')) reset() }} style={{marginTop:6, background:'none', border:0, color:'#94a3b8', textDecoration:'underline', fontSize:11}}>Retake (admin only)</button></div>
          </div>
        </div>
      </div>
    </div>
  </div>
}
