from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import (
    CustomUser, UserActivity, Receipt, Transaction, Product, InventoryItem,
    InventoryMovement, CustomerCredit, CreditPayment, Report, ReportSchedule,
    Role, Customer, Supplier, Agent, Staff, SalesOrder, SalesReturn, Purchase,
    PurchaseReturn, Stock, Expense, ExpenseCategory, MonthlySales, Metrics,
    Discount,StorageLocation, Brand, ProductCategory, Unit
)

CustomUser = get_user_model()

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = '__all__'

class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['id', 'receipt_number', 'transaction', 'printed_count',
                 'last_printed', 'void_status', 'void_reason']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'customer', 'cashier', 'timestamp',
                 'payment_method', 'total_amount', 'paid_amount',
                 'change_amount', 'is_completed']

class ProductSerializer(serializers.ModelSerializer):
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'barcode', 'sku', 'category', 'brand', 'unit',
                 'price', 'cost_price', 'tax_rate', 'reorder_point', 'is_active',
                 'stock_quantity', 'packing_date', 'available_quantity']

    def get_available_quantity(self, obj):
        return obj.get_available_quantity()

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'batch_number', 'quantity', 'location',
                 'expiry_date', 'last_counted']

class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = ['id', 'product', 'movement_type', 'quantity', 'reference_number',
                 'from_location', 'to_location', 'timestamp', 'performed_by']

class CustomerCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCredit
        fields = ['id', 'customer', 'credit_limit', 'current_balance',
                 'last_payment_date']

class CreditPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPayment
        fields = ['id', 'customer_credit', 'amount', 'payment_date',
                 'reference_number', 'received_by']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'report_type', 'start_date', 'end_date', 'generated_by',
                 'generated_at', 'parameters', 'results', 'file_path']

class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = ['id', 'report_type', 'frequency', 'recipients', 'is_active',
                 'last_run', 'next_run']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'contact_id', 'business_name', 'name', 'email',
                 'pay_term', 'opening_balance', 'advance_balance', 'credit_limit',
                 'date', 'mobile', 'total_sales_due', 'total_sales_return_due']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'contact_id', 'business_name', 'name', 'email',
                 'tax_number', 'pay_term', 'opening_balance', 'advance_balance',
                 'date', 'address', 'mobile', 'total_purchase_due']

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'name', 'commission_rate']

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name', 'position']

class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = ['id', 'customer', 'agent', 'staff', 'date', 'order_no',
                 'location', 'status', 'shipping_status', 'quantity_remaining',
                 'total_amount', 'created_at']

class SalesReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReturn
        fields = ['id', 'date', 'invoice_no', 'parent_sale', 'customer_name',
                 'location', 'payment_status', 'total_amount', 'payment_due']

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['id', 'date', 'reference_no', 'location', 'supplier',
                 'purchase_status', 'payment_status', 'grand_total',
                 'payment_due', 'total']

class PurchaseReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturn
        fields = ['id', 'date', 'reference_no', 'parent_purchase', 'location',
                 'supplier', 'payment_status', 'grand_total', 'payment_due',
                 'total']

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'sku', 'product', 'variation', 'category', 'location',
                 'unit_selling_price', 'current_stock',
                 'current_stock_value_purchase_price',
                 'current_stock_value_sale_price', 'potential_profit',
                 'total_units_sold', 'total_units_transferred',
                 'total_units_adjusted']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'date', 'reference_no', 'customer_name',
                 'recurring_details', 'expense_category', 'sub_category',
                 'location', 'payment_status', 'tax', 'total_amount',
                 'payment_due', 'expense_for']

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'category_name', 'category_code']

class MonthlySalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySales
        fields = ['id', 'month', 'sales']

class MetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = ['id', 'out_of_stock_products', 'number_of_customers',
                 'monthly_sales', 'weekly_sales', 'daily_sales']

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'from_date', 'to_date', 'discount_type', 'products',
                 'all_products_discount', 'quantity_based_discount', 'quantity',
                 'total_price', 'discount_percent']
        

class StorageLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageLocation
        fields = ['id', 'name', 'description']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description']

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'symbol']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name',
            'role',
            'is_active',
            'last_login_ip',
            'failed_login_attempts',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

# Nested serializer for CustomUser to include more details
class CustomUserDetailSerializer(CustomUserSerializer):
    groups = serializers.StringRelatedField(many=True)
    user_permissions = serializers.StringRelatedField(many=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ['groups', 'user_permissions']