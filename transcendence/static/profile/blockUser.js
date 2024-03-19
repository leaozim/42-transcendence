async function fetchPage(url, username = "") {
  return fetch(url + `${username}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`fail to fetching ${url}`);
      }

      return response.text();
    })
    .catch((e) => {
      console.error(e);
    });
}

function parseHtml(htmlText, elementSelector) {
  return new DOMParser()
    .parseFromString(htmlText, "text/html")
    .body.querySelector(elementSelector);
}

let blockModal;

const _blockModal = {
  get modal() {
    return blockModal;
  },

  open: async function (userNameElement, parentNode) {
    blockModal = parseHtml(
      await fetchPage(BLOCK_USER_URL, userNameElement),
      "div#block-user-modal",
    );

    (function () {
      const okButton = blockModal.querySelector("button#ok-button");
      const backButton = blockModal.querySelector("button#back-button");

      okButton.addEventListener("click", (event) => {
        event.preventDefault();
        const xhr = new XMLHttpRequest();

        xhr.open("POST", BLOCK_USER_URL);

        const form = new FormData(this.modal.querySelector("form#block-form"));

        form.set("blockedUserName", userNameElement);

        xhr.send(form);

        xhr.onreadystatechange = () => {
          if (xhr.readyState === 4) {
            if (xhr.status === 200) {
              this.close();
            } else {
              throw new Error(`${xhr.responseText}`);
            }
          }
        };
      });

      backButton.addEventListener("click", () => this.close());
    }).call(this);

    parentNode.appendChild(_blockModal.modal);

    _blockModal.modal.style.display = "block";
  },

  close: function () {
    this.modal.remove();
  },
};
