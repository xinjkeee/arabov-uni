from abc import ABC, abstractmethod
from datetime import datetime
import json

# Исключения
class InvalidOrderError(Exception):
    pass

# Интерфейс заказа
class Order(ABC):
    def __init__(self, order_id, price, customer, order_date, status):
        self.order_id = order_id
        self.price = price
        self.customer = customer
        self.order_date = order_date
        self.status = status

    @abstractmethod
    def track_status(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass

# Интерфейс логирования
class Logger(ABC):
    @abstractmethod
    def log_action(self, order_id, action):
        pass

# Интерфейс уведомлений
class Notifier(ABC):
    @abstractmethod
    def send_notification(self, order_id):
        pass

# Интерфейс сериализации
class Serializable(ABC):
    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass

# Миксин логирования
class LoggingMixin(Logger):
    def log_action(self, order_id, action):
        print(f"[LOG] Order {order_id}: {action}")

# Миксин уведомлений
class NotificationMixin(Notifier):
    def send_notification(self, order_id):
        print(f"[NOTIFY] Уведомление по заказу {order_id} отправлено")

# Адрес
class Address:
    def __init__(self, street, city, zip_code, country):
        self.street = street
        self.city = city
        self.zip_code = zip_code
        self.country = country

    def __str__(self):
        return f"{self.street}, {self.city}, {self.zip_code}, {self.country}"

# Клиент
class Customer:
    def __init__(self, name, email, phone, address):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.order_history = []

    def place_order(self, order):
        self.order_history.append(order)

    def get_order_history(self):
        return self.order_history

# Конкретные типы заказов
class OnlineOrder(Order, LoggingMixin, NotificationMixin, Serializable):
    def __init__(self, order_id, price, customer, order_date, status, items, payment_method):
        super().__init__(order_id, price, customer, order_date, status)
        self.items = items
        self.payment_method = payment_method

    def track_status(self):
        return f"Онлайн-заказ {self.order_id} сейчас в статусе '{self.status}'"

    def to_dict(self):
        return {
            "type": "online",
            "order_id": self.order_id,
            "price": self.price,
            "customer": self.customer,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "items": self.items,
            "payment_method": self.payment_method,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data["order_id"],
            price=data["price"],
            customer=data["customer"],
            order_date=datetime.fromisoformat(data["order_date"]),
            status=data["status"],
            items=data["items"],
            payment_method=data["payment_method"],
        )

class PhoneOrder(Order, LoggingMixin, NotificationMixin, Serializable):
    def __init__(self, order_id, price, customer, order_date, status, operator_name):
        super().__init__(order_id, price, customer, order_date, status)
        self.operator_name = operator_name

    def track_status(self):
        return f"Телефонный заказ {self.order_id} сейчас в статусе '{self.status}'"

    def to_dict(self):
        return {
            "type": "phone",
            "order_id": self.order_id,
            "price": self.price,
            "customer": self.customer,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "operator_name": self.operator_name,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data["order_id"],
            price=data["price"],
            customer=data["customer"],
            order_date=datetime.fromisoformat(data["order_date"]),
            status=data["status"],
            operator_name=data["operator_name"],
        )

class StoreOrder(Order, LoggingMixin, NotificationMixin, Serializable):
    def __init__(self, order_id, price, customer, order_date, status, store_location):
        super().__init__(order_id, price, customer, order_date, status)
        self.store_location = store_location

    def track_status(self):
        return f"Магазинный заказ {self.order_id} сейчас в статусе '{self.status}'"

    def to_dict(self):
        return {
            "type": "store",
            "order_id": self.order_id,
            "price": self.price,
            "customer": self.customer,
            "order_date": self.order_date.isoformat(),
            "status": self.status,
            "store_location": self.store_location,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data["order_id"],
            price=data["price"],
            customer=data["customer"],
            order_date=datetime.fromisoformat(data["order_date"]),
            status=data["status"],
            store_location=data["store_location"],
        )

# Фабрика заказов
class OrderFactory:
    @staticmethod
    def create_order(order_type):
        if order_type == "online":
            return OnlineOrder
        elif order_type == "phone":
            return PhoneOrder
        elif order_type == "store":
            return StoreOrder
        else:
            raise InvalidOrderError(f"Неизвестный тип заказа: {order_type}")

# Цепочка обязанностей: отмена заказа
class CancellationRequest:
    def __init__(self, order, reason):
        self.order = order
        self.reason = reason
        self.approved = False

class Handler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request):
        pass

class CallCenterOperator(Handler):
    def handle(self, request):
        print("Оператор проверяет запрос...")
        if request.reason:
            print("Оператор передает дальше")
            if self._next_handler:
                return self._next_handler.handle(request)
        else:
            print("Оператор отклонил запрос")

class Manager(Handler):
    def handle(self, request):
        print("Менеджер рассматривает запрос...")
        if request.order.price > 500:
            print("Менеджер требует одобрения администратора")
            if self._next_handler:
                return self._next_handler.handle(request)
        else:
            print("Менеджер одобрил отмену заказа")
            request.approved = True

class Admin(Handler):
    def handle(self, request):
        print("Администратор окончательно одобряет отмену")
        request.approved = True

# Проверка прав
def check_permission(user):
    # Допустим, все проходят
    return True

# -------------------------- MAIN --------------------------

def main():
    addr = Address("Ленина, 10", "Москва", "101000", "Россия")
    customer = Customer("Иван Иванов", "ivan@mail.ru", "+7 999 123 4567", addr)

    order1 = OnlineOrder(
        order_id=1,
        price=100.0,
        customer=customer.name,
        order_date=datetime.now(),
        status="создан",
        items=[{"name": "ноутбук", "qty": 1}],
        payment_method="карта"
    )

    customer.place_order(order1)
    print(order1.track_status())
    order1.log_action(order1.order_id, "Заказ создан")
    order1.send_notification(order1.order_id)

    cancel_request = CancellationRequest(order1, reason="Передумал")
    operator = CallCenterOperator()
    manager = Manager()
    admin = Admin()
    operator.set_next(manager).set_next(admin)

    if check_permission(operator):
        operator.handle(cancel_request)

    data = [order.to_dict() for order in customer.get_order_history()]
    with open("orders.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print("Заказы сохранены в orders.json")

    with open("orders.json", "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
        restored_orders = [OrderFactory.create_order(d["type"]).from_dict(d) for d in loaded_data]
        print("Загруженные заказы:")
        for o in restored_orders:
            print(o.track_status())

if __name__ == "__main__":
    main()
    