 $(document).ready(function() {
     // Display Speak Message
     eel.expose(DisplayMessage)

     function DisplayMessage(message) {
         // Replace the hidden textillate <li>
         $(".siri-message .texts li").text(message);

         // Re-initialize textillate so it splits into chars again
         $('.siri-message').textillate('start');
     }

     // Display hood
     eel.expose(ShowHood)

     function ShowHood() {
         $("#Oval").attr("hidden", false);
         $("#SiriWave").attr("hidden", true);
     }
 });