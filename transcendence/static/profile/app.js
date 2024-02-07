const profileButton = document.getElementById("profile-button");
const profileModal = document.getElementById("profile-modal");
const inputSlide = document.querySelector("label.switch > input");

profileButton.addEventListener("click", function () {
  fetch(VERIFY_TWO_FACTOR_STATE_URL)
    .then((response) => {
      if (!response.ok) {
        throw new Error("fetching VERIFY_TWO_FACTOR_STATE_URL");
      } else {
        inputSlide.checked = response.status == 204 ? false : true;
      }
    })
    .catch((e) => {
      console.log(e);
    });

  profileModal.style.display = "block";
});

inputSlide.addEventListener("change", function () {
  if (this.checked) {
    window.location.href = CREATE_TWO_FACTOR_URL;
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
  if (event.target == profileModal) {
    profileModal.style.display = "none";
  }
});
