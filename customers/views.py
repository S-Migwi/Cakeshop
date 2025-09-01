import io
import os
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.db import transaction
from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDate, TruncMonth
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer

from .models import Product, Order, OrderItem, Contact, Gallery, Supplier
from .forms import ProductForm, OrderItemForm, ContactForm, SupplierForm, ProfitLossForm
from django.contrib import messages


from django.shortcuts import render
# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the data to the database
            messages.success(request, "Thank you for contacting us! We will get back to you soon.")
            return redirect('contact')  # Redirect to the same page or another page
        else:
            messages.error(request, "There was an error with your submission. Please check the form and try again.")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})




def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('dashboard')  # Redirect to dashboard on successful login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

LOW_STOCK_THRESHOLD = 5

def product_list(request):
    q = request.GET.get('q', '').strip()
    if q:
        products = Product.objects.filter(name__icontains=q)
    else:
        products = Product.objects.all()

    # ——— low-stock check & notify ———
    low_stock_items = products.filter(stock__lt=LOW_STOCK_THRESHOLD)

    # Keep the on-page user warnings every request
    for p in low_stock_items:
        messages.warning(
            request,
            f'⚠️ "{p.name}" only has {p.stock} left in stock!'
        )

    # Prepare to email admins only about items that have NOT been notified before
    new_low_qs = low_stock_items.filter(low_stock_notified=False)

    if new_low_qs.exists():
        new_low = list(new_low_qs)  # evaluate queryset so we can reference the objects
        subject = "Low Stock Alert"
        body = "\n".join(f'- {p.name}: {p.stock} left' for p in new_low)

        # Atomically mark those products as notified to reduce race conditions
        with transaction.atomic():
            ids = [p.pk for p in new_low]
            Product.objects.filter(pk__in=ids, low_stock_notified=False).update(low_stock_notified=True)

        # Send a single email for all newly-notified items
        mail_admins(subject, body)

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': q,
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        auth_login(request, user) # Log the user in immediately after signup
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'signup.html')


def product_gallery(request):
    products = Gallery.objects.all()
    return render(request, 'product_gallery.html', {'products': products})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'contact_list.html', {'contacts': contacts})



def suppliers_page(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('suppliers_page')
    else:
        form = SupplierForm()

    suppliers = Supplier.objects.all()
    return render(request, 'suppliers_page.html', {'form': form, 'suppliers': suppliers})


@login_required
def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('suppliers_page')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'edit_supplier.html', {'form': form, 'supplier': supplier})




@login_required
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')
    return redirect('suppliers_page')


def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('feedback')  # Replace with your list view name
    else:
        form = ContactForm(instance=contact)

    return render(request, 'edit_contact.html', {'form': form})


def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)

    if request.method == 'POST':
        contact.delete()
        return redirect('feedback')  # Replace with your list view name

    return render(request, 'confirm_delete.html', {'contact': contact})



@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES, instance=product)
        if form.is_valid():
            form.save()
            if 'image' in request.FILES:
                file_name = os.path.basename(request.FILES['image'].name)
                messages.success(request, f'Customer updated successfully! {file_name} uploaded')
            else:
                messages.error(request, 'Product details updated successfully')
            return redirect('product_list')
        else:
            messages.error(request, 'Please confirm your changes')

    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})


from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def place_order(request):
    # server-side search support (reads ?q=...)
    q = request.GET.get('q', '').strip()
    if q:
        products = Product.objects.filter(name__icontains=q)
    else:
        products = Product.objects.all()

    # Either get or start a new draft order
    order, created = Order.objects.get_or_create(
        user=request.user,
        is_paid=False,
        defaults={'total_price': Decimal('0.00')}
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('products')
        if not selected_ids:
            messages.error(request, "Please select at least one product.")
            return redirect('place_order')

        with transaction.atomic():
            # clear previous draft items (optional)
            if order.items.exists():
                order.items.all().delete()
                order.total_price = Decimal('0.00')

            order_total = Decimal('0.00')

            for pid in selected_ids:
                product = get_object_or_404(Product, pk=pid)
                try:
                    qty = int(request.POST.get(f'quantity_{pid}', 1))
                except (ValueError, TypeError):
                    qty = 1

                if qty < 1:
                    messages.error(request, f"Invalid quantity for {product.name}.")
                    continue
                if product.stock < qty:
                    messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock}.")
                    continue

                unit_price = Decimal(product.price)
                line_price = (unit_price * qty).quantize(Decimal('0.01'))

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=unit_price,   # store unit price
                )

                # decrement stock
                product.stock = F('stock') - qty
                product.save(update_fields=['stock'])

                order_total += line_price

            # refresh product instances that used F() (optional)
            for pid in selected_ids:
                Product.objects.filter(pk=pid).update()  # no-op but ensures F() applied, or use refresh_from_db()

            order.total_price = order_total.quantize(Decimal('0.01'))
            order.is_paid = True
            order.save()

        if action == 'save':
            messages.success(request, "Order saved! You can view it in the report.")
            return redirect('orders_report')
        elif action == 'print':
            return render(request, 'orders/view_order.html', {
                'order': order,
                'items': order.items.select_related('product'),
            })

    # GET or fall-through: pass 'query' so the template keeps the search value
    return render(request, 'orders/place_order.html', {
        'products': products,
        'query': q,
    })



@login_required
def view_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/view_order.html', {'order': order})


def edit_order(request, order_id):
    # 1. fetch order and all products
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    products = Product.objects.all()

    # 2. build a map of existing OrderItems by product id
    order_items_map = {item.product.id: item for item in order.items.all()}

    # 3. build product_list entries for the template
    product_list = []
    for p in products:
        existing = order_items_map.get(p.id)
        product_list.append({
            'product': p,
            'selected': bool(existing),
            'quantity': existing.quantity if existing else 1,
        })

    if request.method == 'POST':
        selected_ids = request.POST.getlist('products')
        if not selected_ids:
            messages.error(request, "Please select at least one product.")
            return redirect('edit_order', order.id)

        # clear out old items and reset total
        order.items.all().delete()
        order.total_price = Decimal('0.00')

        for pid in selected_ids:
            p = get_object_or_404(Product, pk=pid)
            try:
                qty = int(request.POST.get(f'quantity_{pid}', 1))
            except ValueError:
                qty = 1

            if qty < 1 or qty > p.stock:
                messages.error(request, f"Invalid quantity for {p.name}.")
                continue

            line_price = Decimal(p.price) * qty
            order.items.create(
                product=p,
                quantity=qty,
                price=line_price
            )
            p.stock -= qty
            p.save()
            order.total_price += line_price

        order.save()
        messages.success(request, "Order updated.")
        return redirect('view_order', order.id)

    # GET: render with product_list
    return render(request, 'orders/edit_order.html', {
        'order': order,
        'product_list': product_list,
    })



def delete_order(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        # Delete the order
        order.delete()
        messages.success(request, f"Order {order_id} has been deleted successfully!")
        return redirect('orders_report')  # Redirect to a relevant page (e.g., dashboard or order list)

    return render(request, 'orders/confirm_delete.html', {'order': order})

def generate_pdf(request):
    # Buffer instead of writing straight to HttpResponse for Platypus
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()
    title = Paragraph("Product List Report", styles['Heading1'])

    # Table header
    data = [[
        'Product Name',
        'Description',
        'Cost Price',
        'Selling Price',
        'Stock',
    ]]

    # Fetch and append each product row
    for prod in Product.objects.all().order_by('name'):
        desc = (prod.description[:40] + '…') \
               if len(prod.description) > 40 else prod.description
        data.append([
            prod.name,
            desc,
            f"Ksh {prod.cost_price:.2f}",
            f"Ksh {prod.price:.2f}",
            str(prod.stock),
        ])

    # Create the table and style it
    table = Table(data, colWidths=[100, 200, 80, 80, 50])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3d3d3')),
        ('TEXTCOLOR',   (0, 0), (-1, 0), colors.black),
        ('ALIGN',       (2, 1), (4, -1), 'RIGHT'),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 0), (-1, 0), 12),
        ('FONTSIZE',    (0, 1), (-1, -1), 10),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    # Build document
    elements = [title, Spacer(1, 12), table]
    doc.build(elements)

    # Return PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="product_report.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response
MONTH_CHOICES = [
    ('01', 'Jan'), ('02', 'Feb'), ('03', 'Mar'), ('04', 'Apr'),
    ('05', 'May'), ('06', 'Jun'), ('07', 'Jul'), ('08', 'Aug'),
    ('09', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec'),
]

def orders_report(request):
    start = request.GET.get('start_date')
    end   = request.GET.get('end_date')

    # Base queryset of paid orders
    qs_orders = Order.objects.filter(is_paid=True)
    if start:
        qs_orders = qs_orders.filter(created_at__date__gte=start)
    if end:
        qs_orders = qs_orders.filter(created_at__date__lte=end)

    # Build the OrderItem queryset, with line_total annotation
    qs_items = (
        OrderItem.objects
                 .filter(order__in=qs_orders)
                 .select_related('order', 'product')
                 .annotate(
                     line_total=ExpressionWrapper(
                         F('price') * F('quantity'),
                         output_field=DecimalField(max_digits=12, decimal_places=2)
                     )
                 )
    )  # <- annotate() closed here

    # Group items by order for template
    orders_grouped = {}
    for item in qs_items:
        orders_grouped.setdefault(item.order, []).append(item)

    # Superuser-only daily sales
    sales_date  = request.GET.get('sales_date')
    total_sales = None
    if request.user.is_superuser and sales_date:
        total_sales = (
            qs_items
            .filter(order__created_at__date=sales_date)
            .aggregate(sum=Sum('line_total'))['sum']
        ) or Decimal('0.00')

    return render(request, 'orders/orders_report.html', {
        'orders':      orders_grouped,
        'start_date':  start,
        'end_date':    end,
        'sales_date':  sales_date,
        'total_sales': total_sales,
    })



def profit_loss(request):
    form    = ProfitLossForm(request.GET or None)
    revenue = cost = profit = Decimal('0.00')
    details = []

    if form.is_valid():
        sd = form.cleaned_data['start_date']
        ed = form.cleaned_data['end_date']

        # Base queryset
        qs = OrderItem.objects.filter(
            order__created_at__date__gte=sd,
            order__created_at__date__lte=ed
        ).select_related('product', 'order')

        # Annotate each item with line_revenue and line_cost
        qs = qs.annotate(
            line_revenue=ExpressionWrapper(
                F('price') * F('quantity'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            line_cost=ExpressionWrapper(
                F('product__cost_price') * F('quantity'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
        )

        # Sum up totals
        revenue = qs.aggregate(total_rev=Sum('line_revenue'))['total_rev'] or Decimal('0.00')
        cost    = qs.aggregate(total_cost=Sum('line_cost'))['total_cost'] or Decimal('0.00')
        profit  = revenue - cost

        # Build detail rows
        for it in qs.order_by('order__created_at'):
            details.append({
                'date':        it.order.created_at.date(),
                'item':        it.product.name,
                'quantity':    it.quantity,
                'unit_cost':   it.product.cost_price,
                'unit_price':  it.price,
                'line_cost':   it.line_cost,
                'line_revenue':it.line_revenue,
                'line_profit': it.line_revenue - it.line_cost,
            })

    return render(request, 'orders/profit_loss.html', {
        'form':     form,
        'revenue':  revenue,
        'cost':     cost,
        'profit':   profit,
        'details':  details,
    })


def orders_report_pdf(request):
    start = request.GET.get('start_date')
    end   = request.GET.get('end_date')

    qs_orders = Order.objects.filter(is_paid=True)
    if start:
        qs_orders = qs_orders.filter(created_at__date__gte=start)
    if end:
        qs_orders = qs_orders.filter(created_at__date__lte=end)

    qs_items = (
        OrderItem.objects
                 .filter(order__in=qs_orders)
                 .select_related('order', 'product')
                 .annotate(
                     line_total=ExpressionWrapper(
                         F('price') * F('quantity'),  # use price field
                         output_field=DecimalField(max_digits=12, decimal_places=2)
                     )
                 )
    )

    # Write PDF to buffer
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Draw headers
    p.setFont('Helvetica-Bold', 12)
    y = 750
    headers = ['Date', 'Product', 'Qty', 'Price', 'Line Total']
    x_positions = [30, 100, 260, 320, 400]
    for idx, header in enumerate(headers):
        p.drawString(x_positions[idx], y, header)
    p.setFont('Helvetica', 10)
    y -= 20

    # Draw rows with borders
    row_height = 20
    for item in qs_items:
        if y < 50:
            p.showPage()
            p.setFont('Helvetica-Bold', 12)
            y = 750
            for idx, header in enumerate(headers):
                p.drawString(x_positions[idx], y, header)
            p.setFont('Helvetica', 10)
            y -= row_height

        values = [
            item.order.created_at.strftime('%Y-%m-%d'),
            item.product.name[:15],
            str(item.quantity),
            f"{item.price:.2f}",
            f"{item.line_total:.2f}"
        ]
        for idx, val in enumerate(values):
            p.drawString(x_positions[idx], y, val)
        # horizontal border line
        p.line(x_positions[0], y-2, x_positions[-1]+80, y-2)
        y -= row_height

    p.save()
    buffer.seek(0)

    # Return HttpResponse with attachment header
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="orders_report.pdf"'
    return response

