from __future__ import annotations

import json


def _base_shell(title: str, body: str, *, app_shell: bool = False) -> str:
    nav = """
    <div class="nav">
      <div class="brand-wrap">
        <div class="brand">Personal AI Phone</div>
        <div class="tagline">A calmer assistant for everyday life</div>
      </div>
      <div class="nav-links">
        <a href="/">Home</a>
        <a href="/app">My AI</a>
        <a href="/download">Install</a>
      </div>
    </div>
    """
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="theme-color" content="#102026">
  <link rel="manifest" href="/manifest.webmanifest">
  <style>
    :root {{
      --bg: #102026;
      --bg-soft: #17303a;
      --panel: #1a313a;
      --panel-2: #23414c;
      --text: #f5fbfd;
      --muted: #c4d4da;
      --accent: #8de6bb;
      --accent-2: #7ebdff;
      --warning: #ffd576;
      --danger: #ff9d91;
      --border: rgba(255,255,255,0.1);
      --shadow: 0 22px 60px rgba(0,0,0,0.26);
    }}
    * {{ box-sizing: border-box; }}
    html {{ font-size: 20px; }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", Helvetica, Arial, sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top, rgba(126,189,255,0.17), transparent 32%),
        radial-gradient(circle at 82% 10%, rgba(141,230,187,0.14), transparent 22%),
        linear-gradient(180deg, #0f1c21, #13262d 45%, #102026 100%);
    }}
    a {{ color: inherit; text-decoration: none; }}
    .page {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 18px;
      display: grid;
      gap: 18px;
    }}
    .nav {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      padding: 6px 2px 12px;
    }}
    .brand-wrap {{
      display: grid;
      gap: 4px;
    }}
    .brand {{
      font-size: 1.18rem;
      font-weight: 900;
      letter-spacing: 0.01em;
    }}
    .tagline {{
      font-size: 0.92rem;
      color: var(--muted);
    }}
    .nav-links {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      color: var(--muted);
    }}
    .nav-links a {{
      padding: 12px 16px;
      border-radius: 999px;
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
    }}
    .hero, .panel, .card {{
      border-radius: 28px;
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
      box-shadow: var(--shadow);
    }}
    .hero {{
      padding: 32px;
      display: grid;
      gap: 18px;
    }}
    .panel, .card {{
      padding: 22px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.4rem, 6vw, 4.4rem);
      line-height: 1;
      max-width: 11ch;
    }}
    h2 {{
      margin: 0;
      font-size: 1.5rem;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 1.1rem;
    }}
    p, li {{
      line-height: 1.65;
      color: var(--muted);
    }}
    .badge-row, .chip-row, .cta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .badge, .chip {{
      border-radius: 999px;
      padding: 12px 16px;
      font-size: 0.96rem;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.05);
    }}
    .badge strong {{ color: var(--accent); }}
    .layout-2 {{
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 18px;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }}
    .stack {{
      display: grid;
      gap: 14px;
    }}
    .mini-stack {{
      display: grid;
      gap: 10px;
    }}
    .form {{
      display: grid;
      gap: 14px;
    }}
    .row-2 {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    label {{
      display: grid;
      gap: 8px;
      font-weight: 800;
    }}
    button, .button, input, textarea, select {{
      font: inherit;
      border-radius: 20px;
    }}
    button, .button {{
      border: 0;
      min-height: 62px;
      padding: 16px 22px;
      cursor: pointer;
      font-weight: 900;
      color: #08161b;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }}
    .button.secondary, .secondary {{
      background: rgba(255,255,255,0.05);
      color: var(--text);
      border: 1px solid var(--border);
    }}
    .button.warning {{
      background: linear-gradient(135deg, var(--warning), #ffb86c);
      color: #231400;
    }}
    input, textarea, select {{
      width: 100%;
      min-height: 62px;
      border: 1px solid var(--border);
      background: rgba(0,0,0,0.25);
      color: var(--text);
      padding: 15px 16px;
      font-size: 1rem;
    }}
    textarea {{
      min-height: 150px;
      resize: vertical;
    }}
    .status {{
      min-height: 1.5rem;
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .success {{ color: var(--accent); font-weight: 800; }}
    .warning-text {{ color: var(--warning); font-weight: 800; }}
    .danger-text {{ color: var(--danger); font-weight: 800; }}
    .muted {{ color: var(--muted); }}
    .small {{ font-size: 0.93rem; }}
    .list {{
      display: grid;
      gap: 12px;
    }}
    .item {{
      padding: 16px;
      border-radius: 20px;
      background: var(--panel-2);
      border: 1px solid var(--border);
    }}
    .item strong {{
      display: inline-block;
      margin-bottom: 4px;
    }}
    .summary-box {{
      padding: 18px;
      border-radius: 22px;
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
    }}
    .big-stat {{
      font-size: 1.2rem;
      font-weight: 900;
      color: var(--text);
    }}
    .assistant-reply {{
      min-height: 150px;
      white-space: pre-wrap;
    }}
    .quick-actions {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .steps {{
      margin: 0;
      padding-left: 24px;
    }}
    .qr-box {{
      border: 2px dashed rgba(255,255,255,0.13);
      border-radius: 24px;
      padding: 20px;
      text-align: center;
      background: rgba(255,255,255,0.03);
    }}
    .install-link {{
      font-size: 1.05rem;
      font-weight: 800;
      word-break: break-word;
    }}
    .kicker {{
      color: var(--accent);
      font-weight: 900;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      font-size: 0.82rem;
    }}
    @media (max-width: 980px) {{
      html {{ font-size: 18px; }}
      .layout-2, .grid-2, .grid-3, .row-2, .quick-actions {{
        grid-template-columns: 1fr;
      }}
      h1 {{ max-width: none; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    {nav if app_shell else ''}
    {body}
  </main>
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('/sw.js').catch(() => {{}});
      }});
    }}
  </script>
</body>
</html>
"""


def render_landing_page() -> str:
    body = """
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>Web-first v1</strong> no App Store required</div>
        <div class="badge">Built for older and non-technical users</div>
        <div class="badge">Large text, big controls, fewer decisions</div>
      </div>
      <div class="kicker">A simpler way to use a phone</div>
      <h1>One gentle AI can replace the stress of app-hunting.</h1>
      <p>
        Personal AI Phone starts as a mobile-friendly web app that feels calm, clear, and helpful.
        It gives people one place to ask for help with calling family, remembering preferences,
        planning the day, understanding paperwork, and eventually letting trusted AI agents handle more work.
      </p>
      <div class="cta-row">
        <a class="button" href="#signup">Create an account</a>
        <a class="button secondary" href="/download">See install options</a>
      </div>
    </section>

    <section class="grid-3">
      <div class="card">
        <h3>Made for real people</h3>
        <p>Large elements, plain language, and guided confirmations make the product feel easier than a regular smartphone.</p>
      </div>
      <div class="card">
        <h3>Useful right away</h3>
        <p>Keep contacts, shared helpers, preferences, and assistant history in one account you can reuse later on phone hardware.</p>
      </div>
      <div class="card">
        <h3>Ready for what comes next</h3>
        <p>The architecture is built for future calendar flows, agent-to-agent scheduling, shopping help, and device handoff.</p>
      </div>
    </section>

    <section class="layout-2">
      <div class="panel" id="signup">
        <div class="kicker">Get started</div>
        <h2>Create your account</h2>
        <p class="small">Your account unlocks your dashboard, install page, trusted circle, and future phone app pairing.</p>
        <div class="form">
          <div class="row-2">
            <label>Display name
              <input id="register-display-name" placeholder="Pat" />
            </label>
            <label>Username
              <input id="register-username" placeholder="pat-helper" />
            </label>
          </div>
          <label>Email
            <input id="register-email" type="email" placeholder="you@example.com" />
          </label>
          <label>Password
            <input id="register-password" type="password" placeholder="At least 8 characters" />
          </label>
          <button onclick="registerUser()">Create account</button>
          <div id="register-status" class="status">Your account becomes the home for your profile, preferences, contacts, and future app installs.</div>
        </div>
      </div>

      <div class="panel">
        <div class="kicker">Welcome back</div>
        <h2>Sign in</h2>
        <div class="form">
          <label>Email or username
            <input id="login-identifier" placeholder="you@example.com or username" />
          </label>
          <label>Password
            <input id="login-password" type="password" placeholder="Password" />
          </label>
          <button onclick="loginUser()">Open my assistant</button>
          <div id="login-status" class="status">After signing in, you can open the dashboard and install the web app to your phone home screen.</div>
        </div>
      </div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <div class="kicker">How it helps</div>
        <h2>What the first version already supports</h2>
        <div class="list">
          <div class="item"><strong>Calls and contacts</strong><br><span class="muted">Save important people in one place so later the assistant can launch the right calling flow fast.</span></div>
          <div class="item"><strong>Personal memory</strong><br><span class="muted">Store habits, preferences, relationships, and life details so the AI becomes more personal over time.</span></div>
          <div class="item"><strong>Trusted circle</strong><br><span class="muted">Add caregivers or family members who can share context and eventually help coordinate tasks.</span></div>
          <div class="item"><strong>Install on phone</strong><br><span class="muted">Use it like an app from your home screen today while native phone integrations continue in parallel.</span></div>
        </div>
      </div>

      <div class="panel">
        <div class="kicker">What comes later</div>
        <h2>Why this is a bridge product</h2>
        <div class="list">
          <div class="item"><strong>Calendar help</strong><br><span class="muted">Schedule appointments with clear confirmations.</span></div>
          <div class="item"><strong>Agent-to-agent tasks</strong><br><span class="muted">Your assistant can eventually coordinate with other assistants about meetings, purchases, and bookings.</span></div>
          <div class="item"><strong>Native phone handoff</strong><br><span class="muted">The same account and profile will move into the deeper mobile app experience later.</span></div>
        </div>
      </div>
    </section>

    <script>
      async function registerUser() {
        const res = await fetch('/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            display_name: document.getElementById('register-display-name').value,
            username: document.getElementById('register-username').value,
            email: document.getElementById('register-email').value,
            password: document.getElementById('register-password').value
          })
        });
        const data = await res.json();
        const el = document.getElementById('register-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Registration failed.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Account created. Opening your assistant now...';
        el.className = 'status success';
        window.location.href = '/app';
      }

      async function loginUser() {
        const res = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            identifier: document.getElementById('login-identifier').value,
            password: document.getElementById('login-password').value
          })
        });
        const data = await res.json();
        const el = document.getElementById('login-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Login failed.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Signed in. Opening your assistant now...';
        el.className = 'status success';
        window.location.href = '/app';
      }
    </script>
    """
    return _base_shell("Personal AI Phone", body)


def render_app_page() -> str:
    body = """
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>My AI dashboard</strong></div>
        <div class="badge">Phone-friendly web app</div>
        <div class="badge">Older-user friendly design</div>
      </div>
      <div class="layout-2">
        <div class="stack">
          <div class="kicker">Welcome</div>
          <h1 id="welcome-name">Loading...</h1>
          <p id="welcome-copy">Preparing your assistant, profile, and daily briefing.</p>
          <div class="cta-row">
            <a class="button secondary" href="/download">Install on my phone</a>
            <button class="secondary" onclick="logoutUser()">Sign out</button>
          </div>
        </div>
        <div class="summary-box">
          <h3>Today at a glance</h3>
          <div class="big-stat" id="briefing-headline">Loading...</div>
          <p id="briefing-summary" class="muted">Loading...</p>
          <div id="briefing-suggestions" class="mini-stack muted"></div>
        </div>
      </div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <div class="kicker">Quick actions</div>
        <h2>Start with one tap</h2>
        <div class="quick-actions">
          <button onclick="fillPrompt('Call my daughter')">Call someone</button>
          <button onclick="fillPrompt('Schedule lunch next Tuesday')">Plan my day</button>
          <button onclick="fillPrompt('Remember that I prefer large text and short instructions')">Save a preference</button>
          <button class="secondary" onclick="window.location.href='/download'">Install on phone</button>
        </div>
      </div>
      <div class="panel">
        <div class="kicker">Accessibility</div>
        <h2>Simple by default</h2>
        <div class="list">
          <div class="item"><strong>Voice guidance</strong><br><span id="accessibility-summary" class="muted">Loading...</span></div>
          <div class="item"><strong>Saved preferences</strong><br><span id="preferences-summary" class="muted">Loading...</span></div>
          <div class="item"><strong>Trusted support</strong><br><span id="trusted-summary" class="muted">Loading...</span></div>
        </div>
      </div>
    </section>

    <section class="layout-2">
      <div class="panel">
        <div class="kicker">Assistant</div>
        <h2>Ask in plain language</h2>
        <div class="form">
          <label>Assistant mode
            <select id="assistant-mode">
              <option value="talk">Talk</option>
              <option value="call">Call</option>
              <option value="calendar">Calendar</option>
              <option value="camera">Camera</option>
              <option value="documents">Documents</option>
              <option value="memory">Memory</option>
            </select>
          </label>
          <label>What do you need?
            <textarea id="assistant-prompt" placeholder="For example: Call Alice, schedule lunch with Alex next Tuesday, or buy my usual vitamins."></textarea>
          </label>
          <button onclick="askAssistant()">Ask my assistant</button>
          <div class="summary-box">
            <h3>Assistant response</h3>
            <div id="assistant-reply" class="assistant-reply muted">Nothing yet.</div>
          </div>
        </div>
      </div>

      <div class="stack">
        <div class="panel">
          <div class="kicker">Profile</div>
          <h2>Your setup</h2>
          <div class="form">
            <label>Display name
              <input id="profile-display-name" />
            </label>
            <label>One important preference
              <input id="profile-preference" placeholder="I prefer simple instructions and larger text" />
            </label>
            <div class="row-2">
              <label>Voice guidance
                <select id="profile-voice-guidance">
                  <option value="true">On</option>
                  <option value="false">Off</option>
                </select>
              </label>
              <label>Text size
                <select id="profile-text-scale">
                  <option value="large">Large</option>
                  <option value="extra-large">Extra large</option>
                </select>
              </label>
            </div>
            <button onclick="saveProfile()">Save my profile</button>
            <div id="profile-status" class="status">Your account profile will also be reused later by the native phone app.</div>
          </div>
        </div>

        <div class="panel">
          <div class="kicker">Memory vault</div>
          <h2>Teach the assistant about you</h2>
          <div class="form">
            <label>Memory type
              <select id="memory-category">
                <option value="preferences">Preference</option>
                <option value="habits">Habit</option>
                <option value="relationships">Relationship</option>
                <option value="life_details">Life detail</option>
              </select>
            </label>
            <label>Short memory
              <input id="memory-summary" placeholder="My daughter usually calls in the evening" />
            </label>
            <label>Optional detail
              <input id="memory-detail" placeholder="Use this when suggesting the best time to call" />
            </label>
            <button onclick="addMemory()">Save memory</button>
            <div id="memory-status" class="status">Memories help the assistant become more personal over time.</div>
          </div>
        </div>
      </div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <div class="kicker">Contacts</div>
        <h2>Important people</h2>
        <div class="form">
          <div class="row-2">
            <label>Name
              <input id="contact-name" placeholder="Alice Example" />
            </label>
            <label>Phone
              <input id="contact-phone" placeholder="+1 555 123 0000" />
            </label>
          </div>
          <label>Notes
            <input id="contact-notes" placeholder="Daughter, prefers evenings" />
          </label>
          <label>Shared household contact?
            <select id="contact-shared">
              <option value="false">No</option>
              <option value="true">Yes</option>
            </select>
          </label>
          <button onclick="addContact()">Add contact</button>
          <div id="contact-status" class="status">Shared contacts are useful for a household, caregiver, or family setup.</div>
        </div>
        <div id="contacts-list" class="list muted" style="margin-top:16px;">Loading...</div>
      </div>

      <div class="panel">
        <div class="kicker">Trusted circle</div>
        <h2>Family and helpers</h2>
        <div class="form">
          <label>Name
            <input id="trusted-name" placeholder="Jamie Helper" />
          </label>
          <div class="row-2">
            <label>Email
              <input id="trusted-email" placeholder="jamie@example.com" />
            </label>
            <label>Role
              <input id="trusted-role" placeholder="Caregiver, daughter, neighbor" />
            </label>
          </div>
          <button onclick="addTrustedPerson()">Add trusted person</button>
          <div id="trusted-status" class="status">Trusted people are who the assistant can eventually coordinate with or share approved context with.</div>
        </div>
        <div id="trusted-list" class="list muted" style="margin-top:16px;">Loading...</div>
      </div>
    </section>

    <section class="grid-2">
      <div class="panel">
        <div class="kicker">Saved memory</div>
        <h2>What your assistant knows</h2>
        <div id="memory-list" class="list muted">Loading...</div>
      </div>
      <div class="panel">
        <div class="kicker">Future-ready</div>
        <h2>What this account grows into</h2>
        <div class="list">
          <div class="item"><strong>Phone install today</strong><br><span class="muted">Use the web app on your home screen right now.</span></div>
          <div class="item"><strong>Native phone app later</strong><br><span class="muted">The same profile, memory, and contacts will carry forward.</span></div>
          <div class="item"><strong>Agent-to-agent workflows</strong><br><span class="muted">Future versions can help schedule, buy, and coordinate with other trusted assistants online.</span></div>
        </div>
      </div>
    </section>

    <script>
      let appState = null;

      function fillPrompt(text) {
        document.getElementById('assistant-prompt').value = text;
      }

      function renderBriefing() {
        const briefing = appState.daily_briefing || {};
        document.getElementById('briefing-headline').textContent = briefing.headline || 'Your assistant is ready.';
        document.getElementById('briefing-summary').textContent = briefing.summary || 'No summary available yet.';
        const box = document.getElementById('briefing-suggestions');
        box.innerHTML = '';
        for (const item of (briefing.suggestions || [])) {
          const div = document.createElement('div');
          div.className = 'item';
          div.innerHTML = '<span class="muted">' + item + '</span>';
          box.appendChild(div);
        }
      }

      function renderSummaries() {
        document.getElementById('accessibility-summary').textContent =
          'Voice guidance ' + (appState.state.accessibility.voice_guidance ? 'on' : 'off') +
          ', text size ' + appState.state.accessibility.text_scale + '.';
        document.getElementById('preferences-summary').textContent =
          (appState.state.preferences || []).map(p => p.summary).join(', ') || 'No saved preferences yet.';
        document.getElementById('trusted-summary').textContent =
          (appState.state.trusted_circle || []).map(p => p.name).join(', ') || 'No trusted people added yet.';
      }

      function renderContacts() {
        const list = document.getElementById('contacts-list');
        list.innerHTML = '';
        const contacts = appState.state.contacts || [];
        if (!contacts.length) {
          list.textContent = 'No contacts saved yet.';
          return;
        }
        for (const contact of contacts) {
          const div = document.createElement('div');
          div.className = 'item';
          div.innerHTML =
            '<strong>' + contact.name + '</strong><br>' +
            '<span class="muted">' + contact.phone + '</span><br>' +
            '<span class="small muted">' + (contact.notes || 'No notes yet.') + (contact.shared ? ' · shared contact' : '') + '</span>';
          list.appendChild(div);
        }
      }

      function renderTrusted() {
        const list = document.getElementById('trusted-list');
        list.innerHTML = '';
        const people = appState.state.trusted_circle || [];
        if (!people.length) {
          list.textContent = 'No trusted people added yet.';
          return;
        }
        for (const person of people) {
          const div = document.createElement('div');
          div.className = 'item';
          div.innerHTML =
            '<strong>' + person.name + '</strong><br>' +
            '<span class="muted">' + person.email + '</span><br>' +
            '<span class="small muted">' + person.role + '</span>';
          list.appendChild(div);
        }
      }

      function renderMemory() {
        const list = document.getElementById('memory-list');
        list.innerHTML = '';
        const groups = [
          ['preferences', 'Preferences'],
          ['habits', 'Habits'],
          ['relationships', 'Relationships'],
          ['life_details', 'Life details']
        ];
        let hasItems = false;
        for (const [key, label] of groups) {
          const entries = appState.state[key] || [];
          for (const entry of entries) {
            hasItems = true;
            const div = document.createElement('div');
            div.className = 'item';
            div.innerHTML =
              '<strong>' + label + '</strong><br>' +
              '<span class="muted">' + entry.summary + '</span>' +
              (entry.detail ? '<br><span class="small muted">' + entry.detail + '</span>' : '');
            list.appendChild(div);
          }
        }
        if (!hasItems) {
          list.textContent = 'No saved memory yet.';
        }
      }

      function hydrateApp(data) {
        appState = data;
        document.getElementById('welcome-name').textContent = 'Hello, ' + appState.user.display_name;
        document.getElementById('welcome-copy').textContent =
          'Your assistant can already help organize contacts, memory, and trusted support while the phone-native experience keeps growing.';
        document.getElementById('profile-display-name').value = appState.user.display_name || '';
        document.getElementById('profile-voice-guidance').value = String(appState.state.accessibility.voice_guidance);
        document.getElementById('profile-text-scale').value = appState.state.accessibility.text_scale;
        renderBriefing();
        renderSummaries();
        renderContacts();
        renderTrusted();
        renderMemory();
      }

      async function fetchBootstrap() {
        const res = await fetch('/app/api/bootstrap');
        if (res.status === 401) {
          window.location.href = '/';
          return;
        }
        const data = await res.json();
        hydrateApp(data);
      }

      async function askAssistant() {
        const res = await fetch('/app/api/assistant', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: document.getElementById('assistant-prompt').value,
            interface_mode: document.getElementById('assistant-mode').value
          })
        });
        const data = await res.json();
        const reply = document.getElementById('assistant-reply');
        if (!res.ok) {
          reply.textContent = data.detail || 'The assistant could not answer right now.';
          reply.className = 'assistant-reply danger-text';
          return;
        }
        reply.textContent = '[' + data.mode + ' / ' + data.interface_mode + '] ' + data.text;
        reply.className = 'assistant-reply';
      }

      async function saveProfile() {
        const res = await fetch('/app/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            display_name: document.getElementById('profile-display-name').value,
            preference_summary: document.getElementById('profile-preference').value,
            voice_guidance: document.getElementById('profile-voice-guidance').value === 'true',
            text_scale: document.getElementById('profile-text-scale').value
          })
        });
        const data = await res.json();
        const el = document.getElementById('profile-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not save profile.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Profile updated.';
        el.className = 'status success';
        document.getElementById('profile-preference').value = '';
        hydrateApp({ user: data.user, state: data.state, daily_briefing: data.daily_briefing });
      }

      async function addContact() {
        const res = await fetch('/app/api/contacts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: document.getElementById('contact-name').value,
            phone: document.getElementById('contact-phone').value,
            notes: document.getElementById('contact-notes').value,
            shared: document.getElementById('contact-shared').value === 'true'
          })
        });
        const data = await res.json();
        const el = document.getElementById('contact-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not add contact.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Contact added.';
        el.className = 'status success';
        document.getElementById('contact-name').value = '';
        document.getElementById('contact-phone').value = '';
        document.getElementById('contact-notes').value = '';
        hydrateApp({ user: appState.user, state: data.state, daily_briefing: data.daily_briefing });
      }

      async function addTrustedPerson() {
        const res = await fetch('/app/api/trusted-circle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: document.getElementById('trusted-name').value,
            email: document.getElementById('trusted-email').value,
            role: document.getElementById('trusted-role').value
          })
        });
        const data = await res.json();
        const el = document.getElementById('trusted-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not add trusted person.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Trusted person added.';
        el.className = 'status success';
        document.getElementById('trusted-name').value = '';
        document.getElementById('trusted-email').value = '';
        document.getElementById('trusted-role').value = '';
        hydrateApp({ user: appState.user, state: data.state, daily_briefing: data.daily_briefing });
      }

      async function addMemory() {
        const res = await fetch('/app/api/memory', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            category: document.getElementById('memory-category').value,
            summary: document.getElementById('memory-summary').value,
            detail: document.getElementById('memory-detail').value
          })
        });
        const data = await res.json();
        const el = document.getElementById('memory-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not save memory.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Memory saved.';
        el.className = 'status success';
        document.getElementById('memory-summary').value = '';
        document.getElementById('memory-detail').value = '';
        hydrateApp({ user: appState.user, state: data.state, daily_briefing: data.daily_briefing });
      }

      async function logoutUser() {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.href = '/';
      }

      fetchBootstrap();
    </script>
    """
    return _base_shell("My AI", body, app_shell=True)


def render_download_page(user_name: str) -> str:
    body = f"""
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>Install access unlocked</strong></div>
        <div class="badge">Account-linked onboarding</div>
        <div class="badge">Ready for friend testing</div>
      </div>
      <div class="kicker">Install</div>
      <h1>Put Personal AI Phone on your phone.</h1>
      <p>Hello {user_name}. This version is designed to work as a mobile-friendly web app right now, so your friends can test it without an app store.</p>
    </section>

    <section class="layout-2">
      <div class="panel">
        <h2>How to install it now</h2>
        <ol class="steps">
          <li>Open this page on your iPhone or Android browser.</li>
          <li>Sign in with the same account you created on the web.</li>
          <li>Choose “Add to Home Screen” in your browser.</li>
          <li>Open the app from your home screen just like a normal app.</li>
          <li>Your profile, contacts, memory, and trusted circle stay linked to your account.</li>
        </ol>
        <div class="cta-row" style="margin-top:16px;">
          <a class="button" href="/app">Open my assistant</a>
          <a class="button secondary" href="/">Back to home</a>
        </div>
      </div>

      <div class="panel">
        <h2>Share this with a friend</h2>
        <div class="qr-box">
          <p class="small muted">Open this link on the phone you want to test</p>
          <div class="install-link">https://telefon-phi.vercel.app</div>
          <p class="small muted" style="margin-top:12px;">
            Version 1 is a web app with account-based onboarding. The same profile can later connect to the deeper native app experience.
          </p>
        </div>
      </div>
    </section>
    """
    return _base_shell("Install Personal AI Phone", body, app_shell=True)


def manifest_payload() -> str:
    return json.dumps(
        {
            "name": "Personal AI Phone",
            "short_name": "Personal AI",
            "start_url": "/app",
            "display": "standalone",
            "background_color": "#102026",
            "theme_color": "#102026",
            "description": "A calm, large-format personal assistant for calls, planning, memory, and everyday help.",
        }
    )


def service_worker_payload() -> str:
    return """
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});
self.addEventListener('fetch', () => {});
"""
