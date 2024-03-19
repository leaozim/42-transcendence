chatSocketUpdate = new WebSocket(
    'ws://' + 
    window.location.hostname + 
    ':' + 
    window.location.port + 
    '/ws/chat_update/'
);		

chatSocketUpdate.onopen = (event) => {
    console.log("CONNECTED TO UPDATE CHAT");

};

chatSocketUpdate.onmessage = async (event) => {
    console.log("CONNECTED TO ONMESSAGE CHAT");
    // console.log(event.data)

    let receivedData = JSON.parse(event.data);

    console.log(receivedData)
    for(let [chat, user_id] of Object.entries(receivedData.chat) ) {
        // console.log(  " aaaaaaaaaaaaaaaaaaaaaaaaaa = ", await ChatUpdater.getLoggedUserId())
        // console.log( " aaaaaaaaaaaaaaaaaaaaaaaaaa = ", user_id)
        // console.log( " aaaaaaaaaaaaaaaaaaaaaaaaaa = ", await ChatUpdater.getLoggedUserId() in user_id)

        if (await ChatUpdater.getLoggedUserId() in user_id){
            console.log(user_id)

        }
        
    }

    // if (senderUserData !== null && senderUserData !== undefined) {
    //     const receivingUserData = receivedData.data_receiving_user;
    //     ChatUpdater.renderUpdatedUser(senderUserData, receivingUserData);
    // }
};

chatSocketUpdate.onclose = function(e){
    console.log("DISCONNECTED FROM UPDATE CHAT", e);
}
