import DisplayStyleEnum from "./displayStyleEnum.js";

// document.cookie works in every browser (window.cookieStore is Chromium-only).
function getCookie(name) {
  const prefix = `${name}=`;
  const cookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(prefix));

  return cookie ? decodeURIComponent(cookie.substring(prefix.length)) : "";
}

export default {
  element: document.getElementById("verify-two-factor-modal"),
  listening: false,

  showError: function (message) {
    const errorElement = this.element.querySelector("[data-role='error']");
    errorElement.textContent = message || "";
    errorElement.hidden = !message;
  },

  submit: async function () {
    const tokenInput = this.element.querySelector("input#token");
    const tokenValue = tokenInput.value.replace(/\s/g, "");

    this.showError("");
    if (!/^\d{6}$/.test(tokenValue)) {
      this.showError(this.element.dataset.invalidFormatMessage);
      return;
    }

    try {
      const response = await fetch(TOTP_LOGIN_URL + tokenValue + "/", {
        method: "POST",
        mode: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });
      const data = await response.json();

      if (!data.success) {
        throw new Error("Invalid Token");
      }
    } catch (e) {
      console.error(e);
      tokenInput.value = "";
      this.showError(this.element.dataset.invalidCodeMessage);
      return;
    }

    if (window.location.href.search(VALIDATE_TOKEN_URL) > -1) {
      window.location.href = window.location.href.replace(VALIDATE_TOKEN_URL, "");
    } else {
      this.close();
    }
  },

  open: function () {
    this.element.querySelector("div.modal-content").style.width = "350px";
    this.element.querySelector("div.modal-content").style.minHeight = "450px";

    if (!this.listening) {
      this.listening = true;
      this.element
        .querySelector("form#testForm")
        .addEventListener("submit", (event) => {
          event.preventDefault();
          this.submit();
        });
    }

    this.showError("");
    this.element.querySelector("input#token").value = "";
    this.element.style.display = DisplayStyleEnum.BLOCK;
  },

  close: function () {
    this.element.style.display = DisplayStyleEnum.NONE;
  },
};
