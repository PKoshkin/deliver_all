var view = null;

function switchView(newView) {
    view = newView;
    console.log(view);
    view.render();
}

class View {
    constructor() {
        this.template = "";
        this.context = {};
    }

    render() {
        document.getElementById("container").innerHTML = Mustache.render(this.template, this.context);
    }

    request(endpoint, method, context, key) {
        context["method"] = method;
        var xhttp = new XMLHttpRequest();
        var that = this;
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                that.context[key] = JSON.parse(this.responseText);
                that.render();
            }
        };
        xhttp.open("POST", "/api/"+endpoint+"/", true);
        xhttp.setRequestHeader("Content-type", "application/json");
        xhttp.send(JSON.stringify(context));
    }

    validate() {
        return true;
    }

    submit() {
        return;
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
        this.template = "<button onclick='init()'>Назад</button><ol>{{#orders}}"+
        "<li>{{from}} -> {{to}} ({{num}} товаров)"+
        "{{#route}}{{#element}}{{#vertex}}{{name}}{{/vertex}}"+
        "{{^vertex}} --{{name}}-> {{/vertex}}{{/element}}{{/route}}"+
        "{{^route}}<button onclick='view.chooseRoute({{id}})'>Выбрать маршрут</button>{{/route}}</li>"+
        "{{/orders}}</ol>{{^orders}}Загрузка{{/orders}}"
        this.request("order_list", "get_orders", {}, "orders")
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
