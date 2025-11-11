from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Medicine, CartItem


# Show all medicines
@login_required
def medicine_list(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    medicines = Medicine.objects.filter(is_available=True)
    
    if search:
        medicines = medicines.filter(name__icontains=search)
    
    if category:
        medicines = medicines.filter(category=category)
    
    categories = Medicine.objects.values_list('category', flat=True).distinct()
    
    context = {
        'medicines': medicines,
        'search': search,
        'category': category,
        'categories': categories
    }
    return render(request, "medical_store/medicine_list.html", context)


# Show cart
@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total() for item in cart_items)
    
    # Calculate discount (10% for orders over ₹500)
    discount = 0
    if total_price > 500:
        discount = total_price * 0.1
    
    final_total = total_price - discount
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount,
        'final_total': final_total,
        'cart_count': cart_items.count()
    }
    return render(request, "medical_store/cart.html", context)


# Add to cart
@login_required
def add_to_cart(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)

    if not medicine.is_in_stock():
        messages.error(request, f'{medicine.name} is currently out of stock.')
        return redirect('medicine_list')

    cart_item, created = CartItem.objects.get_or_create(
        medicine=medicine,
        user=request.user,
        defaults={'quantity': 1, 'price': medicine.price}
    )

    if not created:
        if cart_item.quantity >= medicine.stock_quantity:
            messages.error(request, f'Not enough stock available for {medicine.name}.')
            return redirect('medicine_list')
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'{medicine.name} quantity updated in cart!')
    else:
        messages.success(request, f'{medicine.name} added to cart successfully!')
    
    return redirect('view_cart')


# Remove from cart
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    medicine_name = cart_item.medicine.name
    cart_item.delete()
    
    messages.success(request, f'{medicine_name} removed from cart.')
    return redirect("view_cart")
