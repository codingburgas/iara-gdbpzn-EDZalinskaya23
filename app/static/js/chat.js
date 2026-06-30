// Live chat helper: poll a JSON endpoint and re-render the list so users see
// new messages without reloading. Endpoint returns { messages, seen_by }.

function startChatPolling(listId, url, intervalMs) {
    const el = document.getElementById(listId);
    if (!el) return;

    // Escape text before inserting as HTML to prevent injection
    function escapeHtml(s) {
        const div = document.createElement('div');
        div.textContent = (s === null || s === undefined) ? '' : s;
        return div.innerHTML;
    }

    // "Seen by" line under the last message
    function seenLine(names) {
        if (!names || !names.length) {
            return '<div class="seen-line">Изпратено</div>';
        }
        let text;
        if (names.length <= 3) {
            text = names.join(', ');
        } else {
            text = names.slice(0, 2).join(', ') + ' и още ' + (names.length - 2);
        }
        return '<div class="seen-line">Видяно от ' + escapeHtml(text) + '</div>';
    }

    function render(data) {
        const messages = data.messages || [];
        if (!messages.length) {
            el.innerHTML = '<p class="muted">Все още няма съобщения.</p>';
            return;
        }
        // Auto-scroll to the newest message only if the user is already near the bottom
        const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
        el.innerHTML = messages.map(function (m) {
            return '<div class="chat-msg">' +
                   '<span class="who">' + escapeHtml(m.author) + '</span>' +
                   '<span class="time">' + escapeHtml(m.created_at) + '</span>' +
                   '<div>' + escapeHtml(m.body) + '</div>' +
                   '</div>';
        }).join('') + seenLine(data.seen_by);
        if (atBottom) el.scrollTop = el.scrollHeight;
    }

    function load() {
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(render)
            .catch(function () { /* ignore transient network errors */ });
    }

    load();
    setInterval(load, intervalMs);
}
