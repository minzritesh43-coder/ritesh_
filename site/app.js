(() => {
  'use strict';

  const notes = window.COMMONPLACE_NOTES || [];
  const subjects = {
    mathematics: { label: 'Mathematics', className: 'maths', icon: '<path d="M6 5h12M6 19h12M9 5l6 14M15 5 9 19" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' },
    physics: { label: 'Physics', className: 'physics', icon: '<circle cx="12" cy="12" r="1.5" fill="currentColor"/><ellipse cx="12" cy="12" rx="9" ry="4" stroke="currentColor" stroke-width="1.3"/><ellipse cx="12" cy="12" rx="9" ry="4" transform="rotate(60 12 12)" stroke="currentColor" stroke-width="1.3"/><ellipse cx="12" cy="12" rx="9" ry="4" transform="rotate(120 12 12)" stroke="currentColor" stroke-width="1.3"/>' },
    chemistry: { label: 'Chemistry', className: 'chemistry', icon: '<path d="M9 3h6M10 3v6l-5.5 9.2A1.8 1.8 0 0 0 6 21h12a1.8 1.8 0 0 0 1.5-2.8L14 9V3M8 14h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="11" cy="17" r=".8" fill="currentColor"/><circle cx="15" cy="18" r=".8" fill="currentColor"/>' },
    'computer-science': { label: 'Computer Science', className: 'computer', icon: '<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-13-2 16" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' }
  };
  const bookmarkIcon = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 4h12v17l-6-4-6 4V4Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  const clockIcon = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"/><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
  const storageKey = 'commonplace-bookmarks-v1';
  const grid = document.getElementById('notes-grid');
  const search = document.getElementById('note-search');
  const resultsCount = document.getElementById('results-count');
  const savedToggle = document.getElementById('saved-toggle');
  const savedCount = document.getElementById('saved-count');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const emptyState = document.getElementById('empty-state');
  const dialog = document.getElementById('note-dialog');
  const dialogBookmark = document.getElementById('dialog-bookmark');
  const closeButton = document.getElementById('close-dialog');
  const toast = document.getElementById('toast');
  const menuToggle = document.querySelector('.menu-toggle');
  const navigation = document.getElementById('primary-nav');
  const dialogStatus = document.createElement('p');
  dialogStatus.className = 'dialog-toast';
  dialogStatus.setAttribute('role', 'status');
  dialogStatus.setAttribute('aria-live', 'polite');
  dialog.querySelector('.dialog-content').append(dialogStatus);

  const state = { subject: 'all', query: '', savedOnly: false };
  let storageAvailable = true;
  let saved = new Set(readBookmarks());
  let activeNoteId = null;
  let lastNoteTrigger = null;
  let toastTimer;
  const originalTitle = document.title;
  const searchText = new Map(notes.map(note => [note.id, [
    note.title, note.summary, subjects[note.subject].label, note.level,
    ...note.sections.flatMap(section => [
      ...(section.paragraphs || []), ...(section.list || []),
      section.heading || '', section.formula || '', section.tip || ''
    ])
  ].join(' ').toLocaleLowerCase()]));

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[character]);
  }

  function readBookmarks() {
    try {
      const value = JSON.parse(localStorage.getItem(storageKey) || '[]');
      return Array.isArray(value) ? value.filter(id => notes.some(note => note.id === id)) : [];
    } catch {
      storageAvailable = false;
      return [];
    }
  }

  function persistBookmarks() {
    try {
      localStorage.setItem(storageKey, JSON.stringify([...saved]));
      storageAvailable = true;
      return true;
    } catch {
      storageAvailable = false;
      return false;
    }
  }

  function showToast(message) {
    clearTimeout(toastTimer);
    if (dialog.open) {
      dialogStatus.textContent = message;
      toastTimer = setTimeout(() => { dialogStatus.textContent = ''; }, 3200);
    } else {
      toast.textContent = message;
      toast.classList.add('visible');
      toastTimer = setTimeout(() => { toast.classList.remove('visible'); }, 2800);
    }
  }

  function updateBookmarkButtons() {
    savedCount.textContent = String(saved.size);
    document.querySelectorAll('[data-bookmark]').forEach(button => {
      const id = button.dataset.bookmark;
      const note = notes.find(item => item.id === id);
      if (!note) return;
      const isSaved = saved.has(id);
      const label = isSaved ? `Remove “${note.title}” from saved notes` : `Save “${note.title}”`;
      button.setAttribute('aria-pressed', String(isSaved));
      button.setAttribute('aria-label', label);
      button.title = label;
    });
  }

  function toggleBookmark(id) {
    if (!notes.some(note => note.id === id)) return;
    const wasSaved = saved.has(id);
    if (wasSaved) saved.delete(id); else saved.add(id);
    const persisted = persistBookmarks();
    if (state.savedOnly) {
      renderNotes();
      if (!dialog.open) savedToggle.focus({ preventScroll: true });
    }
    updateBookmarkButtons();
    showToast(wasSaved ? 'Note removed from your saved pages.' : storageAvailable ? 'A good page, kept. Note saved in this browser.' : 'Saved for this visit. Browser storage is unavailable.');
  }

  function cardHTML(note, index) {
    const subject = subjects[note.subject];
    return `<article class="note-card ${subject.className}" style="animation-delay:${Math.min(index * 35, 175)}ms">
      <div class="card-top"><span class="subject-icon"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true">${subject.icon}</svg></span><button class="bookmark-button" type="button" data-bookmark="${note.id}" aria-label="Save note" aria-pressed="false">${bookmarkIcon}</button></div>
      <div class="card-meta"><span class="subject-label">${subject.label}</span><span class="meta-dot" aria-hidden="true"></span><span class="class-level">${escapeHTML(note.level)}</span></div>
      <h3><a class="note-link" href="#note/${note.id}">${escapeHTML(note.title)}</a></h3>
      <p class="card-summary">${escapeHTML(note.summary)}</p>
      <div class="card-footer"><span class="read-time">${clockIcon}${note.minutes} min read</span><a class="read-link" href="#note/${note.id}" aria-label="Read ${escapeHTML(note.title)}">Read note <span aria-hidden="true">→</span></a></div>
    </article>`;
  }

  function renderNotes() {
    const query = state.query.trim().toLocaleLowerCase();
    const visible = notes.filter(note =>
      (state.subject === 'all' || note.subject === state.subject) &&
      (!state.savedOnly || saved.has(note.id)) &&
      (!query || searchText.get(note.id).includes(query))
    );
    grid.innerHTML = visible.map(cardHTML).join('');
    grid.hidden = visible.length === 0;
    emptyState.hidden = visible.length !== 0 || notes.length === 0;
    resultsCount.textContent = `${visible.length} ${visible.length === 1 ? 'note' : 'notes'} ${state.savedOnly ? 'saved' : 'to explore'}`;
    const noSavedNotes = state.savedOnly && saved.size === 0;
    document.getElementById('empty-title').textContent = noSavedNotes ? 'Keep a little clarity for later.' : 'No notes on that page yet.';
    document.getElementById('empty-description').textContent = noSavedNotes ? 'Tap the bookmark on any note to keep it here in this browser.' : 'Try another word or explore a different subject.';
    filterButtons.forEach(button => {
      const active = button.dataset.filter === state.subject;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    savedToggle.setAttribute('aria-pressed', String(state.savedOnly));
    updateBookmarkButtons();
  }

  function resetFilters() {
    state.subject = 'all';
    state.query = '';
    state.savedOnly = false;
    search.value = '';
    renderNotes();
  }

  function sectionHTML(section) {
    return `<section>${section.heading ? `<h3>${escapeHTML(section.heading)}</h3>` : ''}
      ${(section.paragraphs || []).map(text => `<p>${escapeHTML(text)}</p>`).join('')}
      ${section.formula ? `<div class="note-formula">${escapeHTML(section.formula)}</div>` : ''}
      ${section.list ? `<ul>${section.list.map(item => `<li>${escapeHTML(item)}</li>`).join('')}</ul>` : ''}
      ${section.tip ? `<p class="note-tip"><strong>Try this. </strong>${escapeHTML(section.tip)}</p>` : ''}
    </section>`;
  }

  function noteIdFromHash() {
    const match = location.hash.match(/^#note\/([a-z0-9-]+)$/);
    return match && notes.some(note => note.id === match[1]) ? match[1] : null;
  }

  function openNote(id) {
    const note = notes.find(item => item.id === id);
    if (!note) return;
    activeNoteId = id;
    const subject = subjects[note.subject];
    document.getElementById('dialog-title').textContent = note.title;
    document.getElementById('dialog-summary').textContent = note.summary;
    document.getElementById('dialog-subject').textContent = subject.label;
    document.getElementById('dialog-read-time').textContent = `${note.minutes} min read · ${note.level}`;
    document.getElementById('dialog-body').innerHTML = note.sections.map(sectionHTML).join('');
    dialogBookmark.dataset.bookmark = id;
    dialogBookmark.innerHTML = bookmarkIcon;
    dialogStatus.textContent = '';
    updateBookmarkButtons();
    document.title = `${note.title} — Commonplace`;
    if (!dialog.open) dialog.showModal();
    document.body.classList.add('modal-open');
    dialog.scrollTop = 0;
    closeButton.focus({ preventScroll: true });
  }

  function syncNoteWithLocation() {
    const id = noteIdFromHash();
    if (id) openNote(id);
    else if (dialog.open) dialog.close();
  }

  function navigateToNote(id, trigger) {
    closeMenu();
    lastNoteTrigger = trigger || document.activeElement;
    if (location.hash === `#note/${id}`) openNote(id);
    else location.hash = `note/${id}`;
  }

  function closeMenu() {
    navigation.dataset.open = 'false';
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Open navigation');
  }

  filterButtons.forEach(button => button.addEventListener('click', () => {
    state.subject = button.dataset.filter;
    renderNotes();
  }));
  search.addEventListener('input', () => { state.query = search.value; renderNotes(); });
  savedToggle.addEventListener('click', () => { state.savedOnly = !state.savedOnly; renderNotes(); });
  document.getElementById('reset-filters').addEventListener('click', () => { resetFilters(); search.focus(); });
  grid.addEventListener('click', event => {
    const bookmark = event.target.closest('[data-bookmark]');
    if (bookmark) { toggleBookmark(bookmark.dataset.bookmark); return; }
    const link = event.target.closest('a.note-link, a.read-link');
    if (link) lastNoteTrigger = link;
  });
  dialogBookmark.addEventListener('click', () => { if (activeNoteId) toggleBookmark(activeNoteId); });
  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('modal-open');
    document.title = originalTitle;
    activeNoteId = null;
    dialogStatus.textContent = '';
    if (location.hash.startsWith('#note/')) {
      try { history.replaceState(null, '', `${location.pathname}${location.search}#notes`); }
      catch { location.hash = 'notes'; }
    }
    if (lastNoteTrigger && lastNoteTrigger.isConnected) lastNoteTrigger.focus({ preventScroll: true });
    else document.getElementById('notes-title').focus({ preventScroll: true });
    lastNoteTrigger = null;
  });
  window.addEventListener('hashchange', syncNoteWithLocation);
  document.getElementById('random-note').addEventListener('click', event => {
    if (notes.length) navigateToNote(notes[Math.floor(Math.random() * notes.length)].id, event.currentTarget);
  });
  menuToggle.addEventListener('click', () => {
    const open = menuToggle.getAttribute('aria-expanded') !== 'true';
    navigation.dataset.open = String(open);
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('click', event => { if (!event.target.closest('.site-header')) closeMenu(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menuToggle.focus();
    }
  });
  window.matchMedia('(max-width: 620px)').addEventListener('change', closeMenu);
  window.addEventListener('storage', event => {
    if (event.key === storageKey || event.key === null) {
      saved = new Set(readBookmarks());
      renderNotes();
    }
  });

  renderNotes();
  syncNoteWithLocation();
})();
