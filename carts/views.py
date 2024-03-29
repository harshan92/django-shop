from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from carts.models import Cart, CartItem
from store.models import Product, Variation
from django.shortcuts import get_object_or_404, redirect, render

# Create your views here.
def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request, product_id):
    product=Product.objects.get(id=product_id)
    product_variations=[]
    if request.method=='POST':
        for item in request.POST:
            key=item
            value=request.POST[key]

            try:
                variation=Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
                print(variation)
            except:
                pass
   
    
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exist=CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exist:
        cart_item=CartItem.objects.filter(product=product, cart=cart)
        # exsiting varition db
        # current va
        # item id
        ex_var_list=[]
        id=[]
        for item in cart_item:
            existing_variation=item.variations.all()
            ex_var_list.append(list(existing_variation))
            id.append(item.id)

        print(ex_var_list)

        if product_variations in ex_var_list:
            # increase thr existing cart quantity
            index=ex_var_list.index(product_variations)
            item_id=id[index]
            item=CartItem.objects.get(product=product, id=item_id)
            item.quantity +=1
            item.save()
        else:
            # create new cart 
            item=CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variations)>0:
                item.variations.clear()
                item.variations.add(*product_variations)
                # cart_item.quantity+=1
                item.save()
    else:
        cart_item=CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )     
        if len(product_variations)>0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product, id=product_id)
    try:
        cart_item=CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity-=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product, id=product_id)
    cart_item=CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=0):
    try:
        tax=0
        grand_total=0
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price *cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(total*2)/100
        grand_total=total+tax
    except ObjectDoesNotExist:
        pass #just ignore

    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    # return HttpResponse(total)
    return render(request, 'store/cart.html', context)