from django import forms
from .models import Product, OrderItem, Contact, Supplier


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'cost_price', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product name'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Enter Product Description'}),
            'cost_price': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Product Cost Price'}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'placeholder': 'Enter the Product Price'}),
            'stock': forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'placeholder': 'Enter the Product Stock'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class OrderItemForm(forms.ModelForm):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class ProfitLossForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="From"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="To"
    )

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'option', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Phone Number'}),
            'option': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select an option'),
                ('1', 'Order an accessory'),
                ('2', 'Order a cake'),
                ('3', 'Request baker information'),
            ]),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your message'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Please use a valid email address.")
        return email

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'address', 'company_name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please enter Suppliers name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Suppliers Email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Suppliers Phone Number'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Suppliers Address Number'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Suppliers Company Name'}),
        }

