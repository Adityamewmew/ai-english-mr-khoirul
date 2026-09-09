import { create } from 'zustand'
const usePlacement = create((set, get)=>({
  stage: 0, // 0 welcome, 1 stage1, 2 stage2, 3 input longform, 4 result
  stage1: [], stage2: [],
  answers: {}, // id -> {cefr_tag, is_correct, chosen}
  estimate: null,
  writing: "", speaking: "",
  result: null, loading: false, error: null,
  set: (p)=>set(p),
  choose: (id, item, chosenIdx) => set(s=>{
    const correct = item.options ? item.options[chosenIdx]===item.answer : chosenIdx===0
    // store by original id, keep cefr_tag for grading
    return {answers:{...s.answers, [id]:{cefr_tag:item.cefr, is_correct:correct, chosen:chosenIdx, id}}}
  }),
  reset: ()=>set({stage:0, stage1:[], stage2:[], answers:{}, estimate:null, writing:"", speaking:"", result:null, loading:false, error:null})
}))
export default usePlacement
