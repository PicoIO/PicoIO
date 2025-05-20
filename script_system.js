document.getElementById("host").value = conf['hw']['sysname'];
document.getElementById("sys_user").value = conf['security']['user'];
document.getElementById("board").innerText = conf['hw']['board'];
document.getElementById("micropython").innerText = conf['hw']['release'];
document.getElementById("software_v").innerText = conf['hw']['sw'];
document.getElementById('sys_save').disabled = true;
document.getElementById("up_conf").disabled = true;

if (conf['hw']['sw_ch'] == 'production'){
    document.getElementById("sw_ch").selectedIndex = 0;
}
if (conf['hw']['sw_ch'] == 'test'){
    document.getElementById("sw_ch").selectedIndex = 1;
}

fetch('https://api.github.com/repos/picoio/picoio/releases', {
  headers: {Authorization: 'Bearer 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'}
})
    .then(response => response.json())
    .then(response => new_soft(response));

document.getElementById('sys_pass').addEventListener("change", () => {
    if (document.getElementById('sys_pass').value.length >= 8){
        document.getElementById('sys_save').disabled = false;
    }
    else{
        document.getElementById('sys_save').disabled = true;
    }
})

document.getElementById("conf_file").addEventListener("change", () => {
    if (document.getElementById("conf_file").files.length > 0){
        document.getElementById("up_conf").disabled = false;
    }
    else{
        document.getElementById("up_conf").disabled = true;
    }
})

document.getElementById("up_conf").addEventListener("click", async() => {
    reader = new FileReader();
    reader.addEventListener("load", () => {
        file_read = reader['result'];
        body_send = file_read + '\r\nEOF\r\n';
        fetch('\\up_conf', {body: body_send, method: "POST"})
    })
    reader.readAsText(document.getElementById("conf_file").files[0])
})

function new_soft(response){
    last_version = ''
    for (let items in response){
        if ((response[items]['prerelease'] == true || response[items]['prerelease'] == false) && conf['hw']['sw_ch'] == 'test'){
            //update test
            last_version = items;
            break;
        }
        if (response[items]['prerelease'] == false && conf['hw']['sw_ch'] == 'production'){
            //update production
            last_version = items;
            break;
        }
    }

    if (last_version != ''){
        if (response[last_version]['tag_name'] != conf['hw']['sw']){
            git_version = response[last_version]['tag_name'].replace('v', '').split('-')[0].split('.');
            loc_version = conf['hw']['sw'].replace('v', '').split('-')[0].split('.');
            git_non_prod = response[last_version]['tag_name'].replace('v', '').split('-')[1];
            loc_non_prod = conf['hw']['sw'].replace('v', '').split('-')[1];

            update_test = 0;
            if (git_non_prod && loc_non_prod){
                if (git_non_prod.split('.')[0] == 'beta' && loc_non_prod.split('.')[0] == 'alpha'){
                    update_test += 1;
                }
                if (git_non_prod.split('.')[0] == 'alpha' && loc_non_prod.split('.')[0] == 'alpha'){
                    if (loc_non_prod.split('.')[1]){
                        if (git_non_prod.split('.')[1] > loc_non_prod.split('.')[1]){
                            update_test += 1;
                        }
                    }
                    else{
                        update_test += 1;
                    }
                }
                if (git_non_prod.split('.')[0] == 'beta' && loc_non_prod.split('.')[0] == 'beta'){
                    if (loc_non_prod.split('.')[1]){
                        if (git_non_prod.split('.')[1] > loc_non_prod.split('.')[1]){
                            update_test += 1;
                        }
                    }
                    else{
                        update_test += 1;
                    }
                }
            }
            else{
                if (loc_non_prod){
                    if (loc_non_prod.split('.')[0] == 'alpha' || loc_non_prod.split('.')[0] == 'beta'){
                        update_test += 1;
                    }
                }
            }

            if (git_version[0] > loc_version[0] || git_version[1] > loc_version[1] || git_version[2] > loc_version[2] || update_test > 0){
                var new_tr8 = document.createElement("tr");
                var new_td15 = document.createElement("td");
                var new_label8 = document.createElement("label");
                new_label8.innerText = "New Software Version: " + response[last_version]['tag_name'];
                new_td15.appendChild(new_label8);
                new_tr8.appendChild(new_td15);

                var new_td16 = document.createElement("td");
                var new_button4 = document.createElement("button");
                new_button4.type = "button";
                new_button4.innerText = "Update";
                new_button4.className = "delete";
                new_td16.appendChild(new_button4);

                new_button4.addEventListener("click", () => {
                    window.location.href = '/update?version=' + response[last_version]['tag_name'];
                    console.log("update: " + response[last_version]['tag_name']);
                })

                new_tr8.appendChild(new_td16);
                document.getElementById("tb_system").appendChild(new_tr8);
            }
        }
    }
}