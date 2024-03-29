const MessageType = {
  sent: "sent-message",
  received: "received-message",
};

function createMessageHtml(
  messageType,
  message,
  isLastMessage = false,
  userPictureElement = "",
) {
  const pClass = isLastMessage ? 'class="special-style"' : "";

  return `<div class=${messageType}>${userPictureElement}<p ${pClass}>${makeLinksClickable(message)}</p></div>`;
}

function initializeChatLog(current_user, messages) {
  const chatLog = document.querySelector("div#chat-log");
  let senderAvatar, senderName;

  clearChatLog();

  messages.forEach((item, index) => {
    const isCurrentUser = item.user === current_user;

    if (!isCurrentUser) {
      senderAvatar = item.avatar;
      senderName = item.user;
    }

    chatLog.innerHTML += `<div>${createMessageHtml(
      isCurrentUser ? MessageType.sent : MessageType.received,
      item.content,
      messages.length - 1 === index,
    )}</div>`;
  });

  const receivedMessages = chatLog.querySelectorAll("div.received-message");

  if (receivedMessages.length) {
    receivedMessages[receivedMessages.length - 1].insertAdjacentHTML(
      "afterbegin",
      `<div class="user-photo"><img src="${senderAvatar}" alt="${senderName}"></div>`,
    );
  }
}

function makeLinksClickable(message) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const messageWithClickableLinks = message.replace(
    urlRegex,
    '<a href="$1" target="_blank" style="color: black;">$1</a>',
  );
  return messageWithClickableLinks;
}
