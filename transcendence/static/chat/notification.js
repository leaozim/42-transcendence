function alertOnMessage({ id: userId = undefined }) {
  let user;
  const alertSignal = document.getElementById("alerts-on-message-chat");

  if (typeof userId !== undefined) {
    user = document.querySelector(`li[data-user-id="${userId}"]`);
  }

  alertSignal.hidden = false;
}

function popAlert(userId = undefined) {
  let user;
  const alertSignal = document.getElementById("alerts-on-message-chat");

  if (typeof user !== undefined) {
    user = document.querySelector(`li[data-user-id="${userId}"]`);
  }

  alertSignal.hidden = true;
}
