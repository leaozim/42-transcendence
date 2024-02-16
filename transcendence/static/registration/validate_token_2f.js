function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  return match.length >= 3 ? match[2] : "";
}

function sendTOTPRequest() {
  const totpToken = document.getElementById("token").value;

  fetch(TOTP_LOGIN_URL + totpToken + "/", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      console.error(response);
      throw new Error("Erro na solicitação");
    })
    .then(() => {
      window.location.href = "http://localhost:8000/auth/user";
    })
    .catch((error) => {
      console.error("Erro:", error);
    });
}

const form = document.getElementById("testForm");

form.addEventListener("submit", () => {
  return sendTOTPRequest();
});
