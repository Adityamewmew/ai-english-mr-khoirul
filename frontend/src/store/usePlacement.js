import { create } from 'zustand'
const LS_KEY="placement_result"
const load=()=>{ try{ const s=localStorage.getItem(LS_KEY); return s?JSON.parse(s):null }catch{ return null } }
const save=(r)=>{ try{ localStorage.setItem(LS_KEY, JSON.stringify(r)) }catch{} }
const usePlacement = create((set, get)=>({
  stage: load()?.stage ?? 0,
  stage1: [], stage2: [],
  answers: {},
  estimate: null,
  writing: "", speaking: "",
  result: load()?.result || null,
  loading: false, error: null,
  set: (p)=>set(p),
  choose: (id, item, chosenIdx) => set(s=>{
    const correct = item.options ? item.options[chosenIdx]===item.answer : chosenIdx===0
    return {answers:{...s.answers, [id]:{cefr_tag:item.cefr, is_correct:correct, chosen:chosenIdx, id}}}
  }),
  persistResult: (result)=>{ save({result, stage:4}); set({result, stage:4}) },
  goDashboard: ()=>{ const r=get().result; if(r) save({result:r, stage:5}); set({stage:5}) },
  reset: ()=>{ localStorage.removeItem(LS_KEY); set({stage:0, stage1:[], stage2:[], answers:{}, estimate:null, writing:"", speaking:"", result:null, loading:false, error:null}) },
  softReset: ()=> set({stage:0, stage1:[], stage2:[], answers:{}, estimate:null, writing:"", speaking:""}),
  init: ()=>{ const d=load(); if(d?.result) set({result:d.result, stage:d.stage||5}) }
}))
export default usePlacement
