function alertOnMessage({ id: userId = undefined }) {
  let user;
  const alertSignal = document.getElementById("alerts-on-message-chat");
  const chatModal = document.getElementById("chat-modal");

  if (typeof userId !== "undefined") {
    user = document.querySelector(`li[data-user-id="${userId}"]`);
    const selected = user.classList.contains("selected");
    if (!selected) {
      user.querySelector(`span#alert-message-${userId}`).hidden = false;
    }
  }

  if (chatModal.style.display !== "block") {
    alertSignal.hidden = false;
  }
}

function popAlert(userId = undefined) {
  let user;
  const alertSignalInHome = document.getElementById("alerts-on-message-chat");

  if (typeof userId !== "undefined") {
    user = document.querySelector(`li[data-user-id="${userId}"]`);
    user.querySelector(`span#alert-message-${userId}`).hidden = true;
  }

  alertSignalInHome.hidden = true;
}
