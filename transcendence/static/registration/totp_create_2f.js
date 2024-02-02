const backButton = document.getElementById("back-button");
const okButton = document.getElementById("ok-button");

backButton.addEventListener("click", () => {
  history.back();
});

okButton.addEventListener("click", () => {
  window.location.href = VALIDATE_TOKEN_URL;
});
