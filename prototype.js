const form = document.querySelector('#chat-form');
const input = document.querySelector('#message-input');
const sendButton = document.querySelector('#send-button');
const resetButton = document.querySelector('#reset-button');
const historyElement = document.querySelector('#chat-history');
const errorBanner = document.querySelector('#error-banner');
const modeBadge = document.querySelector('#mode-badge');
const suggestedQuestions = document.querySelectorAll('.suggested-question');

const initialAssistantText = "Hello! I'm your Pharmacy Patient Assistant. I can help with general questions about medicines and their use. What would you like to know? Demonstration mode is active, so I am not consulting a real medication knowledge base. Please do not use a simulated response to make a treatment decision.";
let conversation = [];

function addMessage(role, text, meta = '', state = '') {
  const row = document.createElement('div');
  row.className = `message-row ${role} ${state}`.trim();
  const avatar = document.createElement('span');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? 'YOU' : 'AI';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  const paragraph = document.createElement('p');
  paragraph.textContent = text;
  bubble.appendChild(paragraph);
  if (meta) {
    const metadata = document.createElement('small');
    metadata.className = 'message-meta';
    metadata.textContent = meta;
    bubble.appendChild(metadata);
  }
  row.append(avatar, bubble);
  historyElement.appendChild(row);
  historyElement.scrollTop = historyElement.scrollHeight;
  return row;
}

function resetConversation() {
  conversation = [];
  historyElement.replaceChildren();
  addMessage('assistant', initialAssistantText, 'DEMONSTRATION MODE · NO SOURCE LOOKUP');
  errorBanner.hidden = true;
  input.focus();
}

async function loadMode() {
  try {
    const response = await fetch('/health');
    const data = await response.json();
    modeBadge.textContent = data.provider_mode === 'cloudflare' ? 'Hosted mode configured' : 'Demonstration mode';
  } catch {
    modeBadge.textContent = 'Mode unavailable';
  }
}

function responseMeta(data) {
  if (data.category === 'emergency') return 'EMERGENCY GUIDANCE · NO MODEL REQUEST MADE';
  if (data.category === 'pharmacist') return 'PHARMACIST REVIEW NEEDED · NO MODEL REQUEST MADE';
  if (data.category === 'out_of_scope') return 'OUTSIDE PROTOTYPE SCOPE · NO MODEL REQUEST MADE';
  if (data.simulated) return 'SIMULATED RESPONSE · NO SOURCE LOOKUP';
  return data.source?.label || 'HOSTED RESPONSE · NO SOURCE LOOKUP IN MILESTONE 1';
}

function responseState(data) {
  if (data.category === 'emergency' || data.category === 'pharmacist' || data.category === 'out_of_scope') return data.category;
  return data.status;
}

suggestedQuestions.forEach((button) => {
  button.addEventListener('click', () => {
    input.value = button.dataset.question || '';
    input.focus();
  });
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || sendButton.disabled) return;

  errorBanner.hidden = true;
  addMessage('user', message);
  conversation.push({ role: 'user', content: message });
  input.value = '';
  sendButton.disabled = true;
  const loadingRow = addMessage('assistant', 'Checking the safety boundaries, then contacting the configured provider…', 'WORKING', 'loading');

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history: conversation.slice(-20) }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error('The backend rejected this request. Please enter a shorter, non-empty question.');
    loadingRow.remove();
    const assistantRow = addMessage('assistant', data.message, responseMeta(data), responseState(data));
    if (data.source?.url) {
      const sourceLink = document.createElement('a');
      sourceLink.href = data.source.url;
      sourceLink.target = '_blank';
      sourceLink.rel = 'noreferrer';
      sourceLink.textContent = `Source: ${data.source.label}`;
      sourceLink.className = 'message-meta';
      assistantRow.querySelector('.bubble').appendChild(sourceLink);
    }
    conversation.push({ role: 'assistant', content: data.message });
  } catch (error) {
    loadingRow.remove();
    const isNetworkError = error instanceof TypeError;
    const errorMessage = isNetworkError ? 'The prototype could not reach its backend. No medication information was generated.' : error.message;
    addMessage('assistant', errorMessage, 'ERROR', 'error');
    errorBanner.textContent = isNetworkError ? 'Connection error. Check that the FastAPI server is running.' : errorMessage;
    errorBanner.hidden = false;
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

resetButton.addEventListener('click', resetConversation);
resetConversation();
loadMode();
