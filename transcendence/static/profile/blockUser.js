async function fetchPage() {
  return fetch(OTHER_USER_PROFILE)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`fail to fetching ${OTHER_USER_PROFILE}`);
      }

      return response.text();
    })
    .catch((e) => {
      console.error(e);
    });
}

function parseHtml(htmlText) {
  return new DOMParser()
    .parseFromString(htmlText, "text/html")
    .body.querySelector("div#block-user-modal");
}

let blockModal;

const _blockModal = {
  get modal() {
    return blockModal;
  },

  open: async function (userNameElement, parentNode) {
    blockModal = parseHtml(await fetchPage());

    const paragraph = blockModal.querySelector("div.modal-content > p");

    (function () {
      const okButton = blockModal.querySelector("button#ok-button");
      const backButton = blockModal.querySelector("button#back-button");

      okButton.addEventListener("click", (event) => {
        event.preventDefault();
        const xhr = new XMLHttpRequest();

        xhr.open("POST", OTHER_USER_PROFILE);

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

    paragraph.textContent = eval(paragraph.textContent);

    parentNode.appendChild(_blockModal.modal);

    _blockModal.modal.style.display = "block";
  },

  close: function () {
    this.modal.remove();
  },
};
