const BASE = import.meta.env.VITE_API_URL;

async function request(path, options = {}) {
  // BASE 주소 끝에 /가 있다면 제거하여 중복 슬래시(//)를 방지합니다.
  const baseUrl = BASE.endsWith('/') ? BASE.slice(0, -1) : BASE;

  const res = await fetch(`${baseUrl}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }

  return res.json()
}

export async function getLists() {
  return request('/lists')
}

export async function createList(title) {
  return request('/lists', { method: 'POST', body: JSON.stringify({ title }) })
}

export async function deleteList(id) {
  return request(`/lists/${id}`, { method: 'DELETE' })
}

export async function updateList(id, body) {
  return request(`/lists/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export default { getLists, createList, deleteList, updateList }
