import twoFactorModal from "../registration/twoFactorModal.js";

const profileButton = document.getElementById("profile-button");
const profileModal = document.getElementById("profile-modal");
const inputSlide = document.querySelector("label.switch > input");

window.addEventListener("click", function (event) {
  switch (event.target) {
    case profileModal:
      profileModal.style.display = "none";
      break;
    case twoFactorModal.modal:
      twoFactorModal.close();
      break;
    default:
      break;
  }
});

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
    twoFactorModal.open();
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
