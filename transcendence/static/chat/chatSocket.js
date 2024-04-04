async function setupWebSocket(roomId) {
  const response = await fetch("/user/");
  const { id: user_id } = await response.json();
  const base_url = `wss://${window.location.host}/ws/chat/${roomId}/${user_id}`;
  const chatSocket = new WebSocket(base_url);

  chatSocket.onmessage = (event) => {
    addReceivedMessage(JSON.parse(event.data));
  };

  sockets.add(chatSocket);
}

function addReceivedMessage(data) {
  const chatLog = document.getElementById("chat-log");

  const getLastReceivedMessage = () => {
    const receivedsMessages = chatLog.querySelectorAll("div.received-message");
    return receivedsMessages[receivedsMessages.length - 1];
  };

  let lastMessage = getLastReceivedMessage();

  const resetLastMessage = () => {
    const userPictureDiv = lastMessage.querySelector("img.user-photo");
    const lastMessageParagraph = lastMessage.querySelector("p.special-style");

    if (lastMessageParagraph) {
      lastMessageParagraph.classList.remove("special-style");
    }
    if (userPictureDiv) {
      userPictureDiv.remove();
    }
  };

  const userPictureElement = `
    <div class="user-photo">
      <img src="${data.avatar}" alt="${data.username}">
    </div>
  `;

  const messageHtml = createMessageHtml(
    MessageType.received,
    data.message,
    true,
    userPictureElement,
  );

  resetLastMessage();

  chatLog.insertAdjacentHTML("beforeend", messageHtml);

  lastMessage = getLastReceivedMessage();
  lastMessage.scrollIntoView({
    behavior: "smooth",
    block: "end",
    inline: "nearest",
  });
}
