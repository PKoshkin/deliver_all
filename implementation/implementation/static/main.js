var view = null;

function switchView(newView) {
    view = newView;
    console.log(view);
    view.render();
}

class View {
    constructor() {
        this.template = "";
    }

    render(context) {
        document.getElementById("container").innerHTML = Mustache.render(this.template, context);
    }

    request(endpoint, method, context, callback) {
        context["method"] = method;
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                callback(JSON.parse(this.responseText));
            }
        };
        xhttp.open("POST", "/api/"+endpoint+"/", true);
        xhttp.setRequestHeader("Content-type", "application/json");
        xhttp.send(JSON.dump(context));
    }
}

class MainView extends View {
    constructor() {
        super()
        this.template = "<ol><li><a onclick='view.toOrderList()'>Список заказов</a></li><li><a onclick='view.toPlaceOrder()'>Разместить заказ</a></li></ol>";
    }

    toOrderList() {
        switchView(new OrderListView())
    }

    toPlaceOrder() {
        switchView(new PlaceOrderView())
    }
}

class OrderListView extends View {
    constructor() {
        super()
        this.template = "test";
    }
}

class PlaceOrderView extends View {
    constructor() {
        super()
        this.template = "no";
    }
}

function init() {
    switchView(new MainView());
}
