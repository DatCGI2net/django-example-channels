$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_url = ws_scheme + '://' + window.location.host + window.location.pathname;
    console.log('ws_url:', ws_url);
    var socket = new WebSocket(ws_url);
    
    socket.onopen = function open() {
      console.log('WebSockets connection created.');
    };

    socket.onmessage = function message(event) {
        console.log('on event:', event);
        var data = JSON.parse(event.data);
        console.log('on message:', data);
        if(data.message){
            
          var chat = $("#chat")
          var ele = $('<tr></tr>')
        
          ele.append(
              $("<td></td>").text(data.timestamp)
          )
          ele.append(
              $("<td></td>").text(data.room + ' - ' + data.owner)
          )
          ele.append(
              $("<td></td>").text(data.message)
          )
          
          chat.append(ele)
        }
        
    };
    socket.onclose = function(event){
        console.log('socket is closed');
    };
    
    if (socket.readyState == WebSocket.OPEN) {
      socket.onopen();
    }
    
    

    $('body').on('click', '#go', function(event) {
      event.preventDefault();
        var message_ele = $('#id_message');
        var message = {
            
            message: message_ele.val(),
        }
        console.log('sending message:', message);
        try{
          
          socket.send(JSON.stringify(message));
        }catch(e){
          console.log('sent error:', e.message);
        }
        message_ele.val('').focus();
        return false;
    });
});