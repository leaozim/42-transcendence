import DisplayStyleEnum from "./displayStyleEnum.js";

async function getCookie(name) {
  const result = await window.cookieStore.get(name);

  return result.value;
}

export default {
  element: document.getElementById("verify-two-factor-modal"),

  open: async function () {
    this.element.querySelector("div.modal-content").style.width = "350px";
    this.element.querySelector("div.modal-content").style.height = "450px";

    (function () {
      const formElement = this.element.querySelector("form#testForm");

      formElement.addEventListener("submit", async () => {
        const tokenValue = this.element.querySelector("input#token").value;
        const requestURL = TOTP_LOGIN_URL + tokenValue + "/";
        fetch(requestURL, {
          method: "POST",
          mode: "same-origin",
          headers: {
            "X-CSRFToken": await getCookie("csrftoken"),
          },
        })
          .then((response) => {
            return response.json();
          })
          .then((data) => {
            if (!data.success) {
              throw new Error("Invalid Token");
            } else {
              if (window.location.href.search(VALIDATE_TOKEN_URL) > -1) {
                window.location.href = window.location.href.replace(
                  VALIDATE_TOKEN_URL,
                  "",
                );
              } else {
                this.close();
              }
            }
          })
          .catch((e) => console.error(e));
      });
    }).call(this);

    this.element.style.display = DisplayStyleEnum.BLOCK;
  },

  close: function () {
    this.element.style.display = DisplayStyleEnum.NONE;
  },
};
