const userId = "tunnel";
let code = "";
let lastMessageIndex = 0;

// ایجاد کد تونل ویس
function generateVoiceCode() {
  fetch("http://localhost:5000/generate_voice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId })
  })
  .then(res => res.json())
  .then(data => {
    if (data.code) {
      document.getElementById('voiceTunnelCode').value = data.code;
      document.getElementById('voiceStatusMessage').textContent = "Voice tunnel code generated!";
    } else {
      document.getElementById('voiceStatusMessage').textContent = "Error generating voice code.";
    }
  })
  .catch(() => {
    document.getElementById('voiceStatusMessage').textContent = "Server error.";
  });
}

// کپی کردن کد تونل ویس
function copyVoiceCode() {
  const input = document.getElementById('voiceTunnelCode');
  input.select();
  document.execCommand("copy");
  document.getElementById('voiceStatusMessage').textContent = "Voice code copied!";
}

// ایجاد کد تونل پیام
function generateMessageCode() {
  fetch("http://localhost:5000/generate_message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId })
  })
  .then(res => res.json())
  .then(data => {
    if (data.code) {
      document.getElementById('messageTunnelCode').value = data.code;
      document.getElementById('messageStatusMessage').textContent = "Message tunnel code generated!";
    } else {
      document.getElementById('messageStatusMessage').textContent = "Error generating message code.";
    }
  })
  .catch(() => {
    document.getElementById('messageStatusMessage').textContent = "Server error.";
  });
}

// کپی کردن کد تونل پیام
function copyMessageCode() {
  const input = document.getElementById('messageTunnelCode');
  input.select();
  document.execCommand("copy");
  document.getElementById('messageStatusMessage').textContent = "Message code copied!";
}

// شروع چت
function startChat() {
  code = document.getElementById("codeInput").value.trim();
  if (!code) return alert("Enter a code");

  document.getElementById("chat").style.display = "block";
  document.getElementById("msgInput").style.display = "inline-block";
  document.querySelector("button[onclick='sendMessage()']").style.display = "inline-block";

  setInterval(fetchMessages, 2000);
}

// ارسال پیام
function sendMessage() {
  const msg = document.getElementById("msgInput").value.trim();
  if (!msg) return;
  document.getElementById("msgInput").value = "";

  fetch("http://localhost:5000/send_message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: code, message: msg, sender: "web" })
  });
}

// دریافت پیام‌های جدید
function fetchMessages() {
  fetch("http://localhost:5000/get_messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: code, last: lastMessageIndex })
  })
  .then(res => res.json())
  .then(data => {
    data.messages.forEach(m => {
      const div = document.createElement("div");
      div.textContent = `[${m.from}] ${m.content}`;
      div.setAttribute("data-sender", m.from);
      document.getElementById("chat").appendChild(div);
    });
    lastMessageIndex = data.new_last;
  });
}

// شروع تونل ویس
function startVoice() {
  const voiceCode = document.getElementById("voiceCodeInput").value.trim();
  if (!voiceCode) return alert("Enter a voice tunnel code");

  fetch("http://localhost:5000/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: voiceCode })
  })
  .then(res => res.json())
  .then(data => {
    if (data.valid && data.type === "voice") {
      document.getElementById("voiceConnectStatus").textContent = "Voice tunnel connected!";
      // بعداً اینجا میتونیم اتصال ویس واقعی رو هم انجام بدیم
    } else {
      document.getElementById("voiceConnectStatus").textContent = "Invalid voice tunnel code!";
    }
  })
  .catch(() => {
    document.getElementById("voiceConnectStatus").textContent = "Error connecting to server.";
  });
}
let voiceSocket;

function startVoiceStreaming() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const audioContext = new AudioContext();
      const input = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      input.connect(processor);
      processor.connect(audioContext.destination);

      voiceSocket = new WebSocket("ws://localhost:5001/voice");

      voiceSocket.onopen = () => {
        console.log("Voice WebSocket connected!");
      };

      processor.onaudioprocess = (e) => {
        if (voiceSocket.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          // فشرده‌سازی اولیه به آرایه بافر
          const buffer = new Float32Array(inputData.length);
          buffer.set(inputData);
          voiceSocket.send(buffer);
        }
      };
    })
    .catch(err => {
      console.error("Error accessing microphone:", err);
    });
}