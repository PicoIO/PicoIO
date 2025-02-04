
    conf = %s;
    gp = [];
    input = 0;
    aux = 0;
    onewire = null;
    ref = 0;

    for (var key in conf['gpio'] ){
        gp.push(key.replace('gp', ''));
    }

    gp.sort(function(a, b){return a - b});
    
    for (let item in gp){
        var new_tr1 = document.createElement("tr");
        var new_td1 = document.createElement("td");
        new_td1.id = 'td1_' + gp[item];

        var new_label1 = document.createElement("label");
        new_label1.innerText = 'GP' + gp[item];
        new_td1.appendChild(new_label1);

        var new_td2 = document.createElement("td");
        new_td2.id = 'td2_' + gp[item];

        var new_select1 = document.createElement("select");
        new_select1.name = 'type' + gp[item];
        new_select1.id = 'type' + gp[item];

        var new_option0 = document.createElement("option");
        new_option0.innerText = "N/A";
        new_option0.value = 0;
        new_select1.appendChild(new_option0);

        var new_option1 = document.createElement("option");
        new_option1.innerText = "Input";
        new_option1.value = 1;
        new_select1.appendChild(new_option1);

        var new_option2 = document.createElement("option");
        new_option2.innerText = "Output";
        new_option2.value = 2;
        new_select1.appendChild(new_option2);

        var new_option3 = document.createElement("option");
        new_option3.innerText = "1-Wire";
        new_option3.value = 3;
        new_select1.appendChild(new_option3);

        new_select1.selectedIndex = conf['gpio']['gp' + gp[item]]['type'];

        new_td2.appendChild(new_select1);

        var new_td3 = document.createElement("td");
        new_td3.id = 'td3_' + gp[item];
        var new_td4 = document.createElement("td");
        new_td4.id = 'td4_' + gp[item];
        var new_td4_1 = document.createElement("td");
        new_td4_1.id = 'td4_1_' + gp[item];

        if (conf['gpio']['gp' + gp[item]]['type'] == "1"){
            digital_input(gp[item], new_td3, conf['gpio']['gp' + gp[item]]['resistor'], new_td4, conf['gpio']['gp' + gp[item]]['contact'], conf['debounce']['ms_time']);
            var new_div = document.createElement("span");
            new_div.className = "grey_dot";
            new_div.id = "stat" + gp[item];
            new_td4_1.appendChild(new_div);
        }
        if (conf['gpio']['gp' + gp[item]]['type'] == "2"){
            digital_output(gp[item], new_td4_1);
        }
        if (conf['gpio']['gp' + gp[item]]['type'] == "3"){
            onewire = gp[item];
        }

        new_tr1.appendChild(new_td1);
        new_tr1.appendChild(new_td2);
        new_tr1.appendChild(new_td3);
        new_tr1.appendChild(new_td4);
        new_tr1.appendChild(new_td4_1);

        document.getElementById("gpio").appendChild(new_tr1);

        document.getElementById("type" + gp[item]).addEventListener("change", () => {
            //Input
            if (document.getElementById("type" + gp[item]).options.selectedIndex == 1){
                digital_input(gp[item], document.getElementById('td3_' + gp[item]), 1, document.getElementById('td4_' + gp[item]), 1, conf['debounce']['ms_time']);
            }
            else{
                if (document.getElementById('resistor' + gp[item]) || document.getElementById('contact' + gp[item])){
                    document.getElementById('td3_' + gp[item]).removeChild(document.getElementById('resistor' + gp[item]));
                    document.getElementById('td4_' + gp[item]).removeChild(document.getElementById('contact' + gp[item]));
                    input -= 1;
                    aux -= 1;
                }
            }
            if (input == 0 && document.getElementById("tr_debounce")){
                document.getElementById("gpio_aux").removeChild(document.getElementById("tr_debounce"));
                if (aux == 0){
                    document.getElementById("gpio_aux").style.display = "None";
                }
            }
            //1 Wire
            if (document.getElementById("type" + gp[item]).options.selectedIndex == 3){
                onewire = gp[item];
                one_wire(gp[item]);
            }
            else{
                if (onewire == gp[item] && document.getElementById("tr_1wire_1") && document.getElementById("tr_1wire_2")){
                    aux -= 1;
                    one_wire_rem();
                    if (aux == 0){
                        document.getElementById("gpio_aux").style.display = "None";
                    }
                }
            }
        })
    }
    var new_button1 = document.createElement("button");
    new_button1.innerText = "Save";
    document.getElementById("gpio_config").appendChild(new_button1)

    if (onewire){
        one_wire(onewire);
    }

    var auto_refresh = setInterval(
        function (){
            fetch('\gp_stat')
                .then(stat => stat.json())
                .then(stat => check(stat))
                .catch(err => check_err(err))
        },
        5000 //timeout ms
    );

    function digital_input(num, td1, resistor, td2, contact, debounce_time){
        input += 1;
        aux += 1;

        var new_select2 = document.createElement("select");
        new_select2.name = 'resistor' + num;
        new_select2.id = 'resistor' + num;

        var new_option4 = document.createElement("option");
        new_option4.innerText = "Pull UP";
        new_option4.value = 1;
        new_select2.appendChild(new_option4);

        var new_option5 = document.createElement("option");
        new_option5.innerText = "Pull DOWN";
        new_option5.value = 2;
        new_select2.appendChild(new_option5);

        new_select2.selectedIndex = resistor-1;

        td1.appendChild(new_select2);

        var new_select3 = document.createElement("select");
        new_select3.name = 'contact' + num;
        new_select3.id = 'contact' + num;

        var new_option6 = document.createElement("option");
        new_option6.innerText = "NO";
        new_option6.value = 1;
        new_select3.appendChild(new_option6);

        var new_option7 = document.createElement("option");
        new_option7.innerText = "NC";
        new_option7.value = 2;
        new_select3.appendChild(new_option7);

        new_select3.selectedIndex = contact-1;

        td2.appendChild(new_select3);

        if (!document.getElementById("tr_debounce")){
            var new_tr2 = document.createElement("tr");
            new_tr2.id = "tr_debounce";
            var new_td5 = document.createElement("td");
            var new_label2 = document.createElement("label");
            new_label2.innerText = "Debounce";
            new_td5.appendChild(new_label2);

            var new_td6 = document.createElement("td");
            var new_input1 = document.createElement("input");
            new_input1.name = "debounce";
            new_input1.type = "number";
            new_input1.value = debounce_time;
            new_td6.appendChild(new_input1);

            var new_label3 = document.createElement("label");
            new_label3.innerText = "ms";
            new_td6.appendChild(new_label3);

            new_tr2.appendChild(new_td5);
            new_tr2.appendChild(new_td6);
            document.getElementById("gpio_aux").appendChild(new_tr2);
            document.getElementById("gpio_aux").style.display = "table";
        }
    }

    function digital_output(num, td1){
        var new_label6 = document.createElement("label");
        new_label6.className = "switch";
        var new_input3 = document.createElement("input");
        new_input3.type = "checkbox";
        new_input3.id = "checkbox" + num;
        var new_span1 = document.createElement("span");
        new_span1.className = "slider";

        new_label6.appendChild(new_input3);
        new_label6.appendChild(new_span1);

        td1.appendChild(new_label6);

        new_input3.addEventListener("change", () => {
            if (new_input3.checked){
                fetch('/gp_act?' + num + '=1');
            }
            else{
                fetch('/gp_act?' + num + '=0');
            }
        })
    }

    function one_wire(num){
        aux += 1;
        document.getElementById("gpio_aux").style.display = "Table";
        for (let item in gp){
            if (num != gp[item]){
                document.getElementById("type" + gp[item]).getElementsByTagName("option")[3].disabled = "True";
            }
        }
        var new_tr3 = document.createElement("tr");
        new_tr3.id = "tr_1wire_1";
        var new_td7 = document.createElement("td");
        var new_label4 = document.createElement("label");
        new_label4.innerText = "1-Wire refresh interval";

        new_td7.appendChild(new_label4);

        var new_td8 = document.createElement("td");
        var new_input2 = document.createElement("input");
        new_input2.name = "1wire_refresh";
        new_input2.type = "Number";
        new_input2.value = conf['1wire']['s_time'];

        new_td8.appendChild(new_input2);

        var new_label5 = document.createElement("label");
        new_label5.innerText = "s";

        new_td8.appendChild(new_label5);

        new_tr3.appendChild(new_td7);
        new_tr3.appendChild(new_td8);
        document.getElementById("gpio_aux").appendChild(new_tr3);

        var new_tr4 = document.createElement("tr");
        new_tr4.id = "tr_1wire_2"
        var new_td9 = document.createElement("td");
        new_td9.colSpan = "2";
        new_td9.id = "for_1wire";

        var new_header1 = document.createElement("h3");
        new_header1.innerText = "Sensors:";

        new_td9.appendChild(new_header1);

        var new_table1 = document.createElement("table");
        new_table1.id = "table_1wire"
        var new_tr5 = document.createElement("tr");
        var new_th1 = document.createElement("th");
        new_th1.innerText = "ID";
        new_tr5.appendChild(new_th1);

        var new_th2 = document.createElement("th");
        new_th2.innerText = "Name";
        new_tr5.appendChild(new_th2);

        var new_th3 = document.createElement("th");
        new_th3.innerText = "Temperature";
        new_tr5.appendChild(new_th3);

        var new_tr6 = document.createElement("tr")
        var new_td10 = document.createElement("td");

        new_tr6.appendChild(new_td10);
        new_table1.appendChild(new_tr5);
        new_td9.appendChild(new_table1);

        new_tr4.appendChild(new_td9);
        document.getElementById("gpio_aux").appendChild(new_tr4);
    }

    function one_wire_rem(){
        document.getElementById("gpio_aux").removeChild(document.getElementById("tr_1wire_1"));
        document.getElementById("gpio_aux").removeChild(document.getElementById("tr_1wire_2"))
        for (let item in gp){
            document.getElementById("type" + gp[item]).getElementsByTagName("option")[3].disabled = "";
        }
    }

    function check_err(err){
        red = document.getElementsByClassName("red_dot");
        for (let i = 0; i < red.length;){
            red[0].className = "grey_dot";
        }
        green = document.getElementsByClassName("green_dot");
        for (let i = 0; i < green.length;){
            green[0].className = "grey_dot";
        }
        delete_cl = document.getElementsByClassName("delete");
        for (let i = 0; i < delete_cl.length;){
            delete_cl[i].parentNode.removeChild(delete_cl[i])
            ref = 0;
        }
        console.error(err);
    }

    function check(js){
        for (item in js['input']){
            if (js['input'][item] == 0){
                document.getElementById('stat' + item.replace('gp', '')).className = "red_dot";
            }
            if (js['input'][item] == 1){
                document.getElementById('stat' + item.replace('gp', '')).className = "green_dot";
            }
        }
        for (item in js['output']){
            if (js['output'][item] == 0){
                document.getElementById('checkbox' + item.replace('gp', '')).checked = "";
            }
            if (js['output'][item] == 1){
                document.getElementById('checkbox' + item.replace('gp', '')).checked = "True";
            }
        }
        //sensors
        if (ref == 0 && document.getElementById("table_1wire")){
            ref = 1
            document.getElementById("table_1wire").innerHTML = '';
            var new_tr5 = document.createElement("tr");
            var new_th1 = document.createElement("th");
            new_th1.innerText = "ID";
            new_tr5.appendChild(new_th1);

            var new_th2 = document.createElement("th");
            new_th2.innerText = "Name";
            new_tr5.appendChild(new_th2);

            var new_th3 = document.createElement("th");
            new_th3.innerText = "Temperature";
            new_tr5.appendChild(new_th3);

            document.getElementById("table_1wire").appendChild(new_tr5);

            for (let items in js['1wire']){
                var new_tr7 = document.createElement("tr");
                new_tr7.id = 'tr_1wire_sensors' + items;

                var new_td11 = document.createElement("td");
                var new_input4 = document.createElement("input");
                new_input4.value = js['1wire'][items]['rom'];
                new_input4.name = '1w_sensor_id' + items;
                new_input4.readOnly = 'True';
                new_td11.appendChild(new_input4);

                var new_td12 = document.createElement("td");
                var new_input5 = document.createElement("input");
                new_input5.value = js['1wire'][items]['name'];
                new_input5.name = '1w_sensor_name' + items;
                new_td12.appendChild(new_input5);

                var new_td13 = document.createElement("td");
                var new_label7 = document.createElement("label");
                new_label7.innerText = js['1wire'][items]['temp'] + ' \u2103';
                new_td13.appendChild(new_label7);

                if (js['1wire'][items]['temp'] == 'offline'){
                    new_tr7.style.backgroundColor = "red";
                    new_input4.style.backgroundColor = "red";
                    new_input5.style.backgroundColor = "red";
                    new_label7.innerText = "Offline";
                }
                if (js['1wire'][items]['new'] == '1'){
                    new_tr7.style.backgroundColor = "yellow";
                    new_input4.style.backgroundColor = "yellow";
                    new_input5.style.backgroundColor = "yellow";
                }

                new_tr7.appendChild(new_td11);
                new_tr7.appendChild(new_td12);
                new_tr7.appendChild(new_td13);

                var new_td14 = document.createElement("td");
                var new_button3 = document.createElement("button");
                new_button3.type = "button";
                new_button3.innerText = "Delete";
                new_button3.className = "delete";

                new_button3.addEventListener("click", () => {
                    document.getElementById("table_1wire").removeChild(document.getElementById("tr_1wire_sensors" + items));
                })
                new_td14.appendChild(new_button3);
                new_tr7.appendChild(new_td14)
                
                document.getElementById("table_1wire").appendChild(new_tr7);
            }
        
            var new_button2 = document.createElement("button");
            new_button2.type = "button";
            new_button2.innerText = "Refresh";
            new_button2.className = "delete"
            
            new_button2.addEventListener("click", () => {
                ref = 0;
                document.getElementById('for_1wire').removeChild(new_button2);
            })
            document.getElementById('for_1wire').appendChild(new_button2);
        }
    }
