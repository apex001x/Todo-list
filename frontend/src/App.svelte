<script>
  import { onMount, onDestroy } from 'svelte'
  import * as api from './lib/api.js'

  let lists = []
  let newTitle = ''
  let loading = true
  let error = ''
  let mounted = false
  let deletingId = null
  let confirmModal = false
  let modalTarget = { id: null, title: '' }
  let now = new Date()
  let timer

$: total = lists ? lists.length : 0
$: completed = lists ? lists.filter(l => l.completed).length : 0
$: percent = total ? Math.round((completed / total) * 100) : 0

  async function load() {
    loading = true
    error = ''
    try {
      lists = await api.getLists()
    } catch (e) {
      error = `로드 실패: ${e.message}`
    } finally {
      loading = false
    }
  }

  async function addList(e) {
    e.preventDefault()
    if (!newTitle.trim()) return
    try {
      const created = await api.createList(newTitle.trim())
      lists = [created, ...lists]
      newTitle = ''
      error = ''
    } catch (e) {
      error = `추가 실패: ${e.message}`
    }
  }

  async function remove(id) {
    // actual delete after confirmation
    deletingId = id
    try {
      await api.deleteList(id)
      lists = lists.filter((l) => l.id !== id)
      error = ''
    } catch (e) {
      error = `삭제 실패: ${e.message}`
    } finally {
      deletingId = null
      confirmModal = false
      modalTarget = { id: null, title: '' }
    }
  }

  function confirmDelete(id, title) {
    modalTarget = { id, title }
    confirmModal = true
  }

  function cancelDelete() {
    confirmModal = false
    modalTarget = { id: null, title: '' }
  }

  async function toggleComplete(item) {
    if (item.updating) return
    const newVal = !item.completed
    item.updating = true
    lists = lists.map(l => l.id === item.id ? item : l)
    try {
      const updated = await api.updateList(item.id, { title: item.title, completed: newVal })
      updated.updating = false
      lists = lists.map(l => l.id === item.id ? updated : l)
      error = ''
    } catch (e) {
      error = `업데이트 실패: ${e.message}`
      item.updating = false
      lists = lists.map(l => l.id === item.id ? item : l)
    }
  }

  onMount(async () => {
    await load()
    mounted = true
    now = new Date()
    timer = setInterval(() => (now = new Date()), 1000)
  })

  onDestroy(() => {
    if (timer) clearInterval(timer)
  })
</script>

<div id="app" class={mounted ? 'ready' : ''}>
  <header class="header fade-in">
    <div class="header-content">
      <div class="header-left">
        <h1>TODO Lists</h1>
        <p>당신의 목표를 정리하세요</p>
      </div>
      <div class="clock" aria-live="polite">
        <div class="date">{now.toLocaleDateString('ko-KR', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })}</div>
        <div class="time">{now.toLocaleTimeString('ko-KR')}</div>
      </div>
    </div>
  </header>
  <main class="container">
    <div class="stats-row fade-in">
      <div class="stats-card fixed-width">
        <div class="stats-text">전체 <strong>{total}</strong> · 완료 <strong>{completed}</strong></div>
        <div class="progress-track" aria-hidden="true">
          <div class="progress-fill" style="width: {percent}%"></div>
        </div>
      </div>
    </div>
    <form on:submit|preventDefault={addList} class="input-section fade-in wide fixed-width">
      <div class="input-wrapper">
        <input
          type="text"
          placeholder="새로운 할 일을 입력하세요..."
          bind:value={newTitle}
          aria-label="New list title"
          class="todo-input"
        />
        <button type="submit" class="btn-add">추가</button>
      </div>
    </form>

    {#if loading}
      <div class="loading-state fade-in">
        <div class="spinner"></div>
        <p>로딩 중...</p>
      </div>
    {:else}
      {#if error}
        <div class="error-message fade-in">{error}</div>
      {/if}

      {#if lists && lists.length > 0}
        <div class="lists-section fade-in fixed-width">
          <div class="section-header">
            <span class="count-badge">{lists.length}</span>
            <h2>할 일 목록</h2>
          </div>
          <ul class="lists-grid">
            {#each lists as item (item.id)}
              <li class="list-item slide-in" data-id={item.id}>
                <div class="item-left">
                  <button class="btn-complete" on:click={() => toggleComplete(item)} aria-pressed={item.completed} aria-label="Mark complete" disabled={item.updating}>
                    {#if item.updating}
                      <span class="spinner-small"></span>
                    {:else}
                      {#if item.completed}
                        ✓
                      {:else}
                        ✔
                      {/if}
                    {/if}
                  </button>
                  <div class="item-content">
                    <h3 class:done={item.completed}>{item.title}</h3>
                  </div>
                </div>
                <button
                  class="btn-delete {deletingId === item.id ? 'deleting' : ''}"
                  on:click={() => confirmDelete(item.id, item.title)}
                  disabled={deletingId === item.id}
                  aria-label="Delete list"
                >
                  {#if deletingId === item.id}
                    <span class="spinner-small"></span>
                  {:else}
                    ✕
                  {/if}
                </button>
              </li>
            {/each}
          </ul>
        </div>
      {:else}
        <div class="empty-state fade-in">
          <div class="empty-icon">📝</div>
          <h2>아직 리스트가 없어요</h2>
          <p>위에 새로운 리스트를 추가해보세요</p>
        </div>
      {/if}
    {/if}
  </main>
    {#if confirmModal}
      <div class="modal-overlay" role="dialog" aria-modal="true">
        <div class="modal">
          <p>정말 할 일 '{modalTarget.title}'을 지울까요?</p>
          <div class="modal-actions">
            <button class="btn-cancel" on:click={cancelDelete}>취소</button>
            <button class="btn-confirm" on:click={() => remove(modalTarget.id)} disabled={deletingId === modalTarget.id}>
              {#if deletingId === modalTarget.id}
                <span class="spinner-small"></span>
              {:else}
                삭제
              {/if}
            </button>
          </div>
        </div>
      </div>
    {/if}
</div>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }

  #app {
    min-height: 100vh;
    background: rgb(36, 36, 36);
  }

  .header {
    background: linear-gradient(135deg, var(--primary-1) 0%, var(--primary-2) 100%);
    color: white;
    padding: 1.1rem 1.5rem;
    box-shadow: 0 10px 30px rgba(2,6,23,0.5);
  }

  .header-content {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .header-left h1 {
    margin: 0 0 0.25rem 0;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .header-left p {
    margin: 0;
    font-size: 0.95rem;
    opacity: 0.9;
    font-weight: 400;
  }

  .container {
    max-width: 900px;
    margin: -1.25rem auto 0;
    padding: 0 1.5rem 3rem;
    position: relative;
    z-index: 1;
    min-height: calc(100vh - 72px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }

  .input-section {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(2,6,23,0.6);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.03);
  }

  .input-section.wide { width: 100%; max-width: 820px }

  .input-wrapper {
    display: flex;
    gap: 0.75rem;
  }

  .todo-input {
    flex: 1;
    padding: 0.85rem 1rem;
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 10px;
    font-size: 1rem;
    font-family: inherit;
    transition: all 0.15s ease;
    background: rgba(255,255,255,0.02);
    color: var(--text);
  }

  .todo-input:focus {
    outline: none;
    border-color: rgba(59,130,246,0.9);
    background: rgba(255,255,255,0.03);
    box-shadow: 0 0 0 4px rgba(59,130,246,0.06);
  }

  .todo-input::placeholder { color: var(--muted) }

  .btn-add {
    padding: 0.85rem 1.5rem;
    background: linear-gradient(135deg, var(--primary-1) 0%, var(--primary-2) 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
    box-shadow: 0 6px 18px rgba(37,99,235,0.18);
  }

  .btn-add:hover { transform: translateY(-2px); box-shadow: 0 10px 26px rgba(37,99,235,0.22) }

  .btn-add:active { transform: translateY(0) }

  .lists-section {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(2,6,23,0.5);
    border: 1px solid rgba(255,255,255,0.03);
  }

  .stats-row { width: 100%; display:flex; justify-content:center }
  .stats-card {
    width: 100%; max-width: 820px; background: rgba(255,255,255,0.02); padding: 0.6rem 0.75rem; border-radius: 10px; border:1px solid rgba(255,255,255,0.03);
  }
  .stats-text { color: var(--muted); font-size: 0.95rem }
  .progress-track { height: 6px; background: rgba(255,255,255,0.03); border-radius: 6px; margin-top: 0.5rem; overflow:hidden }
  .progress-fill { height: 100%; background: linear-gradient(90deg, rgba(29, 189, 32, 0.9), rgba(36, 219, 57, 0.9)); width: 0%; transition: width 0.5s ease }

  .section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.05rem;
    color: var(--text);
  }

  .count-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, var(--primary-1) 0%, var(--primary-2) 100%);
    color: white;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .lists-grid {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 0.75rem;
  }

  .list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.03);
    border-radius: 10px;
    transition: all 0.12s ease;
  }

  .list-item:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(2,6,23,0.6) }

  .item-content h3 {
    margin: 0;
    font-size: 1rem;
    color: var(--text);
    font-weight: 500;
  }

  .btn-delete {
    width: 36px;
    height: 36px;
    border: none;
    background: rgba(239,68,68,0.08);
    color: #ffb4b4;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.12s ease;
    flex-shrink: 0;
  }

  .btn-delete:hover:not(:disabled) { transform: scale(1.05); background: rgba(239,68,68,0.12) }

  .btn-delete:disabled { opacity: 0.6; cursor: not-allowed }

  .btn-delete.deleting { background: rgba(59,130,246,0.08); color: #60a5fa }

  .spinner-small {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(2, 132, 199, 0.3);
    border-top-color: #0284c7;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .loading-state,
  .empty-state {
    text-align: center;
    padding: 2.5rem 1.5rem;
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(2,6,23,0.5);
    border: 1px solid rgba(255,255,255,0.02);
  }

  .empty-icon { font-size: 2.5rem; margin-bottom: 1rem }

  .empty-state h2 { margin: 0 0 0.5rem; color: var(--text); font-size: 1.25rem }

  .empty-state p { margin: 0; color: var(--muted) }

  .spinner {
    display: inline-block;
    width: 36px;
    height: 36px;
    border: 4px solid rgba(255,255,255,0.06);
    border-top-color: var(--primary-2);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 1rem;
  }

  .loading-state p {
    margin: 0;
    color: #6b7280;
  }

  .error-message {
    background: rgba(239,68,68,0.08);
    color: #fecaca;
    padding: 0.85rem 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    border-left: 4px solid rgba(239,68,68,0.2);
  }

  /* Fade-in animations */
  .fade-in {
    opacity: 0;
    animation: fadeIn 0.6s ease-out forwards;
  }

  .fade-in:nth-child(1) {
    animation-delay: 0s;
  }

  .fade-in:nth-child(2) {
    animation-delay: 0.1s;
  }

  .fade-in:nth-child(3) {
    animation-delay: 0.2s;
  }

  .slide-in {
    opacity: 0;
    animation: slideInUp 0.5s ease-out forwards;
  }

  .lists-grid .slide-in:nth-child(1) {
    animation-delay: 0.1s;
  }

  .lists-grid .slide-in:nth-child(2) {
    animation-delay: 0.15s;
  }

  .lists-grid .slide-in:nth-child(3) {
    animation-delay: 0.2s;
  }

  .lists-grid .slide-in:nth-child(n+4) {
    animation-delay: calc(0.2s + (var(--index, 0) * 0.05s));
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(12px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Clock */
  .clock {
    text-align: right;
    color: var(--text);
    background: var(--glass);
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.03);
    min-width: 140px;
  }

  .clock .date { font-size: 0.78rem; color: var(--muted) }
  .clock .time { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace; font-size: 1rem; margin-top: 3px }

  /* Fixed width for three sections (75% of viewport) */
  .fixed-width { width: 75vw; max-width: none }

  .item-left { display: flex; align-items: center; gap: 0.75rem }

  .btn-complete {
    width: 36px;
    height: 36px;
    border: none;
    background: rgba(34,197,94,0.12);
    color: #4ade80;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.12s ease, background 0.12s ease;
    flex-shrink: 0;
  }

  .btn-complete:hover { transform: scale(1.04); background: rgba(34,197,94,0.16) }
  .btn-complete[aria-pressed="true"] { background: rgba(34,197,94,0.22); color: white }

  .item-content h3.done { text-decoration: line-through; opacity: 0.65; color: var(--muted) }

  /* Modal */
  .modal-overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,0.5);
    z-index: 60;
  }

  .modal {
    background: var(--card-bg);
    padding: 1.25rem;
    border-radius: 12px;
    box-shadow: 0 12px 40px rgba(2,6,23,0.7);
    border: 1px solid rgba(255,255,255,0.04);
    max-width: 460px;
    width: 90%;
    text-align: center;
  }

  .modal p { margin: 0 0 1rem; color: var(--text) }

  .modal-actions { display:flex; gap: 0.75rem; justify-content: center }

  .btn-cancel, .btn-confirm {
    padding: 0.6rem 0.9rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-weight: 600;
  }

  .btn-cancel { background: rgba(255,255,255,0.04); color: var(--text) }
  .btn-confirm { background: rgba(239,68,68,0.12); color: #fecaca }

</style>
