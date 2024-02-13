import twoFactorModal from "../registration/twoFactorModal.js";

const profileButton = document.getElementById("profile-button");
const profileModal = document.getElementById("profile-modal");
const inputSlide = document.querySelector("label.switch > input");

window.addEventListener("click", function (event) {
  if (event.target == profileModal) {
    profileModal.style.display = "none";
  }
});

const verifyTwoFactorState = () => {
  return fetch(VERIFY_TWO_FACTOR_STATE_URL)
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

profileButton.addEventListener("click", async function () {
  inputSlide.checked = await verifyTwoFactorState();
  profileModal.style.display = "block";
});

inputSlide.addEventListener("change", async function () {
  if (this.checked) {
    profileModal.style.display = "none";
    twoFactorModal.open();
  } else {
    const response = await fetch(DELETE_TWO_FACTOR_URL);
    console.log(await response.json());
    // fetch(DELETE_TWO_FACTOR_URL)
    //   .then((response) => {
    //     if (!response.ok) {
    //       throw new Error("Couldn't delete two factor");
    //     }
    //     return response.json();
    //   })
    //   .catch((error) => {
    //     console.error(error);
    //   });
  }
});
