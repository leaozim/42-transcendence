import DisplayStyleEnum from "./displayStyleEnum.js";
import verifyTwoFactorModal from "./verifyTwoFactorModal.js";

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
    twoFactorModalContent.style.minHeight = "700px";
  }).call(this);

  (function () {
    const okButton = document.getElementById("ok-button");
    const backButton = document.getElementById("back-button");
    const cancelButton = document.getElementById("cancel-two-factor-button");
    const profileModal = document.getElementById("profile-modal");
    const slideInputTag = document.querySelector("label.switch > input");

    // Step 1: choosing an app creates (or reuses) the TOTP secret and shows it.
    this.modal.querySelectorAll("button[data-app]").forEach((button) => {
      button.addEventListener("click", () => this.showApp(button.dataset.app));
    });

    // Leaving without finishing the setup: back to the profile, switch off.
    cancelButton.addEventListener("click", () => {
      this.close();
      slideInputTag.checked = false;
      profileModal.style.display = DisplayStyleEnum.BLOCK;
    });

    // Step 2 "back" returns to the app choice.
    backButton.addEventListener("click", () => {
      this.removeQRCodeContent();
      this.showStep("choose-app");
    });

    okButton.addEventListener("click", () => {
      this.close();
      verifyTwoFactorModal.open();
    });
  }).call(this);
}

TwoFactorModal.prototype.showStep = function (step) {
  this.modal.querySelectorAll("[data-step]").forEach((element) => {
    element.hidden = element.dataset.step !== step;
  });
};

TwoFactorModal.prototype.showApp = async function (app) {
  const responseContent = await this.fetchQRCode(app);

  this.removeQRCodeContent();
  this.modal.querySelectorAll(".two-factor-instructions").forEach((element) => {
    element.hidden = element.dataset.app !== app;
  });
  this.totpCodeDiv = responseContent.totp_code;
  this.imgQRCodeDiv = responseContent.qrcode;
  this.showStep("scan");
};

TwoFactorModal.prototype.removeQRCodeContent = function () {
  this.imgQRCodeDiv.querySelectorAll("img").forEach((element) => {
    element.remove();
  });
  this.totpCodeDiv.querySelectorAll("p").forEach((element) => {
    element.remove();
  });
};

TwoFactorModal.prototype.fetchQRCode = async function (app) {
  const url = `${CREATE_TWO_FACTOR_URL}?app=${encodeURIComponent(app)}`;
  const response = await fetch(url);
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
  } else if (event.target == verifyTwoFactorModal.element) {
    verifyTwoFactorModal.close();
  }
});

export default {
  open: function () {
    twoFactorModal.removeQRCodeContent();
    twoFactorModal.showStep("choose-app");
    twoFactorModal.displayStyle = DisplayStyleEnum.BLOCK;
  },
};
