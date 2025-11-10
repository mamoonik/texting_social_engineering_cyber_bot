// static/chat.js

// --- Typing indicator helpers ---
function showTypingIndicator() {
  const log = document.getElementById("log");
  let el = document.getElementById("typing-indicator");
  if (!el) {
    el = document.createElement("div");
    el.id = "typing-indicator";
    el.style.fontStyle = "italic";
    el.style.color = "gray";
    el.style.margin = "4px 0";
    el.textContent = "recruiter is typing…";
    log.appendChild(el);
  }
  log.scrollTop = log.scrollHeight;
}

function hideTypingIndicator() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

// --- Chat boot ---
(() => {
  const conv = document.getElementById("conv_id").innerText || "demo-1";
  const log = document.getElementById("log");
  const wsProto = location.protocol === "https:" ? "wss://" : "ws://";
  const wsUrl = wsProto + location.host + "/ws/" + conv;
  let ws;

  function appendEvent(ev) {
    const div = document.createElement("div");
    div.className = "ev";
    const actorClass = ev.actor === "recruiter" ? "recruiter" : "employee";
    const ts = ev.ts ? new Date(ev.ts).toLocaleString() : new Date().toLocaleString();
    div.innerHTML = `
      <div class="actor ${actorClass}">${ev.actor}</div>
      <div class="text">${ev.text || ""}</div>
      <div class="meta">${ts}</div>
    `;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  function connect() {
    ws = new WebSocket(wsUrl);

    ws.addEventListener("open", () => {
      console.log("WS open", wsUrl);
    });

    // ws.addEventListener("message", (e) => {
    //   let ev;
    //   try {
    //     ev = JSON.parse(e.data);
    //   } catch (err) {
    //     console.error("Bad WS payload:", e.data, err);
    //     return;
    //   }

    //   // Typing protocol
    //   if (typeof ev.typing === "boolean") {
    //     if (ev.typing) showTypingIndicator();
    //     else hideTypingIndicator();
    //     // typing events may or may not carry text; if no text, stop here
    //     if (!ev.text) return;
    //   }

    //   // Any real line from recruiter should clear typing first
    //   if (ev.actor === "recruiter") hideTypingIndicator();

    //   if (ev.text) appendEvent(ev);
    // });

    // ws.addEventListener("message", (e) => {
    //   try {
    //     const ev = JSON.parse(e.data);
    
    //     if (ev.typing === true) {
    //       showTypingIndicator();
    //       return;
    //     }
    //     if (ev.typing === false) {
    //       hideTypingIndicator();
    //       return;
    //     }
    
    //     // real message
    //     hideTypingIndicator();
    //     appendEvent(ev);
    //   } catch (err) {
    //     console.error("Bad message", e.data, err);
    //   }
    // });

    ws.addEventListener("message", (e) => {
      try {
        const ev = JSON.parse(e.data);
    
        if (ev.typing === true) {
          showTypingIndicator();
          return;
        }
        if (ev.typing === false) {
          hideTypingIndicator();
          return;
        }
    
        hideTypingIndicator();       // clear before real text
        appendEvent(ev);
      } catch (err) {
        console.error("Bad message", e.data, err);
      }
    });
    
    ws.addEventListener("close", () => {
      console.log("WS closed, reconnecting in 1s…");
      setTimeout(connect, 1000);
    });

    ws.addEventListener("error", (err) => {
      console.error("WS error", err);
    });
  }

  // Start the socket
  connect();

  // Send employee message (form onSubmit calls this)
  window.sendMessage = function () {
    const input = document.getElementById("msg");
    const txt = input.value.trim();
    if (!txt) return false;

    const payload = { actor: "employee", text: txt };
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
    } else {
      console.warn("WebSocket not open — message not sent");
    }
    input.value = "";
    return false;
  };

  // Also allow Enter to send (without submitting the page)
  const inputEl = document.getElementById("msg");
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      window.sendMessage();
    }
  });

  // Trigger initial recruiter message using x-www-form-urlencoded POST
  document.getElementById("triggerBtn").addEventListener("click", async () => {
    try {
      const body = new URLSearchParams({ conv_id: conv });
      const resp = await fetch("/recruiter/send", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });
      if (!resp.ok) {
        console.error("Trigger failed", resp.status, await resp.text());
      } else {
        console.log("Recruiter trigger sent");
      }
    } catch (err) {
      console.error("Trigger error", err);
    }
  });
})();
