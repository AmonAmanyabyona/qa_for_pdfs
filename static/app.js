const chatToggle = document.getElementById('chatToggle');
const chatWidget = document.getElementById('chatWidget');
const closeChat = document.getElementById('closeChat');
const pdfInput = document.getElementById('pdfInput');
const uploadStatus = document.getElementById('uploadStatus');
const uploadProgress = document.getElementById('uploadProgress');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// Toggle widget open/close
chatToggle.addEventListener('click', () => {
  chatWidget.classList.toggle('open');
});

closeChat.addEventListener('click', () => {
  chatWidget.classList.remove('open');
});

// Add a message bubble to the chat
function addMessage(text, sender) {
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const msg = document.createElement('div');
  msg.classList.add('msg', sender);
  msg.innerHTML = `<div>${text}</div><div class="time">${now}</div>`;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle PDF upload
pdfInput.addEventListener('change', async () => {
  const file = pdfInput.files[0];
  if (!file) return;

  uploadStatus.textContent = `Uploading ${file.name}...`;
  uploadProgress.textContent = '⏳ Processing PDF, please wait...';

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (res.ok) {
      uploadStatus.textContent = `✅ ${file.name}`;
      uploadProgress.textContent = 'Ready to chat!';
      userInput.disabled = false;
      sendBtn.disabled = false;
      addMessage("👋 Hi! I've read your document. Ask me anything about it!", 'bot');
    } else {
      uploadStatus.textContent = 'Upload failed';
      uploadProgress.textContent = data.detail || 'Unknown error';
    }
  } catch (err) {
    uploadStatus.textContent = 'Error uploading file';
    uploadProgress.textContent = err.message;
  }
});

// Send message
async function sendMessage() {
  const question = userInput.value.trim();
  if (!question) return;

  addMessage(question, 'user');
  userInput.value = '';
  sendBtn.disabled = true;
  userInput.disabled = true;

  // Typing indicator
  const typing = document.createElement('div');
  typing.classList.add('msg', 'bot');
  typing.id = 'typing';
  typing.textContent = '...';
  chatMessages.appendChild(typing);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    typing.remove();

    if (res.ok) {
      addMessage(data.answer, 'bot');
    } else {
      addMessage('Sorry, something went wrong.', 'bot');
    }
  } catch (err) {
    typing.remove();
    addMessage('Connection error. Is the server running?', 'bot');
  } finally {
    sendBtn.disabled = false;
    userInput.disabled = false;
    userInput.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMessage();
});