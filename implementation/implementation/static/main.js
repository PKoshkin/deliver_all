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

    request(endpoint, method, context, callback) {
        context["method"] = method;
        var xhttp = new XMLHttpRequest();
        var that = this;
        if (typeof callback === "string") {
            callback = function() {
                if (this.readyState == 4 && this.status == 200) {
                    that.context[callback] = JSON.parse(this.responseText);
                    that.render();
                }
            };
        }
        xhttp.onreadystatechange = callback;
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

const button = "<button onclick='view.chooseRoute({{id}})'>Выбрать маршрут</button>";

class OrderListView extends View {
    constructor() {
        super()
        this.template = "<button onclick='init()'>Назад</button><ol>{{#orders}}"+
        "<li>{{from}} -> {{to}} ({{num}} товаров)"+
        "{{#route}}{{#element}}{{#vertex}}{{name}}{{/vertex}}"+
        "{{^vertex}} --{{name}}-> {{/vertex}}{{/element}}{{/route}}"+
        "{{^route}}<div id='{{id}}'>"+button+"</div>{{/route}}</li>"+
        "{{/orders}}</ol>{{^orders}}Загрузка{{/orders}}"
        this.load()
    }
    
    load() {
        this.request("order_list", "get_orders", {}, "orders")
    }

    chooseRoute(order) {
        var that = this;
        this.request("order_list", "get_routes", {"order": order}, function() {
            var context = JSON.parse(this.responseText);
            document.getElementById(order).innerHTML = Mustache.render("<select onchange='view.onselect({{order}}, this)'>{{#routes}}<option value={{index}}>{{length}} дн. {{cost}} руб. {{type}}{{/routes}}", context)
        });
    }

    onselect(order, elem) {
        this.selectRoute(order, this.val);
    }

    selectRoute(order, index) {
        var that = this;
        this.request("order_list", "select_route", {"order": order, "index": index}, function () {
            that.load();
        });
    }
}

const product = "<input name={{index}}>кг.<br/>";

class PlaceOrderView extends View {
    constructor() {
        super()
        this.template = "Введите параметры заказа:<br/><form name='main'>"+
            "Откуда: <input name='from'><br/>"+
            "Куда: <input name='to'><br/>"+
            "Товары: <button onclick='view.addProduct(); return false;'>+</button><br/>"+
            "<div id='products'>"+Mustache.render(product, {"index": 0})+"</div>"+
            "<button onclick='view.submit()'>Добавить заказ</button></form>";
        this.product_num = 1;
    }

    addProduct() {
        document.getElementById("products").innerHTML += Mustache.render(product, {"index": this.product_num});
        this.product_num += 1;
    }

    submit() {
        var form = document.forms["main"];
        var products = [];
        for (var i = 0; i < this.product_num; ++i) {
            products[i] = form[i.toString()].value;
        }
        var data = {
            "from": form["from"].value,
            "to": form["to"].value,
            "products": products,
        }
        this.request("order_list", "place_order", data, init);
        return false;
    }
}

function init() {
    switchView(new MainView());
}
