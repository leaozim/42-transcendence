

var openModalButton = document.getElementById("tournament-button");
	openModalButton.addEventListener("click", function (e) {

	e.preventDefault()


	const xhr = new XMLHttpRequest();

        xhr.open("POST", "/create_tournament/");

        const form = new FormData(document.getElementById("create_tournament_form"));

        xhr.send(form);

        xhr.onreadystatechange = () => {
          if (xhr.readyState === 4) {
            if (xhr.status === 200) {
				console.log("player invited")
				/* MAYBE TODO: create to show the player was invited, maybe this
				is not necessary if notifications are working in chat channel
				or just show a message */
            } else {
              throw new Error(`${xhr.responseText}`);
            }
          }
        };


});
