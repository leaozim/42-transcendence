import DisplayStyleEnum from "./displayStyleEnum.js";
import verifyModal from "./verifyTwoFactorModal.js";

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
    const twoFactorModalContent = this.modal.querySelector("div.modal-content");
    twoFactorModalContent.style.width = "450px";
    twoFactorModalContent.style.height = "700px";
  }).call(this);

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
      this.close();
      verifyModal.open();
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

TwoFactorModal.prototype.close = function () {
  this.removeQRCodeContent();
  this.displayStyle = DisplayStyleEnum.NONE;
};

const twoFactorModal = new TwoFactorModal();

window.addEventListener("click", (event) => {
  if (event.target == twoFactorModal.modal) {
    twoFactorModal.close();
  } else if (verifyModal.element && event.target == verifyModal.element) {
    verifyModal.close();
  }
});

export default {
  open: async function () {
    const responseContent = await twoFactorModal.fetchQRCode();

    twoFactorModal.totpCodeDiv = responseContent.totp_code;
    twoFactorModal.imgQRCodeDiv = responseContent.qrcode;
    twoFactorModal.displayStyle = DisplayStyleEnum.BLOCK;
  },
};
