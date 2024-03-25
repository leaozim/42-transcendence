function initializeChatLog(current_user, messages) {
  let lastUser = "";
  const chatLog = document.querySelector("div#chat-log");

  messages.forEach((item) => {
    const isCurrentUser = item.user === current_user;
    const isUserChange = lastUser !== item.user || lastUser === "";
    const clickableMessage = makeLinksClickable(item.content);
    chatLog.innerHTML += `
			<div> 
				${
          isCurrentUser
            ? `
						<div class="sent-message">
							<p class="${isUserChange ? "special-style" : ""}">${clickableMessage}</p>
						</div>
					`
            : `
						<div class="received-message">
						  <div class="user-photo">
							${
                isUserChange
                  ? `<img src="${item.avatar}" alt="${item.user}" >`
                  : "<div></div>"
              }
						  </div>
						  <p class="${isUserChange ? "special-style" : ""}">${clickableMessage}</p>
						</div>
					`
        }
			</div>
		`;
    lastUser = item.user;
  });
}

function makeLinksClickable(message) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const messageWithClickableLinks = message.replace(
    urlRegex,
    '<a href="$1" target="_blank" style="color: black;">$1</a>',
  );
  return messageWithClickableLinks;
}

