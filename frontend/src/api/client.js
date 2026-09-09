import axios from 'axios'
const api = axios.create({ baseURL: '/api', timeout: 20000 })
export const getHealth = () => api.get('/health').then(r=>r.data)
export const getMeta = () => api.get('/cefr/meta').then(r=>r.data)
export const getStage1 = (n=10) => api.get(`/placement/stage1?n=${n}`).then(r=>r.data)
export const postStage2 = (answers, exclude_ids, n=10) => api.post('/placement/stage2', {answers, exclude_ids, n}).then(r=>r.data)
export const getNext = (score,n=10) => api.get(`/placement/next?score=${score}&n=${n}`).then(r=>r.data)
export const postGrade = (payload) => api.post('/grade', payload).then(r=>r.data)
export const postChat = (message) => api.post('/chat', {message}).then(r=>r.data)
export const audioUrl = (id) => `/api/listening/audio/${id}`
export default api
