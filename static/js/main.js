function record_audio(){
  console.log("hello");
}
function switchToLive(){
    xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/switch_to_live", true);
    xhttp.send();
}
function switchToRecording(){
    xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/switch_to_recording", true);
    xhttp.send();
}