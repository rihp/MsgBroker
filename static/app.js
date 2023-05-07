const subscribeButton = document.getElementById("subscribe");
const publishButton = document.getElementById("publish");
const channelInput = document.getElementById("channel");
const messageInput = document.getElementById("message");
const messagesContainer = document.getElementById("messages");

subscribeButton.addEventListener("click", async () => {
  const channel = channelInput.value;
  const response = await fetch("/subscribe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel }),
  });
  const data = await response.json();
  console.log(data);
});

publishButton.addEventListener("click", async () => {
  const channel = channelInput.value;
  const message = messageInput.value;
  const response = await fetch("/publish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel, message }),
  });
  const data = await response.json();
  console.log(data);
});

let lastSeenMessageId = -1;
let isFetchingMessages = false;

async function fetchMessages() {
  if (isFetchingMessages) {
    return;
  }

  isFetchingMessages = true;
  const channel = channelInput.value;
  const response = await fetch("/fetch_messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel, last_seen_message_id: lastSeenMessageId }),
  });
  const data = await response.json();


  data.messages.forEach((message) => {
    const messageElement = document.createElement("div");
    messageElement.textContent = `[${message.channel}] [${message.id}] ${message.message}`;
    messagesContainer.appendChild(messageElement);
    lastSeenMessageId = message.id;
  });

  isFetchingMessages = false;
}

// Fetch messages every 3 seconds
setInterval(fetchMessages, 1000);

document.querySelector("#fetch-messages").addEventListener("click", async () => {
    console.log("Fetch messages button clicked"); // Add this line
    await fetchMessages();
  });
  

const Channels = {
    COMMANDS: "commands",
    ALL: "all",
    PROGRESS: "progress",
    MEMORIES: "memories",
    USER_INPUTS: "user_inputs",
    OBJECTIVES_PROMPTS: "objectives_prompts",
    AI_INPUTS: "ai_inputs",
    OUTPUTS: "outputs",
};

const publishCommandButton = document.getElementById("publish-command");

publishCommandButton.addEventListener("click", async () => {
const commandMessage = "Your command message here";
const response = await fetch("/publish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ channel: Channels.COMMANDS, message: commandMessage }),
});
const data = await response.json();
console.log(data);
});
