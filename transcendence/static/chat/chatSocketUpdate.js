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
    console.log("CONNECTED TO UPDATE CHAT");

    const receivedData = JSON.parse(event.data);
    const senderUserData = receivedData.data_sender_user;

    // if (senderUserData !== null && senderUserData !== undefined) {
    //     const receivingUserData = receivedData.data_receiving_user;
    //     ChatUpdater.renderUpdatedUser(senderUserData, receivingUserData);
    // }
};

chatSocketUpdate.onclose = function(e){
    console.log("DISCONNECTED FROM UPDATE CHAT");
}
