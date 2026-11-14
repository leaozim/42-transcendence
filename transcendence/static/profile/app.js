import twoFactorModal from "../registration/twoFactorModal.js";

const profileButton = document.getElementById("profile-button");
const profileModal = document.getElementById("profile-modal");
const inputSlide = document.querySelector("label.switch > input");

window.addEventListener("click", function (event) {
  if (event.target == profileModal) {
    profileModal.style.display = "none";
  }
});

const verifyTwoFactorState = async () => {
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
  }
});

// Avatar upload: sends the chosen image right away and refreshes every picture
// of the current user on the page (the centre of the main circle included).
const avatarForm = document.getElementById("avatar-form");
const avatarInput = document.getElementById("avatar-input");
const avatarStatus = avatarForm.querySelector("[data-role='avatar-status']");

function setAvatarStatus(message, isError = false) {
  avatarStatus.textContent = message;
  avatarStatus.classList.toggle("error", isError);
}

avatarInput.addEventListener("change", async () => {
  if (!avatarInput.files.length) {
    return;
  }
  setAvatarStatus(avatarForm.dataset.uploadingMessage);

  try {
    // FormData includes the csrfmiddlewaretoken field of the form.
    const response = await fetch(avatarForm.action, {
      method: "POST",
      mode: "same-origin",
      body: new FormData(avatarForm),
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.avatar) {
      throw new Error(data.error || avatarForm.dataset.errorMessage);
    }
    document.querySelectorAll("img[data-user-avatar]").forEach((img) => {
      img.src = data.avatar;
    });
    setAvatarStatus(avatarForm.dataset.successMessage);
  } catch (e) {
    setAvatarStatus(e.message || avatarForm.dataset.errorMessage, true);
  } finally {
    avatarInput.value = "";
  }
});
