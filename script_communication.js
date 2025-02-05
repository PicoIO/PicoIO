if (conf['communication']['UDP']['enabled'] == '1'){
    document.getElementById('udp').checked = "checked";
}
else{
    document.getElementById('udp').checked = "";
}

document.getElementById('udp_ip').value = conf['communication']['UDP']['ip'];
document.getElementById('udp_port').value = conf['communication']['UDP']['port'];

udp();

document.getElementById('udp').addEventListener("click", () => {
    udp();
})

function udp(){
    if (document.getElementById('udp').checked){
        document.getElementById('udp_ip').disabled = '';
        document.getElementById('udp_port').disabled = '';
    }
    else{
        document.getElementById('udp_ip').disabled = 'True';
        document.getElementById('udp_port').disabled = 'True';
    }
}