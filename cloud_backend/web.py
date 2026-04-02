from __future__ import annotations

import json


def _base_shell(title: str, body: str, *, app_shell: bool = False) -> str:
    app_nav = """
    <div class="nav">
      <div class="brand-wrap">
        <div class="brand">Personal AI Phone</div>
        <div class="tagline">A calmer assistant for everyday life</div>
      </div>
      <div class="nav-links">
        <a href="/app">Home</a>
        <a href="/download">Install</a>
        <a href="/app#profile">Profile</a>
        <button type="button" class="nav-button" onclick="window.logoutUser && window.logoutUser()">Sign out</button>
      </div>
    </div>
    """
    nav = app_nav if app_shell else ""
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="theme-color" content="#f4efe6">
  <link rel="manifest" href="/manifest.webmanifest">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;500;600;700;800&display=swap');
    :root {{
      --bg: #f4efe6;
      --bg-accent: #ebe3d5;
      --surface: #fffdfa;
      --surface-2: #f7f1e7;
      --surface-3: #e9f0fb;
      --text: #18252b;
      --muted: #475961;
      --accent: #1f5fbf;
      --accent-2: #3c78d8;
      --accent-soft: #dce9ff;
      --success: #1d6b45;
      --warning: #7a4d00;
      --danger: #992b2b;
      --border: #cbd4d8;
      --border-strong: #9caab0;
      --shadow: 0 18px 40px rgba(37, 55, 66, 0.10);
      --shadow-soft: 0 6px 18px rgba(37, 55, 66, 0.08);
      --focus: 0 0 0 4px rgba(31, 95, 191, 0.18);
    }}
    * {{ box-sizing: border-box; }}
    html {{ font-size: 18px; }}
    body {{
      margin: 0;
      font-family: "Atkinson Hyperlegible Next", "Segoe UI", Arial, sans-serif;
      color: var(--text);
      background:
        linear-gradient(180deg, rgba(255,255,255,0.72), rgba(255,255,255,0.72)),
        radial-gradient(circle at top right, rgba(31,95,191,0.06), transparent 30%),
        linear-gradient(180deg, var(--bg), var(--bg-accent));
    }}
    a {{ color: inherit; text-decoration: none; }}
    button, input, textarea, select {{
      font-family: inherit;
    }}
    input:focus, textarea:focus, select:focus, button:focus, a:focus {{
      outline: none;
      box-shadow: var(--focus);
    }}
    .page {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 16px 16px 40px;
      display: grid;
      gap: 20px;
    }}
    .nav {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
      padding: 4px 2px 6px;
      position: sticky;
      top: 0;
      z-index: 20;
      background: rgba(244, 239, 230, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(156, 170, 176, 0.35);
    }}
    .brand-wrap {{
      display: grid;
      gap: 4px;
    }}
    .brand {{
      font-size: 1.18rem;
      font-weight: 900;
    }}
    .tagline {{
      font-size: 0.94rem;
      color: var(--muted);
    }}
    .nav-links {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      color: var(--text);
      align-items: center;
    }}
    .nav-links a, .nav-button {{
      padding: 12px 16px;
      border-radius: 999px;
      background: var(--surface);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-soft);
    }}
    .nav-button {{
      color: inherit;
      min-height: auto;
      font-weight: 700;
      cursor: pointer;
    }}
    .hero, .panel, .card {{
      border-radius: 24px;
      border: 1px solid var(--border);
      background: var(--surface);
      box-shadow: var(--shadow);
    }}
    .hero {{
      padding: 28px;
      display: grid;
      gap: 16px;
      background:
        linear-gradient(180deg, rgba(220,233,255,0.55), rgba(255,253,250,0.96) 42%),
        var(--surface);
    }}
    .panel, .card {{
      padding: 22px;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.5rem, 6vw, 4.3rem);
      line-height: 0.98;
      max-width: 10ch;
      letter-spacing: -0.03em;
    }}
    h2 {{
      margin: 0;
      font-size: 1.7rem;
      line-height: 1.15;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 1.18rem;
      line-height: 1.2;
    }}
    p, li {{
      line-height: 1.7;
      color: var(--muted);
    }}
    .badge-row, .cta-row, .tab-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .feature-carousel {{
      display: grid;
      gap: 12px;
    }}
    .feature-carousel-card {{
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--surface-2);
      padding: 14px 18px;
      min-height: 66px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      box-shadow: var(--shadow-soft);
      transition: opacity 220ms ease, transform 220ms ease;
    }}
    .feature-carousel-title {{
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--text);
      line-height: 1.35;
    }}
    .feature-carousel-meta {{
      display: flex;
      justify-content: center;
      gap: 8px;
    }}
    .feature-dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: #c6d0d6;
      transition: transform 180ms ease, background 180ms ease;
    }}
    .feature-dot.active {{
      background: var(--accent);
      transform: scale(1.15);
    }}
    .badge, .tab-button {{
      border-radius: 999px;
      padding: 12px 16px;
      font-size: 0.96rem;
      border: 1px solid var(--border);
      background: var(--surface-2);
    }}
    .badge strong {{ color: var(--accent); }}
    .tab-button {{
      color: var(--text);
      cursor: pointer;
      font-weight: 800;
      background: var(--surface);
    }}
    .tab-button.active {{
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }}
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
    .list {{
      display: grid;
      gap: 12px;
    }}
    .item {{
      padding: 16px;
      border-radius: 18px;
      background: var(--surface-2);
      border: 1px solid var(--border);
    }}
    .summary-box {{
      padding: 18px;
      border-radius: 20px;
      background: var(--surface-2);
      border: 1px solid var(--border);
    }}
    .big-stat {{
      font-size: 1.3rem;
      font-weight: 900;
      color: var(--text);
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
      color: var(--text);
    }}
    button, .button, input, textarea, select {{
      font: inherit;
      border-radius: 18px;
    }}
    button, .button {{
      border: 0;
      min-height: 60px;
      padding: 16px 22px;
      cursor: pointer;
      font-weight: 900;
      color: #ffffff;
      background: linear-gradient(180deg, var(--accent-2), var(--accent));
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      box-shadow: 0 10px 20px rgba(31, 95, 191, 0.18);
    }}
    .secondary {{
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border-strong);
      box-shadow: none;
    }}
    input, textarea, select {{
      width: 100%;
      min-height: 62px;
      border: 2px solid var(--border);
      background: #fffefb;
      color: var(--text);
      padding: 15px 16px;
      font-size: 1rem;
      box-shadow: inset 0 1px 1px rgba(24, 37, 43, 0.03);
    }}
    input::placeholder, textarea::placeholder {{
      color: #7b878d;
    }}
    textarea {{
      min-height: 150px;
      resize: vertical;
    }}
    .status {{
      min-height: 1.5rem;
      font-size: 0.98rem;
      color: var(--muted);
    }}
    .success {{ color: var(--success); font-weight: 800; }}
    .warning-text {{ color: var(--warning); font-weight: 800; }}
    .danger-text {{ color: var(--danger); font-weight: 800; }}
    .muted {{ color: var(--muted); }}
    .small {{ font-size: 0.93rem; }}
    .assistant-reply {{
      min-height: 150px;
      white-space: pre-wrap;
    }}
    .section.hidden {{
      display: none;
    }}
    .kicker {{
      color: var(--accent);
      font-weight: 900;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      font-size: 0.84rem;
    }}
    .help-note {{
      border-left: 4px solid var(--accent);
      padding-left: 12px;
    }}
    .cta-row > * {{
      flex: 1 1 220px;
    }}
    @media (max-width: 980px) {{
      html {{ font-size: 18px; }}
      .layout-2, .grid-2, .grid-3, .row-2 {{ grid-template-columns: 1fr; }}
      h1 {{ max-width: none; }}
      .nav {{
        position: static;
        border-bottom: 0;
      }}
    }}
    @media (max-width: 760px) {{
      .page {{
        padding: 12px 12px 28px;
      }}
      .hero, .panel, .card {{
        border-radius: 20px;
      }}
      .hero {{
        padding: 22px 18px;
      }}
      .panel, .card, .summary-box {{
        padding: 18px;
      }}
      .nav-links {{
        width: 100%;
      }}
      .nav-links a, .nav-button {{
        flex: 1 1 calc(50% - 10px);
        justify-content: center;
        text-align: center;
      }}
      .badge, .tab-button {{
        width: 100%;
        justify-content: center;
        text-align: center;
      }}
      .feature-carousel-card {{
        border-radius: 20px;
        min-height: 84px;
      }}
      .cta-row > * {{
        flex-basis: 100%;
      }}
      button, .button, input, textarea, select {{
        font-size: 1rem;
      }}
      h1 {{
        font-size: clamp(2.1rem, 12vw, 3rem);
        line-height: 1.02;
      }}
      h2 {{
        font-size: 1.45rem;
      }}
      .summary-box {{
        border-radius: 18px;
      }}
    }}
    @media (max-width: 420px) {{
      html {{
        font-size: 17px;
      }}
      .nav-links a, .nav-button {{
        flex-basis: 100%;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    {nav}
    {body}
  </main>
  <script>
    window.logoutUser = async function logoutUser() {{
      try {{
        await fetch('/auth/logout', {{ method: 'POST' }});
      }} finally {{
        window.location.href = '/';
      }}
    }};
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
      <div class="brand-wrap">
        <div class="brand">Personal AI Phone</div>
        <div class="tagline">A calmer assistant for everyday life</div>
      </div>
      <div class="kicker">One helpful assistant</div>
      <h1>Stop hunting for apps. Ask for help once.</h1>
      <p>
        Personal AI Phone is a calmer, easier way to use a phone. Instead of remembering where everything lives,
        the user gets one assistant that can remember people, save preferences, send the app to their phone, and grow into a fuller AI companion over time.
      </p>
    </section>

    <section class="grid-2">
      <div class="panel">
        <div class="kicker">Create your account</div>
        <h2>We’ll keep it simple</h2>
        <p class="small">We keep just the basics here: first name, last name, email, phone number, and password. Those details become your profile and your shareable contact card later.</p>
        <div class="form">
          <div class="row-2">
            <label>First name
              <input id="register-first-name" placeholder="Pat" />
            </label>
            <label>Last name
              <input id="register-last-name" placeholder="Tulin" />
            </label>
          </div>
          <div class="row-2">
            <label>Email
              <input id="register-email" type="email" placeholder="you@example.com" />
            </label>
            <label>Phone number
              <input id="register-phone" type="tel" placeholder="+1 555 123 0000" />
            </label>
          </div>
          <label>Password
            <input id="register-password" type="password" placeholder="At least 8 characters" />
          </label>
          <button id="register-button" onclick="registerUser()">Create my account</button>
          <div id="register-status" class="status">After you join, we can email the app link to you in one tap.</div>
        </div>
      </div>

      <div class="panel">
        <div class="kicker">Sign in</div>
        <h2>Return to your assistant</h2>
        <div class="form">
          <label>Email
            <input id="login-email" type="email" placeholder="you@example.com" />
          </label>
          <label>Password
            <input id="login-password" type="password" placeholder="Password" />
          </label>
          <button id="login-button" onclick="loginUser()">Open my assistant</button>
          <div id="login-status" class="status">After signing in, you can send the app link to your phone with one tap.</div>
        </div>

        <div class="summary-box" style="margin-top:16px;">
          <h3>Forgot your password?</h3>
          <div class="form">
            <label>Email
              <input id="help-email" type="email" placeholder="you@example.com" />
            </label>
            <button id="help-button" class="secondary" onclick="sendPasswordHelp()">Email me a reset link</button>
            <div id="help-status" class="status">For this beta, recovery is email-first so it stays simple and reliable.</div>
          </div>
        </div>
      </div>
    </section>

    <script>
      function normalizeEmail(value) {
        return (value || '').trim().toLowerCase();
      }

      function formatPhone(value) {
        const digits = (value || '').replace(/\D/g, '').slice(0, 11);
        if (!digits) return '';
        if (digits.length === 11 && digits.startsWith('1')) {
          return `+1 ${digits.slice(1, 4)} ${digits.slice(4, 7)} ${digits.slice(7)}`.trim();
        }
        if (digits.length <= 3) return digits;
        if (digits.length <= 6) return `${digits.slice(0, 3)} ${digits.slice(3)}`;
        return `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
      }

      function setPhoneFormatting(id) {
        const input = document.getElementById(id);
        if (!input) return;
        input.addEventListener('input', () => {
          input.value = formatPhone(input.value);
        });
      }

      function apiMessage(data, fallback) {
        if (!data) return fallback;
        if (typeof data.detail === 'string') return data.detail;
        if (typeof data.message === 'string') return data.message;
        if (Array.isArray(data.detail) && data.detail.length) {
          const first = data.detail[0];
          if (typeof first === 'string') return first;
          if (first && typeof first.msg === 'string') return first.msg;
        }
        return fallback;
      }

      function requireValue(value, message, statusId) {
        if ((value || '').trim()) return true;
        const el = document.getElementById(statusId);
        el.textContent = message;
        el.className = 'status warning-text';
        return false;
      }

      function setButtonBusy(id, busyText, idleText, busy) {
        const button = document.getElementById(id);
        if (!button) return;
        button.disabled = busy;
        button.textContent = busy ? busyText : idleText;
        button.style.opacity = busy ? '0.75' : '1';
        button.style.cursor = busy ? 'progress' : 'pointer';
      }

      async function registerUser() {
        const firstName = document.getElementById('register-first-name').value.trim();
        const lastName = document.getElementById('register-last-name').value.trim();
        const email = normalizeEmail(document.getElementById('register-email').value);
        const phone = document.getElementById('register-phone').value.trim();
        const password = document.getElementById('register-password').value;
        if (!requireValue(firstName, 'Enter your first name.', 'register-status')) return;
        if (!requireValue(lastName, 'Enter your last name.', 'register-status')) return;
        if (!requireValue(email, 'Enter your email address.', 'register-status')) return;
        if (!requireValue(phone, 'Enter your phone number.', 'register-status')) return;
        if (!requireValue(password, 'Create a password.', 'register-status')) return;
        const status = document.getElementById('register-status');
        status.textContent = 'Creating your account...';
        status.className = 'status';
        setButtonBusy('register-button', 'Creating your account...', 'Create my account', true);
        const res = await fetch('/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            first_name: firstName,
            last_name: lastName,
            email,
            phone_number: phone,
            password
          })
        });
        const data = await res.json();
        setButtonBusy('register-button', 'Creating your account...', 'Create my account', false);
        const el = document.getElementById('register-status');
        if (!res.ok) {
          el.textContent = apiMessage(data, 'Registration failed.');
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Account created. Opening your assistant...';
        el.className = 'status success';
        window.location.href = '/app';
      }

      async function loginUser() {
        const email = normalizeEmail(document.getElementById('login-email').value);
        const password = document.getElementById('login-password').value;
        if (!requireValue(email, 'Enter the email address for your account.', 'login-status')) return;
        if (!requireValue(password, 'Enter your password.', 'login-status')) return;
        const status = document.getElementById('login-status');
        status.textContent = 'Signing you in...';
        status.className = 'status';
        setButtonBusy('login-button', 'Opening your assistant...', 'Open my assistant', true);
        const res = await fetch('/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            password
          })
        });
        const data = await res.json();
        setButtonBusy('login-button', 'Opening your assistant...', 'Open my assistant', false);
        const el = document.getElementById('login-status');
        if (!res.ok) {
          el.textContent = apiMessage(data, 'Login failed.');
          el.className = 'status warning-text';
          return;
        }
        el.textContent = 'Signed in. Opening your assistant...';
        el.className = 'status success';
        window.location.href = '/app';
      }

      async function sendPasswordHelp() {
        const email = normalizeEmail(document.getElementById('help-email').value);
        if (!requireValue(email, 'Enter the email address for your account.', 'help-status')) return;
        const status = document.getElementById('help-status');
        status.textContent = 'Preparing your reset link...';
        status.className = 'status';
        setButtonBusy('help-button', 'Preparing your reset link...', 'Email me a reset link', true);
        const res = await fetch('/auth/password-help', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            channel: 'email'
          })
        });
        const data = await res.json();
        setButtonBusy('help-button', 'Preparing your reset link...', 'Email me a reset link', false);
        const el = document.getElementById('help-status');
        if (!res.ok) {
          el.textContent = apiMessage(data, 'Could not prepare password help.');
          el.className = 'status warning-text';
          return;
        }
        el.textContent = data.message || 'Password help is ready.';
        el.className = 'status success';
        if (data.action_url) {
          window.open(data.action_url, '_blank');
        }
      }

      setPhoneFormatting('register-phone');
    </script>
    """
    return _base_shell("Personal AI Phone", body)


def render_app_page() -> str:
    body = """
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>My AI</strong> personal dashboard</div>
        <div class="badge">Calls, memory, and trusted helpers together</div>
      </div>
      <div class="layout-2">
        <div class="stack">
          <div class="kicker">Welcome</div>
          <h1 id="welcome-name">Loading...</h1>
          <p id="welcome-copy">Preparing your assistant, your contacts, and your account.</p>
          <div class="tab-row" id="tab-row"></div>
        </div>
        <div class="summary-box">
          <h3>Today at a glance</h3>
          <div class="big-stat" id="briefing-headline">Loading...</div>
          <p id="briefing-summary" class="muted">Loading...</p>
          <div id="briefing-suggestions" class="list"></div>
        </div>
      </div>
    </section>

    <section id="tab-home" class="section">
      <div class="layout-2">
        <div class="panel">
          <div class="kicker">Assistant</div>
          <h2>Ask for what you need</h2>
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
            <label>What should I help with?
              <textarea id="assistant-prompt" placeholder="Call Alice, schedule lunch, remember a preference, or help me buy something."></textarea>
            </label>
            <div class="cta-row">
              <button onclick="askAssistant()">Ask my assistant</button>
              <button class="secondary" onclick="fillPrompt('Call Alice')">Call someone</button>
              <button class="secondary" onclick="fillPrompt('Schedule lunch next Tuesday')">Plan my day</button>
            </div>
            <div class="summary-box">
              <h3>Assistant response</h3>
              <div id="assistant-reply" class="assistant-reply muted">Nothing yet.</div>
            </div>
          </div>
        </div>

        <div class="stack">
          <div class="panel">
            <div class="kicker">Send it to my phone</div>
            <h2>One tap is better than instructions</h2>
            <p class="help-note" id="install-targets">Loading your saved email address.</p>
            <button onclick="sendInstallLink()">Email me the app</button>
            <div id="install-status" class="status">For this beta, we send the app link by email so onboarding stays predictable.</div>
          </div>

          <div class="panel">
            <div class="kicker">Easy recovery</div>
            <h2>Password help</h2>
            <p class="small">If you ever forget your password, we can email you a reset link right away.</p>
            <button class="secondary" onclick="sendSignedInPasswordHelp()">Email me a reset link</button>
            <div id="password-help-status" class="status">This is here so support is always close by.</div>
          </div>

        </div>
      </div>
    </section>

    <section id="tab-profile" class="section hidden">
      <div class="grid-2">
        <div class="panel">
          <div class="kicker">Profile</div>
          <h2>Your account</h2>
          <div class="form">
            <div class="row-2">
              <label>First name
                <input id="profile-first-name" />
              </label>
              <label>Last name
                <input id="profile-last-name" />
              </label>
            </div>
            <div class="row-2">
              <label>Email
                <input id="profile-email" type="email" />
              </label>
              <label>Phone number
                <input id="profile-phone-number" type="tel" />
              </label>
            </div>
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
            <button onclick="saveProfile()">Save my account</button>
            <div id="profile-status" class="status">These details make up your profile and your future shareable contact card.</div>
            <div class="summary-box">
              <h3>My contact card</h3>
              <div id="profile-card-summary" class="muted">Loading your saved profile.</div>
            </div>
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

      <div class="grid-2">
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
            <div id="contact-status" class="status">Shared contacts are for family, caregivers, or other trusted support.</div>
          </div>
          <div id="contacts-list" class="list" style="margin-top:16px;"></div>
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
            <div id="trusted-status" class="status">Trusted people are the ones your assistant can coordinate with later.</div>
          </div>
          <div id="trusted-list" class="list" style="margin-top:16px;"></div>
        </div>
      </div>

      <div class="panel">
        <div class="kicker">Saved memory</div>
        <h2>What your assistant knows</h2>
        <div id="memory-list" class="list"></div>
      </div>
    </section>

    <section id="tab-users" class="section hidden">
      <div class="panel">
        <div class="kicker">Admin</div>
        <h2>User management</h2>
        <p class="small">This tab is only visible to the admin account.</p>
        <button onclick="loadAdminUsers()">Refresh users</button>
        <div id="admin-users-status" class="status">Loading user list.</div>
        <div id="admin-users-list" class="list" style="margin-top:16px;"></div>
      </div>
    </section>

    <section id="tab-analytics" class="section hidden">
      <div class="panel">
        <div class="kicker">Analytics</div>
        <h2>Simple system overview</h2>
        <button onclick="loadAnalytics()">Refresh analytics</button>
        <div id="analytics-status" class="status">Loading analytics.</div>
        <div class="grid-3" id="analytics-cards" style="margin-top:16px;"></div>
        <div id="analytics-users" class="list" style="margin-top:16px;"></div>
      </div>
    </section>

    <script>
      let appState = null;
      const regularTabs = [
        { id: 'home', label: 'Home' },
        { id: 'profile', label: 'Profile' }
      ];
      const adminTabs = [
        { id: 'home', label: 'Home' },
        { id: 'users', label: 'Users' },
        { id: 'analytics', label: 'Analytics' },
        { id: 'profile', label: 'Profile' }
      ];

      function fillPrompt(text) {
        document.getElementById('assistant-prompt').value = text;
      }

      function activeTabs() {
        return appState && appState.user && appState.user.is_admin ? adminTabs : regularTabs;
      }

      function buildTabs() {
        const row = document.getElementById('tab-row');
        row.innerHTML = '';
        for (const tab of activeTabs()) {
          const button = document.createElement('button');
          button.className = 'tab-button secondary';
          button.textContent = tab.label;
          button.onclick = () => setTab(tab.id);
          button.id = 'tab-button-' + tab.id;
          row.appendChild(button);
        }
      }

      function setTab(id) {
        document.querySelectorAll('.section').forEach((section) => section.classList.add('hidden'));
        const target = document.getElementById('tab-' + id);
        if (target) target.classList.remove('hidden');
        document.querySelectorAll('.tab-button').forEach((button) => button.classList.remove('active'));
        const active = document.getElementById('tab-button-' + id);
        if (active) active.classList.add('active');
        if (id === 'users') loadAdminUsers();
        if (id === 'analytics') loadAnalytics();
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
          div.textContent = item;
          box.appendChild(div);
        }
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
          div.innerHTML = '<strong>' + contact.name + '</strong><br><span class="muted">' + contact.phone + '</span><br><span class="small muted">' + (contact.notes || 'No notes yet.') + (contact.shared ? ' · shared contact' : '') + '</span>';
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
          div.innerHTML = '<strong>' + person.name + '</strong><br><span class="muted">' + person.email + '</span><br><span class="small muted">' + person.role + '</span>';
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
            div.innerHTML = '<strong>' + label + '</strong><br><span class="muted">' + entry.summary + '</span>' + (entry.detail ? '<br><span class="small muted">' + entry.detail + '</span>' : '');
            list.appendChild(div);
          }
        }
        if (!hasItems) list.textContent = 'No saved memory yet.';
      }

      function hydrateApp(data) {
        appState = data;
        buildTabs();
        document.getElementById('welcome-name').textContent = 'Hello, ' + (appState.user.first_name || appState.user.display_name);
        document.getElementById('welcome-copy').textContent = 'Your assistant is set up to help and can send the app straight to your phone.';
        document.getElementById('profile-first-name').value = appState.user.first_name || '';
        document.getElementById('profile-last-name').value = appState.user.last_name || '';
        document.getElementById('profile-email').value = appState.user.email || '';
        document.getElementById('profile-phone-number').value = appState.user.phone_number || '';
        document.getElementById('profile-voice-guidance').value = String(appState.state.accessibility.voice_guidance);
        document.getElementById('profile-text-scale').value = appState.state.accessibility.text_scale;
        document.getElementById('profile-card-summary').innerHTML =
          '<strong>' + appState.user.display_name + '</strong><br>' +
          '<span>' + appState.user.email + '</span><br>' +
          '<span>' + (appState.user.phone_number || 'No phone number saved yet.') + '</span>';
        document.getElementById('install-targets').textContent =
          'We can email the app link to ' + appState.user.email + '.';
        renderBriefing();
        renderContacts();
        renderTrusted();
        renderMemory();
        const requestedTab = window.location.hash === '#profile' ? 'profile' : activeTabs()[0].id;
        setTab(requestedTab);
      }

      async function fetchBootstrap() {
        const res = await fetch('/app/api/bootstrap');
        if (res.status === 401) {
          window.location.href = '/';
          return;
        }
        hydrateApp(await res.json());
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
        reply.textContent = data.text;
        reply.className = 'assistant-reply';
      }

      async function saveProfile() {
        const res = await fetch('/app/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            first_name: document.getElementById('profile-first-name').value,
            last_name: document.getElementById('profile-last-name').value,
            email: document.getElementById('profile-email').value,
            phone_number: document.getElementById('profile-phone-number').value,
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
        setTab('profile');
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
        setTab('profile');
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
        setTab('profile');
      }

      async function sendInstallLink() {
        const res = await fetch('/app/api/install-link', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel: 'email' })
        });
        const data = await res.json();
        const el = document.getElementById('install-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not prepare the install email.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = data.message || 'Install link is ready.';
        el.className = 'status success';
        if (data.action_url) window.open(data.action_url, '_blank');
      }

      async function sendSignedInPasswordHelp() {
        const res = await fetch('/app/api/password-help', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel: 'email' })
        });
        const data = await res.json();
        const el = document.getElementById('password-help-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not prepare password help.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = data.message || 'Password help is ready.';
        el.className = 'status success';
        if (data.action_url) window.open(data.action_url, '_blank');
      }

      async function loadAdminUsers() {
        const res = await fetch('/app/api/admin/users');
        const box = document.getElementById('admin-users-list');
        const status = document.getElementById('admin-users-status');
        if (!res.ok) {
          status.textContent = 'Could not load users.';
          status.className = 'status warning-text';
          return;
        }
        const data = await res.json();
        status.textContent = data.users.length + ' users loaded.';
        status.className = 'status success';
        box.innerHTML = '';
        for (const user of data.users) {
          const div = document.createElement('div');
          div.className = 'item';
          div.innerHTML =
            '<strong>' + user.display_name + '</strong><br>' +
            '<span class="muted">' + user.email + '</span><br>' +
            '<span class="small muted">Phone: ' + (user.phone_number || 'none') + ' · Contacts: ' + user.contacts_count + ' · Memory: ' + user.memory_count + ' · Trusted: ' + user.trusted_count + '</span><br>' +
            '<span class="small muted">Admin: ' + (user.is_admin ? 'yes' : 'no') + ' · Disabled: ' + (user.is_disabled ? 'yes' : 'no') + '</span>' +
            '<div class="cta-row" style="margin-top:10px;"><button class="secondary" onclick="toggleUser(\\'' + user.user_id + '\\',' + (!user.is_disabled) + ')">' + (user.is_disabled ? 'Enable user' : 'Disable user') + '</button><button class="secondary" onclick="toggleAdmin(\\'' + user.user_id + '\\',' + (!user.is_admin) + ')">' + (user.is_admin ? 'Remove admin' : 'Make admin') + '</button></div>';
          box.appendChild(div);
        }
      }

      async function toggleUser(userId, nextValue) {
        await fetch('/app/api/admin/users/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId, is_disabled: nextValue })
        });
        loadAdminUsers();
      }

      async function toggleAdmin(userId, nextValue) {
        await fetch('/app/api/admin/users/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId, is_admin: nextValue })
        });
        loadAdminUsers();
      }

      async function loadAnalytics() {
        const res = await fetch('/app/api/admin/analytics');
        const status = document.getElementById('analytics-status');
        const cards = document.getElementById('analytics-cards');
        const users = document.getElementById('analytics-users');
        if (!res.ok) {
          status.textContent = 'Could not load analytics.';
          status.className = 'status warning-text';
          return;
        }
        const data = await res.json();
        status.textContent = 'Analytics refreshed.';
        status.className = 'status success';
        cards.innerHTML = '';
        users.innerHTML = '';
        for (const [label, value] of Object.entries(data.totals || {})) {
          const div = document.createElement('div');
          div.className = 'item';
          div.innerHTML = '<strong>' + label.replaceAll('_', ' ') + '</strong><br><span class="big-stat">' + value + '</span>';
          cards.appendChild(div);
        }
        for (const row of data.recent_users || []) {
          const div = document.createElement('div');
          div.className = 'item';
          div.innerHTML = '<strong>' + row.display_name + '</strong><br><span class="muted">' + row.email + '</span><br><span class="small muted">Joined: ' + row.created_at + '</span>';
          users.appendChild(div);
        }
      }

      window.setTab = setTab;
      window.addEventListener('hashchange', () => {
        if (window.location.hash === '#profile') {
          setTab('profile');
        } else if (window.location.hash === '#home') {
          setTab('home');
        }
      });

      fetchBootstrap();
    </script>
    """
    return _base_shell("My AI", body, app_shell=True)


def render_download_page(user_name: str) -> str:
    body = """
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>Install unlocked</strong></div>
        <div class="badge">Designed for minimal effort</div>
      </div>
      <div class="kicker">Send the app to your phone</div>
      <h1>We can send the link for you.</h1>
      <p>Hello __USER_NAME__. Instead of asking you to remember steps, this screen focuses on the easiest beta path: email the app link to yourself and open it on your phone.</p>
    </section>

    <section class="grid-2">
      <div class="panel">
        <h2>Choose the easiest option</h2>
        <button onclick="sendInstallLink()">Email me the app</button>
        <div id="install-status" class="status" style="margin-top:14px;">We’ll use your saved email address for this beta.</div>
      </div>

      <div class="panel">
        <h2>Already on your phone?</h2>
        <p class="small">If you are already on the phone you want to use, open your assistant and keep it handy from there.</p>
        <div class="cta-row">
          <a class="button" href="/app">Open my assistant</a>
          <a class="button secondary" href="/">Back to home</a>
        </div>
      </div>
    </section>

    <script>
      async function sendInstallLink() {
        const res = await fetch('/app/api/install-link', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel: 'email' })
        });
        const data = await res.json();
        const el = document.getElementById('install-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not prepare the install email.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = data.message || 'Your install link is ready.';
        el.className = 'status success';
        if (data.action_url) window.open(data.action_url, '_blank');
      }
    </script>
    """
    body = body.replace("__USER_NAME__", user_name)
    return _base_shell("Install Personal AI Phone", body, app_shell=True)


def render_reset_password_page() -> str:
    body = """
    <section class="hero">
      <div class="badge-row">
        <div class="badge"><strong>Password reset</strong></div>
        <div class="badge">Short and simple</div>
      </div>
      <div class="kicker">Reset password</div>
      <h1>Choose a new password.</h1>
      <p>Use this screen only if you asked for password help.</p>
    </section>

    <section class="panel">
      <div class="form">
        <label>Reset link token
          <input id="reset-token" />
        </label>
        <label>New password
          <input id="reset-password" type="password" placeholder="At least 8 characters" />
        </label>
        <button onclick="resetPassword()">Save new password</button>
        <div id="reset-status" class="status">Paste or open your reset link here.</div>
      </div>
    </section>

    <script>
      const params = new URLSearchParams(window.location.search);
      const token = params.get('token');
      if (token) document.getElementById('reset-token').value = token;

      async function resetPassword() {
        const res = await fetch('/auth/reset-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: document.getElementById('reset-token').value,
            new_password: document.getElementById('reset-password').value
          })
        });
        const data = await res.json();
        const el = document.getElementById('reset-status');
        if (!res.ok) {
          el.textContent = data.detail || 'Could not reset password.';
          el.className = 'status warning-text';
          return;
        }
        el.textContent = data.message || 'Password updated.';
        el.className = 'status success';
      }
    </script>
    """
    return _base_shell("Reset password", body)


def manifest_payload() -> str:
    return json.dumps(
        {
            "name": "Personal AI Phone",
            "short_name": "Personal AI",
            "start_url": "/app",
            "display": "standalone",
            "background_color": "#f4efe6",
            "theme_color": "#f4efe6",
            "description": "A calm, large-format personal assistant for calls, planning, memory, and everyday help.",
        }
    )


def service_worker_payload() -> str:
    return """
self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.map((name) => caches.delete(name)));
    const registrations = await self.registration.unregister();
    await self.clients.claim();
    const clients = await self.clients.matchAll({ type: 'window' });
    for (const client of clients) {
      client.navigate(client.url);
    }
  })());
});
self.addEventListener('fetch', () => {});
"""
