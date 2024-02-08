const profileButton = document.getElementById("profile-button");
const profileModal = document.getElementById("profile-modal");
const inputSlide = document.querySelector("label.switch > input");
const twoFactorModal = document.getElementById("two-factor-modal");

const verifyTwoFactorState = () => {
  fetch(VERIFY_TWO_FACTOR_STATE_URL)
    .then((response) => {
      if (!response.ok) {
        throw new Error("fetching VERIFY_TWO_FACTOR_STATE_URL");
      }

      return response.status == 204 ? false : true;
    })
    .catch((e) => {
      console.log(e);
    });
};

profileButton.addEventListener("click", function () {
  inputSlide.checked = verifyTwoFactorState();
  profileModal.style.display = "block";
});

inputSlide.addEventListener("change", function () {
  if (this.checked) {
    profileModal.style.display = "none";
    createTwoFactorPage();
    setEventsTwoFactorPage();
    twoFactorModal.style.display = "block";
    // window.location.href = CREATE_TWO_FACTOR_URL;
  } else {
    fetch(DELETE_TWO_FACTOR_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Couldn't delete two factor");
        }
        return response.json();
      })
      .then((data) => {
        return data;
      })
      .catch((error) => {
        console.error(error);
      });
  }
});

window.addEventListener("click", function (event) {
  switch (event.target) {
    case profileModal:
      profileModal.style.display = "none";
      break;
    case twoFactorModal:
      twoFactorModal.style.display = "none";
      break;
    default:
      break;
  }
});

const setEventsTwoFactorPage = () => {
  const backButton = document.getElementById("back-button");
  const okButton = document.getElementById("ok-button");

  backButton.addEventListener("click", () => {
    const imgQRCode = twoFactorModal.querySelector("img.two-factor-qrcode");
    const totpCodeParagraph = twoFactorModal.querySelector(
      "div.two-factor-code > p",
    );
    imgQRCode.removeAttribute("src");
    totpCodeParagraph.remove();
    twoFactorModal.style.display = "none";
    inputSlide.checked = false;
    profileModal.style.display = "block";
  });

  okButton.addEventListener("click", () => {
    window.location.href = VALIDATE_TOKEN_URL;
  });
};

const createTwoFactorPage = () => {
  fetch(CREATE_TWO_FACTOR_URL)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`fetching ${CREATE_TWO_FACTOR_URL}`);
      }

      return response.json();
    })
    .then((data) => {
      const imgQRCode = twoFactorModal.querySelector("img.two-factor-qrcode");
      const totpParagraph = document.createElement("p");
      const totpCodeContainer = twoFactorModal.querySelector(
        "div.two-factor-code",
      );

      imgQRCode.setAttribute("src", `data:image/png;base64,${data.qrcode}`);

      totpParagraph.innerText = data.totp_code;

      totpCodeContainer.appendChild(totpParagraph);
    })
    .catch((e) => {
      console.error(e);
    });
};
