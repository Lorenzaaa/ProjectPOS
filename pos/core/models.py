from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db.models import Sum
import uuid
from decimal import Decimal


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Cashier', 'Cashier'),
        ('Manager', 'Manager'),
        ('Inventory', 'Inventory'),
        ('Accountant', 'Accountant')
    ]
    
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return self.username
    
    class Meta:
        permissions = [
            ("can_view_reports", "Can view reports"),
            ("can_manage_inventory", "Can manage inventory"),
            ("can_process_returns", "Can process returns"),
            ("can_void_transactions", "Can void transactions"),
            ("can_modify_prices", "Can modify prices"),
        ]


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    ip_address = models.GenericIPAddressField()

    class Meta:
        verbose_name_plural = "User Activities"


class Receipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True)
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE)
    printed_count = models.IntegerField(default=0)
    last_printed = models.DateTimeField(null=True, blank=True)
    void_status = models.BooleanField(default=False)
    void_reason = models.TextField(null=True, blank=True)

    def print_receipt(self):
        if self.void_status:
            raise ValueError("Cannot print voided receipt")
        self.printed_count += 1
        self.save()


class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MOBILE', 'Mobile Money'),
        ('CREDIT', 'Store Credit')
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT)
    cashier = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)


class Product(models.Model):
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, unique=True)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey('ProductCategory', on_delete=models.PROTECT)
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT)
    unit = models.ForeignKey('Unit', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reorder_point = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    stock_quantity = models.IntegerField()
    packing_date = models.DateField()

    def get_available_quantity(self):
        return self.inventoryitem_set.aggregate(
            total=Sum('quantity')
        )['total'] or 0


class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    location = models.ForeignKey('StorageLocation', on_delete=models.PROTECT)
    expiry_date = models.DateField(null=True, blank=True)
    last_counted = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['product', 'batch_number']


class InventoryMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('TRANSFER', 'Transfer'),
        ('ADJUST', 'Adjustment'),
        ('RETURN', 'Return')
    ]

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference_number = models.CharField(max_length=50)
    from_location = models.ForeignKey('StorageLocation', related_name='from_movements', on_delete=models.PROTECT)
    to_location = models.ForeignKey('StorageLocation', related_name='to_movements', on_delete=models.PROTECT, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)


class CustomerCredit(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)
    last_payment_date = models.DateField(null=True, blank=True)

    def add_credit(self, amount):
        self.current_balance += Decimal(amount)
        self.save()

    def use_credit(self, amount):
        if self.current_balance >= Decimal(amount):
            self.current_balance -= Decimal(amount)
            self.save()
            return True
        return False


class CreditPayment(models.Model):
    customer_credit = models.ForeignKey(CustomerCredit, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50)
    received_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)


class Report(models.Model):
    REPORT_TYPES = [
        ('SALES', 'Sales Report'),
        ('INVENTORY', 'Inventory Report'),
        ('CREDIT', 'Credit Report'),
        ('PROFIT', 'Profit Report'),
        ('TAX', 'Tax Report')
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    generated_at = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField()  # Stores report parameters
    results = models.JSONField()  # Stores report results
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)


class ReportSchedule(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly')
    ]

    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPES)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    recipients = models.ManyToManyField(CustomUser)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name



class Customer(models.Model):
    contact_id = models.CharField(max_length=100)
    business_name = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    pay_term = models.CharField(max_length=50)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2)
    advance_balance = models.DecimalField(max_digits=10, decimal_places=2)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    mobile = models.CharField(max_length=20)
    total_sales_due = models.DecimalField(max_digits=10, decimal_places=2)
    total_sales_return_due = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.business_name

class Supplier(models.Model):
    contact_id = models.CharField(max_length=100)
    business_name = models.CharField(max_length=200)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    tax_number = models.CharField(max_length=100)
    pay_term = models.CharField(max_length=50)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2)
    advance_balance = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    address = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20)
    total_purchase_due = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.business_name

class Agent(models.Model):
    name = models.CharField(max_length=255)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Staff(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SalesOrder(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    order_no = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[
        ('Draft', 'Draft'),
        ('Quotation', 'Quotation'),
        ('Completed', 'Completed')
    ])
    shipping_status = models.CharField(max_length=50)
    quantity_remaining = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

class SalesReturn(models.Model):
    date = models.DateField()
    invoice_no = models.CharField(max_length=100)
    parent_sale = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_due = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.invoice_no

class Purchase(models.Model):
    date = models.DateField()
    reference_no = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    supplier = models.CharField(max_length=200)
    purchase_status = models.CharField(max_length=100, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])
    payment_status = models.CharField(max_length=100, choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid')])
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_due = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.reference_no} - {self.supplier}"

class PurchaseReturn(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    reference_no = models.CharField(max_length=100, unique=True)
    parent_purchase = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255)
    supplier = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50, choices=[
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial')
    ], default='Unpaid')
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_due = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.reference_no

class Stock(models.Model):
    sku = models.CharField(max_length=100)
    product = models.CharField(max_length=255)
    variation = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField()
    current_stock_value_purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock_value_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    potential_profit = models.DecimalField(max_digits=10, decimal_places=2)
    total_units_sold = models.IntegerField()
    total_units_transferred = models.IntegerField()
    total_units_adjusted = models.IntegerField()

    def __str__(self):
        return f'{self.product} ({self.sku})'

class Expense(models.Model):
    date = models.DateField()
    reference_no = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=255)
    recurring_details = models.TextField()
    expense_category = models.CharField(max_length=255)
    sub_category = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=50)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_due = models.DecimalField(max_digits=10, decimal_places=2)
    expense_for = models.CharField(max_length=255)

    def __str__(self):
        return self.reference_no

class ExpenseCategory(models.Model):
    category_name = models.CharField(max_length=255)
    category_code = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class MonthlySales(models.Model):
    month = models.CharField(max_length=20)
    sales = models.FloatField()

    def __str__(self):
        return f"{self.month}: {self.sales}"

class Metrics(models.Model):
    out_of_stock_products = models.IntegerField(default=0)
    number_of_customers = models.IntegerField(default=0)
    monthly_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    weekly_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    daily_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return "Dashboard Metrics"

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('Product wise discount', 'Product wise discount'),
        ('Total price discount', 'Total price discount'),
    ]

    from_date = models.DateField()
    to_date = models.DateField()
    discount_type = models.CharField(max_length=255, choices=DISCOUNT_TYPE_CHOICES)
    products = models.ManyToManyField(Product, related_name='discounts', blank=True)
    all_products_discount = models.BooleanField(default=False)
    quantity_based_discount = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.discount_type} from {self.from_date} to {self.to_date}"

class StorageLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class Unit(models.Model):
    name = models.CharField(max_length=50)  # e.g., "piece", "kg", "liter"
    symbol = models.CharField(max_length=10)  # e.g., "pcs", "kg", "L"