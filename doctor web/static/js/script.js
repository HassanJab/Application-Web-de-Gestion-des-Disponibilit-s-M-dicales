const socket = io();

socket.on('background_notification', (data) => {
    alert(data.message);
});
