if (conf['network']['type'] == 'static'){
    document.getElementById('net_method').selectedIndex = '1';
    document.getElementById('ipaddress').value = conf['network']['ip'];
    document.getElementById('netmask').value = conf['network']['netmask'];
    document.getElementById('gateway').value = conf['network']['gateway'];
    document.getElementById('dns').value = conf['network']['dns'];
}

if (conf['network']["wifi"]){
    var new_tr9 = document.createElement("tr");
    var new_td17 = document.createElement("td");

    var new_header2 = document.createElement("h3");
    new_header2.innerText = "Wi-Fi";
    new_td17.appendChild(new_header2);

    var new_td20 = document.createElement("td");
    var new_button4 = document.createElement("button");
    new_button4.type = "button";
    new_button4.innerText = "Scan";

    new_tr9.appendChild(new_td17);
    new_td20.appendChild(new_button4);
    new_tr9.appendChild(new_td20);
    document.getElementById("net_config").appendChild(new_tr9);

    var new_tr13 = document.createElement("tr");
    new_tr13.id = "for_wifi_scan";
    new_tr13.style.visibility = "hidden";
    var new_td21 = document.createElement("td");
    new_td21.id = "wifi_scan"
    new_td21.colSpan = "2";
    new_tr13.appendChild(new_td21);
    document.getElementById("net_config").appendChild(new_tr13);

    new_button4.addEventListener("click", () => {
        document.getElementById("for_wifi_scan").style.visibility = "";
        document.getElementById("wifi_scan").innerHTML = "";

        var new_table2 = document.createElement("table");
        var new_tr11 = document.createElement("tr");
        var new_th5 = document.createElement("th");
        new_tr11.appendChild(new_th5);

        var new_th4 = document.createElement("th");
        new_th4.innerText = "SSID";
        new_tr11.appendChild(new_th4);

        var new_th5 = document.createElement("th");
        new_th5.innerText = "RSSI";
        new_tr11.appendChild(new_th5);

        var new_th6 = document.createElement("th");
        new_th6.innerText = "Security";
        new_tr11.appendChild(new_th5);

        new_table2.appendChild(new_tr11);

        fetch('/wifi_scan')
            .then(response => response.json())
            .then(response => scan_wifi(response, new_table2))

        new_td21.appendChild(new_table2);
    })

    var new_tr8 = document.createElement("tr");
    var new_td15 = document.createElement("td");
    var new_td16 = document.createElement("td");
    var new_label8 = document.createElement("label");
    new_label8.innerText = "SSID"
    var new_input6 = document.createElement("input");
    new_input6.type = "text";
    new_input6.name = "ssid";
    new_input6.value = conf['network']['wifi']['ssid'];

    new_td15.appendChild(new_label8);
    new_td16.appendChild(new_input6);
    new_tr8.appendChild(new_td15);
    new_tr8.appendChild(new_td16);

    document.getElementById("net_config").appendChild(new_tr8);

    var new_tr10 = document.createElement("tr");
    var new_td18 = document.createElement("td");
    var new_label9 = document.createElement("label");
    new_label9.innerText = "Password";
    var new_td19 = document.createElement("td");
    var new_input7 = document.createElement("input");
    new_input7.type = "password";
    new_input7.name = "wifi_password";
    new_input7.value = conf['network']['wifi']['password'];

    new_td18.appendChild(new_label9);
    new_td19.appendChild(new_input7);
    new_tr10.appendChild(new_td18);
    new_tr10.appendChild(new_td19);

    document.getElementById("net_config").appendChild(new_tr10);
}
net_method();

document.getElementById("net_method").addEventListener("change", () => {
    net_method();
})

function scan_wifi(res, tb){
    document.getElementsByName("ssid")[0].value = conf['network']['wifi']['ssid'];
    for (let item in res){
        var new_tr14 = document.createElement("tr");
        var new_td22 = document.createElement("td");
        var new_input8 = document.createElement("input");
        new_input8.type = "radio";
        new_input8.name = "sel_wifi";
        if (res[item]['ssid'] == conf['network']['wifi']['ssid']){
            new_input8.checked = "checked";
        }
        new_td22.appendChild(new_input8);
        new_tr14.appendChild(new_td22);

        new_input8.addEventListener("click", () => {
            document.getElementsByName("ssid")[0].value = res[item]['ssid'];
        })

        var new_td23 = document.createElement("td");
        var new_label10 = document.createElement("label");
        new_label10.innerText = res[item]['ssid'];
        new_td23.appendChild(new_label10);
        new_tr14.appendChild(new_td23);

        var new_td24 = document.createElement("td");
        var new_label11 = document.createElement("label");
        new_label11.innerText = res[item]['rssi'];
        new_td24.appendChild(new_label11);
        new_tr14.appendChild(new_td24);

        tb.appendChild(new_tr14);
    }
}

function net_method(){
    if (document.getElementById("net_method").selectedIndex == '0'){
        net_ip = document.getElementsByClassName("net_ip");
        for (let i = 0; i < net_ip.length; i++){
            net_ip[i].disabled = "True";
            net_ip[i].value = "";
            net_ip[i].backgroundColor = "white";
        }
    }
    else{
        net_ip = document.getElementsByClassName("net_ip");
        for (let i = 0; i < net_ip.length; i++){
            net_ip[i].disabled = "";
        }
    }
}

function ValidateIPaddressOnChange(input) 
{
    var ipformat = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;

    if(!input.value.match(ipformat)) {
        input.style.backgroundColor = "red";
    }
    else{
        input.style.backgroundColor = "white";
    }
}