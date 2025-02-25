"""
URL configuration for pos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, LogoutView, LoginView
from core.views import (
    UserActivityViewSet, ReceiptViewSet,
    TransactionViewSet, ProductViewSet, InventoryItemViewSet,
    InventoryMovementViewSet, CustomerCreditViewSet, ReportViewSet,
    ReportScheduleViewSet, CustomerViewSet, SupplierViewSet,
    SalesOrderViewSet, SalesReturnViewSet, PurchaseViewSet,
    PurchaseReturnViewSet, StockViewSet, ExpenseViewSet,
    ExpenseCategoryViewSet, MonthlySalesViewSet, MetricsViewSet,
    DiscountViewSet,StorageLocationViewSet,
    BrandViewSet,ProductCategoryViewSet,UnitViewSet,CustomUserViewSet
    
)
from core.views import home_view

# Create a router instance
router = DefaultRouter()

# Register ViewSets
router.register(r'user-activity', UserActivityViewSet)
router.register(r'receipts', ReceiptViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'products', ProductViewSet)
router.register(r'inventory', InventoryItemViewSet)
router.register(r'inventory-movements', InventoryMovementViewSet)
router.register(r'customer-credits', CustomerCreditViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'report-schedules', ReportScheduleViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'sales-orders', SalesOrderViewSet)
router.register(r'sales-returns', SalesReturnViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'purchase-returns', PurchaseReturnViewSet)
router.register(r'stock', StockViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'monthly-sales', MonthlySalesViewSet)
router.register(r'metrics', MetricsViewSet)
router.register(r'discounts', DiscountViewSet)
router.register(r'storage-locations', StorageLocationViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'product-categories', ProductCategoryViewSet)
router.register(r'units', UnitViewSet)
router.register(r'users', CustomUserViewSet)


urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),

    # Router URLs
    path('api/', include(router.urls)),

    # Authentication
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('api/auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('', home_view, name='home'),
    
   ] 