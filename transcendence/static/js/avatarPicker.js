// Shows the chosen image in the round preview next to an avatar file input
// (<div class="avatar-picker"> with <img data-avatar-preview> and <input type="file">).
document.querySelectorAll(".avatar-picker").forEach((picker) => {
  const input = picker.querySelector("input[type=file]");
  const preview = picker.querySelector("img[data-avatar-preview]");
  const originalSrc = preview.src;
  let objectUrl = null;

  input.addEventListener("change", () => {
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
      objectUrl = null;
    }
    const file = input.files[0];
    if (file && file.type.startsWith("image/")) {
      objectUrl = URL.createObjectURL(file);
      preview.src = objectUrl;
    } else {
      preview.src = originalSrc;
    }
  });
});
