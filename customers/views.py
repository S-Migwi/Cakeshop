import os
from decimal import Decimal

from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import Product, Order, OrderItem, Contact, Gallery, Supplier
from .forms import ProductForm, OrderItemForm, ContactForm, SupplierForm
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

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


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


def place_order(request):
    if request.method == 'POST':
        form = OrderItemForm(request.POST)
        if form.is_valid():
            #Get or create an order for the user
            order, created = Order.objects.get_or_create(user=request.user, is_paid=False)

            #create the order item
            item = form.save(commit=False)
            item.order = order
            product =item.product

            if product.stock < item.quantity:
                messages.error(request, f"Not enough stock for {product.name}. Only {product.stock} left.")
                return redirect('place_order')

            # calculate price and update stock
            item.price = Decimal(product.price) * item.quantity
            product.stock -= item.quantity
            product.save()

            if isinstance(order.total_price, float):  # If it's a float, convert it to Decimal
                order.total_price = Decimal(order.total_price)

            # Save the order item and update order total
            item.save()
            order.total_price += item.price
            order.save()
            messages.success(request, f"Added {item.quantity} x {product.name} to your order.")
            return redirect('view_order', order.id)
    else:
        form = OrderItemForm()
    return render(request, 'orders/place_order.html', {'form': form})

@login_required
def view_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/view_order.html', {'order': order})


def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, is_paid=False)

    if request.method == 'POST':
        form = OrderItemForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            # Check if the item already exists in the order
            if quantity <= 0:
                messages.error(request, "Quantity must be greater than zero.")
                return redirect('edit_order', order_id=order.id)

                # Check if the item already exists in the order
            order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

            order_item.quantity = quantity
            order_item.price = order_item.product.price * order_item.quantity
            order_item.save()

            # Update order total price
            order.total_price = sum(item.price for item in order.items.all())
            order.save()

            messages.success(request, "Order item updated successfully!")
            return redirect('view_order', order.id)
    else:
        form = OrderItemForm()

    return render(request, 'orders/edit_order.html', {'form': form, 'order': order})


def delete_order(request, order_id):
    # Get the order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        # Delete the order
        order.delete()
        messages.success(request, f"Order {order_id} has been deleted successfully!")
        return redirect('place_order')  # Redirect to a relevant page (e.g., dashboard or order list)

    return render(request, 'orders/confirm_delete.html', {'order': order})

def generate_pdf(request):
    # Create a response object and set the content type to PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="product_report.pdf"'

    # Create a canvas object to generate the PDF
    p = canvas.Canvas(response, pagesize=letter)

    # Set up the title of the PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Product List Report")

    # Set up the table headers
    p.setFont("Helvetica", 12)
    p.drawString(50, 730, "Product Name")
    p.drawString(200, 730, "Description")
    p.drawString(400, 730, "Price")
    p.drawString(500, 730, "Stock")

    # Fetch the product data from the database
    products = Product.objects.all()
    y_position = 710  # Start drawing content just below the headers

    for product in products:
        p.drawString(50, y_position, product.name)
        p.drawString(200, y_position, product.description[:50])  # Truncate the description if it's long
        p.drawString(400, y_position, f"Ksh {product.price}")
        p.drawString(500, y_position, str(product.stock))
        y_position -= 20  # Move down to the next row

        # Add a page if the content overflows
        if y_position < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y_position = 750  # Reset the Y position at the top of the next page

    # Save the PDF document
    p.showPage()
    p.save()
    return response