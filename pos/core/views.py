from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from core.models import (
    UserActivity, Receipt, Transaction, Product, InventoryItem,
    InventoryMovement, CustomerCredit, CreditPayment, Report, ReportSchedule,
    Role, Customer, Supplier, Agent, Staff, SalesOrder, SalesReturn, Purchase,
    PurchaseReturn, Stock, Expense, ExpenseCategory, MonthlySales, Metrics,
    Discount,StorageLocation, Brand, ProductCategory, Unit, CustomUser
)
from serializers import (
    UserActivitySerializer, ReceiptSerializer,
    TransactionSerializer, ProductSerializer, InventoryItemSerializer,
    InventoryMovementSerializer, CustomerCreditSerializer, CreditPaymentSerializer,
    ReportSerializer, ReportScheduleSerializer, RoleSerializer, CustomerSerializer,
    SupplierSerializer, AgentSerializer, StaffSerializer, SalesOrderSerializer,
    SalesReturnSerializer, PurchaseSerializer, PurchaseReturnSerializer,
    StockSerializer, ExpenseSerializer, ExpenseCategorySerializer,
    MonthlySalesSerializer, MetricsSerializer, DiscountSerializer,
    StorageLocationSerializer, BrandSerializer, ProductCategorySerializer,
    UnitSerializer,CustomUserSerializer,CustomUserDetailSerializer
)
from datetime import datetime
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse



class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'activity_type']
    search_fields = ['details']


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['void_status']

    @action(detail=True, methods=['post'])
    def print_receipt(self, request, pk=None):
        receipt = self.get_object()
        try:
            receipt.print_receipt()
            return Response({'status': 'receipt printed'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def void_receipt(self, request, pk=None):
        receipt = self.get_object()
        reason = request.data.get('reason')
        if not reason:
            return Response({'error': 'Void reason is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        receipt.void_status = True
        receipt.void_reason = reason
        receipt.save()
        return Response({'status': 'receipt voided'})


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_method', 'is_completed']
    search_fields = ['transaction_id']

    @action(detail=True, methods=['post'])
    def complete_transaction(self, request, pk=None):
        transaction = self.get_object()
        transaction.is_completed = True
        transaction.save()
        return Response({'status': 'transaction completed'})


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'brand', 'is_active']
    search_fields = ['name', 'barcode', 'sku']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        products = Product.objects.filter(
        stock_quantity__lte=F('reorder_point'))
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'location']

    @action(detail=True, methods=['post'])
    def update_count(self, request, pk=None):
        inventory_item = self.get_object()
        new_quantity = request.data.get('quantity')
        if new_quantity is None:
            return Response({'error': 'Quantity is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        inventory_item.quantity = new_quantity
        inventory_item.last_counted = datetime.now()
        inventory_item.save()
        return Response({'status': 'quantity updated'})


class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['movement_type', 'product']


class CustomerCreditViewSet(viewsets.ModelViewSet):
    queryset = CustomerCredit.objects.all()
    serializer_class = CustomerCreditSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_credit(self, request, pk=None):
        customer_credit = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        customer_credit.add_credit(amount)
        return Response({'status': 'credit added'})

    @action(detail=True, methods=['post'])
    def use_credit(self, request, pk=None):
        customer_credit = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        if customer_credit.use_credit(amount):
            return Response({'status': 'credit used'})
        return Response({'error': 'Insufficient credit'},
                        status=status.HTTP_400_BAD_REQUEST)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'generated_by']


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        return Response({'status': f'schedule {"activated" if schedule.is_active else "deactivated"}'})


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'business_name', 'mobile', 'email']

    @action(detail=True, methods=['get'])
    def get_total_sales(self, request, pk=None):
        customer = self.get_object()
        total_sales = Transaction.objects.filter(
            customer=customer, is_completed=True
        ).aggregate(total=Sum('total_amount'))
        return Response(total_sales)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'business_name', 'mobile', 'email']


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'shipping_status']
    search_fields = ['order_no']


class SalesReturnViewSet(viewsets.ModelViewSet):
    queryset = SalesReturn.objects.all()
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_status']
    search_fields = ['invoice_no', 'customer_name']


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['purchase_status', 'payment_status']
    search_fields = ['reference_no', 'supplier']


class PurchaseReturnViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReturn.objects.all()
    serializer_class = PurchaseReturnSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_status']
    search_fields = ['reference_no', 'supplier']


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['sku', 'product']

    @action(detail=False, methods=['get'])
    def low_stock_items(self, request):
        # Define your low stock threshold
        threshold = request.query_params.get('threshold', 10)
        low_stock = Stock.objects.filter(current_stock__lte=threshold)
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['expense_category', 'payment_status']
    search_fields = ['reference_no', 'customer_name']


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['category_name', 'category_code']


class MonthlySalesViewSet(viewsets.ModelViewSet):
    queryset = MonthlySales.objects.all()
    serializer_class = MonthlySalesSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def year_summary(self, request):
        year = request.query_params.get('year', datetime.now().year)
        sales = MonthlySales.objects.filter(
            month__startswith=str(year)
        ).order_by('month')
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)


class MetricsViewSet(viewsets.ModelViewSet):
    queryset = Metrics.objects.all()
    serializer_class = MetricsSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        metrics = Metrics.objects.first()  # Assuming one metrics record
        if not metrics:
            metrics = Metrics.objects.create()

        # Update metrics with real-time data
        metrics.out_of_stock_products = Product.objects.filter(
            stock_quantity=0).count()
        metrics.number_of_customers = Customer.objects.count()

        # You might want to calculate these based on actual transactions
        metrics.save()

        serializer = self.get_serializer(metrics)
        return Response(serializer.data)


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['discount_type', 'all_products_discount']

    @action(detail=False, methods=['get'])
    def active_discounts(self, request):
        today = datetime.now().date()
        active_discounts = Discount.objects.filter(
            from_date__lte=today,
            to_date__gte=today
        )
        serializer = self.get_serializer(active_discounts, many=True)
        return Response(serializer.data)
    

class StorageLocationViewSet(viewsets.ModelViewSet):
    queryset = StorageLocation.objects.all()
    serializer_class = StorageLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = StorageLocation.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Brand.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProductCategory.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Unit.objects.all()
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CustomUserDetailSerializer
        return CustomUserSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        role = self.request.query_params.get('role', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
def home_view(request):
    return HttpResponse("Welcome to the Home Page")
