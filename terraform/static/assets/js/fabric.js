function gather_farbic_input () {
    var fabric_name = $("#fabric").val();
    var asn = $("#fabric_asn").val();
    var vrf = $("#vrf").val();
    var network = $("#network").val();
    var loopback_id = $("#loopback_id").val();
    var loopback_ipv4 = $("#loopback_ipv4").data("lo_ipv4_addrs");
    var loopback_ipv6 = $("#loopback_ipv6").data("lo_ipv6_addrs");
    if ( network != "" ){
        var gateway_v4 = $("#" + network).data("gateway_v4");
        var gateway_v6 = $("#" + network).data("gateway_v6");
    }else{
        var gateway_v4 = "";
        var gateway_v6 = "";
    }
    var node_sub = $("#ipv4_cluster_subnet").val();
    var ibgp_peer_vlan = $("#ibgp_peer_vlan").val();
    var k8s_route_map = $("#route_map").val();
    var route_tag = $("#loopback_route_tag").val();
    var ipv6_enabled = $("#enable_ipv6").prop("checked");
    var node_sub_v6 = $("#ipv6_cluster_subnet").val();
    var bgp_pass = ""; // seet to emplty untiil it is supported
    var k8s_integ = $("#k8s_integ").is(":checked")

    var vpc_peers = []
    $("#leaf_switches").children().each(function() {
        var peer = {
            primary: $(this).data("primary"),
            secondary: $(this).data("secondary"),
            primary_ipv4: $(this).data("primary_ipv4"),
            secondary_ipv4: $(this).data("secondary_ipv4")
        }
        vpc_peers.push(peer);

    });
    var data = {
        fabric_name: fabric_name,
        asn: asn,
        vrf: vrf,
        network: network,
        loopback_id: loopback_id,
        loopback_ipv4: loopback_ipv4,
        loopback_ipv6: loopback_ipv6,
        gateway_v4: gateway_v4.split("/")[0],
        gateway_v6: gateway_v6.split("/")[0],
        node_sub_v6: node_sub_v6,
        node_sub: node_sub,
        ibgp_peer_vlan: ibgp_peer_vlan,
        k8s_route_map: k8s_route_map,
        route_tag: route_tag,
        ipv6_enabled: ipv6_enabled,
        bgp_pass: bgp_pass,
        vpc_peers: vpc_peers,
        k8s_integ: k8s_integ
    }
    return data
};

$(document).ready(function() {
    $("#loopback_ipv4").data("lo_ipv4_addrs", [])
    $("#loopback_ipv6").data("lo_ipv6_addrs", [])
    $(window).keydown(function(e){
        if(e.key == "Enter") {
            e.preventDefault();
            return false;
        }
    });

    $("#adv_chck").click(function(){
        if ( $(this).prop("checked") ) {
            $("#checkbox-checked").fadeIn(200);
        } else {
            $("#checkbox-checked").fadeOut(200);
        };
    });

    $("#network").change(function(){
        var network = $(this).val();
        $("#ipv4_cluster_subnet").val($("#" + network).data("subnet_v4"));
        $("#ipv6_cluster_subnet").val($("#" + network).data("subnet_v6"));
    });
    $("#vrf").change(function(){
        var vrf_name = $(this).val();
        var fabric_name = $("#fabric").val();
        var query_url = "/query_ndfc"
        $.ajax({
            url: query_url,
            type: 'get',
            dataType: 'json',
            contentType: 'application/json',
            data: {
                fabric_type: getUrlParameter('fabric_type'),
                fabric_name: fabric_name,
                query_network: true,
                vrf_name: vrf_name
            },
            success: function (result, status, xhr) {
                $.each(result, function(index, value){
                    var option = '<option id="' + value["name"] + '"value="' + value["name"] +'">'
                    var option_net = $(option).appendTo($("#datalist_network"));
                    $(option_net).data("subnet_v4", value["subnet_v4"]);
                    $(option_net).data("subnet_v6", value["subnet_v6"]);
                    $(option_net).data("gateway_v4", value["gateway_v4"]);
                    $(option_net).data("gateway_v6", value["gateway_v6"]);
                });
            },
            error: function (xhr, status, error) {
                $("#alert_fail").fadeIn(500).delay(1000).fadeOut(500);
            }
        });

    });

    $("#fabric").change(function(){
        var fabric_name = this.value;
        $("#fabric_asn").val($("#" + this.value).attr("data-asn"));
        $("#div_asn").fadeIn(300);
        var query_url = "/query_ndfc"
        $.ajax({
            url: query_url,
            type: 'get',
            dataType: 'json',
            contentType: 'application/json',
            data: {
                fabric_type: getUrlParameter('fabric_type'),
                fabric_name: fabric_name,
                query_vrf: true
            },
            success: function (result, status, xhr) {
                $.each(result, function(index, value){
                    $('<option value="' + value +'">').appendTo($("#datalist_vrf"));
                });
            },
            error: function (xhr, status, error) {
                $("#alert_fail").fadeIn(500).delay(1000).fadeOut(500);
            }
        });

        $.ajax({
            url: query_url,
            type: 'get',
            dataType: 'json',
            contentType: 'application/json',
            data: {
                fabric_type: getUrlParameter('fabric_type'),
                fabric_name: fabric_name,
                query_vrf: false,
                query_inv: true
            },
            success: function (result, status, xhr) {
                $.each(result, function(index, value){
                    var vpc_peer = value.primary + "/" + value.secondary;
                    var opt_peer = '<option value="' + vpc_peer + '">' + vpc_peer + '</option>';
                    $(opt_peer).appendTo($("#vpc_peer"));
                });
                var vpc_selected = $("#vpc_peer").find(":selected").val();
                $("#primary").val(vpc_selected.split("/")[0]);
                $("#secondary").val(vpc_selected.split("/")[1]);
            },
            error: function (xhr, status, error) {
                $("#alert_fail").fadeIn(500).delay(1000).fadeOut(500);
            }
        });
    });

    $("#vpc_peer").change(function(){
        var vpc_selected = $("#vpc_peer").find(":selected").val();
        $("#primary").val(vpc_selected.split("/")[0]);
        $("#secondary").val(vpc_selected.split("/")[1]);
    });

    $("#input_lo_ipv4").on("keyup", function(e){
        if (e.key == "Enter") {
            var count_lo = $("#loopback_ipv4").children().length;
            if ( count_lo >= 2 ) {
                $("#form_loopback_alert").show();
                $("#form_loopback").addClass("form-group--error");
                return false
            };

            var lo_ipv4_addrs = $("#loopback_ipv4").data("lo_ipv4_addrs");
            if (lo_ipv4_addrs == null) {
                lo_ipv4_addrs = []
                $("#loopback_ipv4").data("lo_ipv4_addrs", lo_ipv4_addrs);
            };

            var ipv4_addr = $("#input_lo_ipv4").val();
            var lo_label = '<span class="label label--info label--raised base-margin-left"><span>' + ipv4_addr + '</span> <span class="icon-close"></span></span>';
            var label_ipv4 = $(lo_label).appendTo("#loopback_ipv4");
            label_ipv4.data("ipv4", ipv4_addr);
            lo_ipv4_addrs.push(ipv4_addr);
            $("#loopback_ipv4").data("lo_ipv4_addrs", lo_ipv4_addrs);
            $(this).val("");
        }
    });

    $("#loopback_ipv4").on("click", ".icon-close", function(){
        var ipv4  = $(this).parent().data("ipv4");
        var lo_ipv4_addrs = $("#loopback_ipv4").data("lo_ipv4_addrs");
        var new_lo_ipv4_addrs = lo_ipv4_addrs.filter(function(v){
            return v != ipv4;
        });
        $("#loopback_ipv4").data("lo_ipv4_addrs", new_lo_ipv4_addrs);
        $(this).parent().remove();
        var count_lo = $("#loopback_ipv4").children().length;
        if ( count_lo < 2 ) {
            $("#form_loopback_alert").hide();
            $("#form_loopback").removeClass("form-group--error");
            return false
        };
    });

    $("#input_lo_ipv6").on("keyup", function(e){
        if (e.key == "Enter") {
            var count_lo = $("#loopback_ipv6").children().length;
            if ( count_lo >= 2 ) {
                $("#form_loopbackv6_alert").show();
                $("#form_loopbackv6").addClass("form-group--error");
                return false
            };

            var lo_ipv6_addrs = $("#loopback_ipv6").data("lo_ipv6_addrs");
            if (lo_ipv6_addrs == null) {
                lo_ipv6_addrs = []
                $("#loopback_ipv6").data("lo_ipv6_addrs", lo_ipv6_addrs);
            };

            var ipv6_addr = $("#input_lo_ipv6").val();
            var lo_label = '<span class="label label--info label--raised base-margin-left"><span>' + ipv6_addr + '</span> <span class="icon-close"></span></span>';
            var label_ipv6 = $(lo_label).appendTo("#loopback_ipv6");
            label_ipv6.data("ipv6", ipv6_addr);
            lo_ipv6_addrs.push(ipv6_addr);
            $("#loopback_ipv6").data("lo_ipv6_addrs", lo_ipv6_addrs);
            $(this).val("");
        }
    });

    $("#loopback_ipv6").on("click", ".icon-close", function(){
        var ipv6  = $(this).parent().data("ipv6");
        var lo_ipv6_addrs = $("#loopback_ipv6").data("lo_ipv6_addrs");
        var new_lo_ipv6_addrs = lo_ipv6_addrs.filter(function(v){
            return v != ipv6;
        });
        $("#loopback_ipv6").data("lo_ipv6_addrs", new_lo_ipv6_addrs);
        $(this).parent().remove();
        var count_lo = $("#loopback_ipv6").children().length;
        if ( count_lo < 2 ) {
            $("#form_loopbackv6_alert").hide();
            $("#form_loopbackv6").removeClass("form-group--error");
            return false
        };
    });

    $("#enable_ipv6").on("change", function() {
        if ($(this).prop("checked")) {
            $("#container_ipv6").fadeIn(500);
        }else {
            $("#container_ipv6").fadeOut(500);
        };
    });

    $("#leaf_switches").on("click", ".icon-close", function(){
        $(this).parent().remove();
    });

    $("#primary_ipv4").on("blur", function (e){
        var this_svi = $(this).val();
        var peer_svi = next_ip(this_svi);
        $("#secondary_ipv4").val(peer_svi);
    });

    $("#add_node").on("click", function(e){
        var dup = false;
        $("#leaf_switches").children("span[class~='label']").each( function(){
            if ($(this).data("primary") == $("#primary").val()) {
                console.log("duplicate vpc peer!")
                dup = true
            };
        });

        if (dup) { return false};

        var line1 = '<span class="label label--raised label--large label--primary base-margin-left"><span class="text-size-12">';
        var line2 = $("#primary").val() + "(" + $("#primary_ipv4").val() +")<br>";
        var line3 = $("#secondary").val() + "(" + $("#secondary_ipv4").val() +")<br>";
        var line4 = '</span><span class="icon-close"></span></span>';
        var label_peers = [line1,line2,line3,line4].join("");
        var peer = $(label_peers).appendTo($("#leaf_switches"))
        peer.data("primary", $("#primary").val());
        peer.data("secondary", $("#secondary").val());
        peer.data("primary_ipv4", $("#primary_ipv4").val());
        peer.data("secondary_ipv4", $("#secondary_ipv4").val());
    });

    $("#next").on("click", function(e){
        var data = gather_farbic_input();
        var url = "/fabric?fabric_type=vxlan_evpn"
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (result, status, xhr) {
                $(location).attr('href',"/vcenterlogin?fabric_type=vxlan_evpn");
            },
            error: function (xhr, status, message) {
                $("#alert_fail_msg").text(xhr.responseJSON["error"]);
                $("#alert_fail").fadeIn(500).delay(2000).fadeOut(500);
            }
        });
    });
});
