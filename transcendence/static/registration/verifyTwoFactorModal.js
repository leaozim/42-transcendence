import DisplayStyleEnum from "./displayStyleEnum.js";

const fetchModalPageHTML = async function () {
  const response = await fetch(VALIDATE_TOKEN_URL);

  if (!response.ok) {
    throw new Error(`fetching ${VALIDATE_TOKEN_URL}`);
  }

  return response.text();
};

const parseModalHTML = function (html) {
  return new DOMParser().parseFromString(html, "text/html").body
    .firstElementChild;
};

export default {
  element: undefined,

  open: async function () {
    this.element = parseModalHTML(await fetchModalPageHTML());
    this.element.querySelector("div.modal-content").style.width = "350px";
    this.element.querySelector("div.modal-content").style.height = "450px";

    (function () {
      const formElement = this.element.querySelector("form#testForm");

      formElement.addEventListener("submit", () => {
        const tokenValue = this.element.querySelector("input#token").value;
        const requestURL = TOTP_LOGIN_URL + tokenValue + "/";
        const csrfToken = this.element.querySelector(
          "form#testForm > input",
        ).value;
        fetch(requestURL, {
          method: "POST",
          mode: "same-origin",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        })
          .then(async (response) => {
            if (!response.ok) {
              const responseContent = await response.json();
              console.error(responseContent.error);
            } else {
              this.close();
            }
          })
          .catch((e) => console.error(e));
      });
    }).call(this);

    document
      .getElementById("profile-modal")
      .parentElement.appendChild(this.element);

    this.element.style.display = DisplayStyleEnum.BLOCK;
  },

  close: function () {
    if (this.element) {
      this.element.remove();
    }
  },
};
