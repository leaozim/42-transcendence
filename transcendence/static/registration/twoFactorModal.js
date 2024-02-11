function DisplayStyleEnum() {}

DisplayStyleEnum.BLOCK = "block";
DisplayStyleEnum.NONE = "none";

function TwoFactorModal() {
  this.modal = document.getElementById("two-factor-modal");

  Object.defineProperty(this, "totpCodeDiv", {
    get() {
      return this.modal.querySelector("div.two-factor-code");
    },

    set(qrcode_text) {
      const paragraphTag = document.createElement("p");

      paragraphTag.innerText = qrcode_text;

      this.totpCodeDiv.appendChild(paragraphTag);
    },
  });

  Object.defineProperty(this, "imgQRCodeDiv", {
    get() {
      return this.modal.querySelector("div.two-factor-qrcode-container");
    },

    set(qrcode) {
      const imgTag = document.createElement("img");

      imgTag.classList.add("two-factor-qrcode");
      imgTag.setAttribute("alt", "QR Code");
      imgTag.setAttribute("src", `data:image/png;base64,${qrcode}`);

      this.imgQRCodeDiv.appendChild(imgTag);
    },
  });

  Object.defineProperty(this, "displayStyle", {
    set(value) {
      this.modal.style.display = value;
    },
  });

  (function () {
    const okButton = document.getElementById("ok-button");
    const backButton = document.getElementById("back-button");
    const profileModal = document.getElementById("profile-modal");
    const slideInputTag = document.querySelector("label.switch > input");

    backButton.addEventListener("click", () => {
      this.removeQRCodeContent();
      slideInputTag.checked = false;
      profileModal.style.display = DisplayStyleEnum.BLOCK;
      this.displayStyle = DisplayStyleEnum.NONE;
    });

    okButton.addEventListener("click", () => {
      window.location.href = VALIDATE_TOKEN_URL;
    });
  }).call(this);
}

TwoFactorModal.prototype.removeQRCodeContent = function () {
  this.imgQRCodeDiv.querySelectorAll("img").forEach((element) => {
    element.remove();
  });
  this.totpCodeDiv.querySelectorAll("p").forEach((element) => {
    element.remove();
  });
};

TwoFactorModal.prototype.fetchQRCode = async function () {
  const response = await fetch(CREATE_TWO_FACTOR_URL);
  return response.json();
};

const twoFactorModal = new TwoFactorModal();

export default {
  get modal() {
    return twoFactorModal.modal;
  },

  open: async function () {
    const responseContent = await twoFactorModal.fetchQRCode();

    twoFactorModal.totpCodeDiv = responseContent.totp_code;
    twoFactorModal.imgQRCodeDiv = responseContent.qrcode;
    twoFactorModal.displayStyle = DisplayStyleEnum.BLOCK;
  },

  close: function () {
    twoFactorModal.removeQRCodeContent();
    twoFactorModal.displayStyle = DisplayStyleEnum.NONE;
  },
};
