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

    let receivedData = JSON.parse(event.data);
    const my_id = await ChatUpdater.getLoggedUserId();
    for(let [chat_id, users_ids] of Object.entries(receivedData.chat) ) {
        console.log(`chat: ${chat_id}`);
        console.log(users_ids)
        if (my_id in users_ids) {
            const response = await fetch('http://localhost:8000/auth/user_object/');
            const data = await response.json();
            other_user = data.user_object
            size = receivedData.chat[chat_id][my_id].length - 1
            addReceivedMessage(receivedData.chat[chat_id][my_id][size][USERNAME], other_user.username, receivedData.chat[chat_id][my_id][size][MESSAGE], other_user.avatar)
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
