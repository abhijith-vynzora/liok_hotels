from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json
from django.db.models.functions import Lower
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Property, Blog, Testimonial, Category, GalleryImage,
    ContactMessage, BookingInquiry, NearbyLocation, RoomCategory
)

from .forms import (
    PropertyForm, BlogForm, TestimonialForm,NearbyLocationForm, RoomCategoryForm,
    CategoryForm, GalleryImageForm, BookingInquiryForm, ContactForm
)

# =================ADMIIN AUTHENTICATION & DASHBOARD VIEWS==========================

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Both fields are required.")
            return render(request, "authenticate/login.html")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("admin_pages:admin-dashboard")
        else:
            messages.error(request, "Invalid credentials or unauthorized access.")

    return render(request, "authenticate/login.html")


@login_required(login_url="admin_login")
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("admin_pages:admin_login")


# ==========================================
# 2. DASHBOARD HOME
# ==========================================

# In views.py, update the admin_dashboard function
@login_required(login_url="admin_login")
def admin_dashboard(request):
    # ... existing stats code ...
    stats = {
        'total_bookings': BookingInquiry.objects.count(),
        'pending_inquiries': BookingInquiry.objects.filter(status='pending').count(),
        'total_properties': Property.objects.count(),
        'contacts_count': ContactMessage.objects.count(),
    }

    current_year = timezone.now().year

    # 1. Existing Monthly Data logic
    booking_data = BookingInquiry.objects.filter(
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    booking_labels = [x['month'].strftime('%b') for x in booking_data]
    booking_counts = [x['count'] for x in booking_data]

    # 2. NEW LOGIC: Status Breakdown
    # Group by status and count
    status_qs = BookingInquiry.objects.values('status').annotate(count=Count('id'))
    
    # Prepare lists for Chart.js
    status_labels = [item['status'].capitalize() for item in status_qs] 
    status_counts = [item['count'] for item in status_qs]

    recent_bookings = BookingInquiry.objects.select_related('property').order_by('-created_at')[:5]
    recent_contacts = ContactMessage.objects.order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'recent_contacts': recent_contacts,
        'booking_labels': json.dumps(booking_labels),
        'booking_counts': json.dumps(booking_counts),
        # Pass new data to template
        'status_labels': json.dumps(status_labels), 
        'status_counts': json.dumps(status_counts),
    }

    return render(request, "admin_pages/admin-dashboard.html", context)


# ==========================================
# 3. PROPERTY MANAGEMENT VIEWS
# ==========================================

@login_required(login_url="admin_login")
def property_list(request):
    properties_qs = Property.objects.all().order_by("-created_at")
    paginator = Paginator(properties_qs, 6)
    page_number = request.GET.get("page")
    properties = paginator.get_page(page_number)

    return render(request, "admin_pages/property_list.html", {"properties": properties})


@login_required(login_url="admin_login")
def property_create(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Property created successfully!")
            return redirect("admin_pages:property_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PropertyForm()

    return render(request, "admin_pages/add_property.html", {"form": form})


@login_required(login_url="admin_login")
def property_update(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Property updated successfully!")
            return redirect("admin_pages:property_list")
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, "admin_pages/add_property.html", {
        "form": form,
        "property": property_obj
    })


@login_required(login_url="admin_login")
def property_delete(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == "POST":
        property_obj.delete()
        messages.success(request, "Property deleted successfully!")
    return redirect("admin_pages:property_list")


# ==========================================
# 4. BOOKINGS & INQUIRIES
# ==========================================

@login_required(login_url="admin_login")
def view_bookings(request):
    bookings = BookingInquiry.objects.all().order_by("-created_at")
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin_pages/view_bookings.html", {"bookings": page_obj})

@login_required(login_url="admin_login")
def delete_booking(request, pk):
    booking = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Booking record deleted.")
    return redirect("admin_pages:view_bookings")

@login_required(login_url="admin_login")
@login_required(login_url="admin_login")
def view_contacts(request):
    contacts_list = ContactMessage.objects.all().order_by("-created_at")
    paginator = Paginator(contacts_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Key must be 'contacts' to match the template loop
    return render(request, "admin_pages/view_contacts.html", {"contacts": page_obj})

@login_required(login_url="admin_login")
def delete_contact(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        contact.delete()
    return redirect("admin_pages:view_contacts")


# ==========================================
# 5. BLOGS
# ==========================================

@login_required(login_url="admin_login")
def blog_list(request):
    blogs_qs = Blog.objects.all().order_by("-created_at")
    paginator = Paginator(blogs_qs, 6)
    page_number = request.GET.get("page")
    blogs = paginator.get_page(page_number)

    return render(request, "admin_pages/blog_list.html", {"blogs": blogs})

@login_required(login_url="admin_login")
def blog_create(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post created!")
            return redirect("admin_pages:blog_list")
    else:
        form = BlogForm()
    return render(request, "admin_pages/create_blog.html", {"form": form})

@login_required(login_url="admin_login")
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated!")
            return redirect("admin_pages:blog_list")
    else:
        form = BlogForm(instance=blog)
    return render(request, "admin_pages/create_blog.html", {"form": form, "blog": blog})

@login_required(login_url="admin_login")
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted.")
    return redirect("admin_pages:blog_list")


#==========================================
# 6. GALLERY (Updated)
# ==========================================

@login_required(login_url="admin_login")
def gallery_images(request):
    categories = Category.objects.all().prefetch_related("images")

    category_pages = {}
    for category in categories:
        images_qs = category.images.all().order_by("-uploaded_at")
        paginator = Paginator(images_qs, 8)  # 8 images per page
        page_number = request.GET.get(f"page_{category.id}", 1)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        category_pages[category.id] = page_obj

    return render(
        request,
        "admin_pages/image_list.html",
        {
            "categories": categories,
            "category_pages": category_pages,
        },
    )

@login_required(login_url="admin_login")
def add_image(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        category = Category.objects.get(id=category_id)
        files = request.FILES.getlist("images")

        for file in files:
            GalleryImage.objects.create(
                category=category,
                title=file.name,
                image=file,
            )
        # Message already existed here, ensuring it runs
        messages.success(request, "Images uploaded successfully!")
        return redirect("admin_pages:list_image")
        
    return render(request, "admin_pages/add_image.html", {"categories": categories})

@login_required(login_url="admin_login")
def delete_image(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)

    if request.method == "POST":
        image.delete()
        messages.success(request, "Image deleted successfully!")
        return redirect("admin_pages:list_image")

    return render(request, "admin_pages/image_list.html", {"image": image})


@login_required(login_url="admin_login")
def category_list(request):
    categories = Category.objects.all().order_by("-created_at")
    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    categories = paginator.get_page(page_number)
    return render(request, "admin_pages/category_list.html", {"categories": categories})


@login_required(login_url="admin_login")
def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            # ADDED: Success message
            messages.success(request, "Category created successfully!") 
            return redirect("admin_pages:category_list")
    return render(request, "admin_pages/add_category.html")


@login_required(login_url="admin_login")
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.name = request.POST.get("name")
        category.save()
        # ADDED: Success message
        messages.success(request, "Category updated successfully!")
        return redirect("admin_pages:category_list")
    
    # FIXED: Added namespace 'admin_pages:'
    return redirect("admin_pages:category_list") 


@login_required(login_url="admin_login")
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        # ADDED: Success message
        messages.success(request, "Category deleted successfully!") 
        return redirect("admin_pages:category_list")
    return redirect("admin_pages:category_list")



# ==========================================testimonials & reviews management=========================

@login_required(login_url="admin_login")
def testimonial_list(request):
    testimonials_list = Testimonial.objects.all().order_by(Lower("name"))
    paginator = Paginator(testimonials_list, 6)
    page_number = request.GET.get("page")
    testimonials = paginator.get_page(page_number)

    return render(
        request, "admin_pages/review_list.html", {"testimonials": testimonials}
    )


@login_required(login_url="admin_login")
def testimonial_create(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial added successfully!")
            return redirect("admin_pages:review_list")
    else:
        form = TestimonialForm()
    return render(request, "admin_pages/create_review.html", {"form": form})


@login_required(login_url="admin_login")
def testimonial_update(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonial updated successfully!")
            return redirect("admin_pages:review_list")
    else:
        form = TestimonialForm(instance=testimonial)
    return render(
        request,
        "admin_pages/review_list.html",
        {"form": form, "testimonial": testimonial},
    )


@login_required(login_url="admin_login")
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, "Testimonial deleted successfully!")
        return redirect("admin_pages:review_list")
    return render(request, "admin_pages/review_list.html", {"testimonial": testimonial})

# ==========================================
# 8. NEARBY LOCATIONS MANAGEMENT
# ==========================================

@login_required(login_url="admin_login")
def nearby_location_list(request):
    properties = Property.objects.prefetch_related('nearby_locations').all()
    return render(request, "admin_pages/nearby_location_list.html", {"properties": properties})

@login_required(login_url="admin_login")
def nearby_location_create(request):
    if request.method == "POST":
        form = NearbyLocationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Nearby location added successfully!")
            return redirect("admin_pages:nearby_list")
    else:
        form = NearbyLocationForm()
    return render(request, "admin_pages/add_nearby_location.html", {"form": form})

@login_required(login_url="admin_login")
def nearby_location_update(request, pk):
    location = get_object_or_404(NearbyLocation, pk=pk)
    if request.method == "POST":
        form = NearbyLocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, "Location updated successfully!")
            return redirect("admin_pages:nearby_list")
    else:
        form = NearbyLocationForm(instance=location)
    return render(request, "admin_pages/add_nearby_location.html", {"form": form, "location": location})

@login_required(login_url="admin_login")
def nearby_location_delete(request, pk):
    location = get_object_or_404(NearbyLocation, pk=pk)
    if request.method == "POST":
        location.delete()
        messages.success(request, "Location removed.")
    return redirect("admin_pages:nearby_list")

# ==========================================
# 9. ROOM CATEGORY MANAGEMENT (Standalone)
# ==========================================

@login_required(login_url="admin_login")
def room_category_list(request):
    properties = Property.objects.prefetch_related('rooms').all()
    return render(request, "admin_pages/room_category_list.html", {"properties": properties})

@login_required(login_url="admin_login")
def room_category_create(request):
    if request.method == "POST":
        form = RoomCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Room Category added successfully!")
            return redirect("admin_pages:room_list")
        else:
            messages.error(request, "Error: Please check the form for missing fields.")
    else:
        form = RoomCategoryForm()
    
    return render(request, "admin_pages/add_room_category.html", {"form": form})

@login_required(login_url="admin_login")
def room_category_update(request, pk):
    room = get_object_or_404(RoomCategory, pk=pk)
    if request.method == "POST":
        form = RoomCategoryForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room Category updated!")
            return redirect("admin_pages:room_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RoomCategoryForm(instance=room)
    return render(request, "admin_pages/add_room_category.html", {"form": form, "room": room})

@login_required(login_url="admin_login")
def room_category_delete(request, pk):
    room = get_object_or_404(RoomCategory, pk=pk)
    if request.method == "POST":
        room.delete()
        messages.success(request, "Room Category deleted.")
    return redirect("admin_pages:room_list")


# ==========================frontend pages==============================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import (
    Property, RoomCategory, NearbyLocation,
    Blog, Testimonial, Category, GalleryImage,
    ContactMessage, BookingInquiry
)


# Home Page
def home(request):
    properties = Property.objects.all()
    testimonials = Testimonial.objects.all()[:5]
    blogs = Blog.objects.all()[:3]

    context = {
        "properties": properties,
        "testimonials": testimonials,
        "blogs": blogs,
    }
    return render(request, "frontend/index4.html", context)

def about(request):
    # Fetch data to populate the sliders in about.html
    testimonials = Testimonial.objects.all()[:5]
    
    # If you have a Team model, you would fetch it here. 
    # For now, we'll just render the page.
    context = {
        "testimonials": testimonials,
    }
    return render(request, "frontend/about.html", context)

# All Properties Listing (The page you shared)
def properties_all(request):
    properties = Property.objects.all().order_by("-created_at")
    testimonials = Testimonial.objects.all()[:5]
    return render(request, "frontend/properties.html", {"properties": properties, "testimonials": testimonials})

# Property Detail Page
def property_detail(request, slug):
    property_obj = get_object_or_404(Property, slug=slug)
    rooms = property_obj.rooms.all()
    nearby = property_obj.nearby_locations.all()

    # Convert the textarea string into a clean Python list
    # This handles extra spaces if a user types 'Wifi,  Pool'
    raw_amenities = property_obj.amenities_list.split(',')
    amenities = [item.strip() for item in raw_amenities if item.strip()]

    context = {
        "property": property_obj,
        "rooms": rooms,
        "nearby": nearby,
        "amenities": amenities,
    }
    return render(request, "frontend/property-details.html", context)


# Rooms Page (All Rooms)
def rooms(request):
    rooms = RoomCategory.objects.select_related("property")
    return render(request, "frontend/rooms.html", {"rooms": rooms})


# Single Room Detail
def room_detail(request, pk):
    room = get_object_or_404(RoomCategory, pk=pk)
    return render(request, "frontend/room-details.html", {"room": room})

# Gallery Page
def gallery(request):
    categories = Category.objects.all()
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    
    context = {
        'categories': categories,
        'images': images,
    }
    return render(request, "frontend/gallery.html", context)

def contact(request):
    if request.method == "POST":
        if not all([request.POST.get("first_name"), 
                    request.POST.get("last_name"), 
                    request.POST.get("phone")]):
            messages.error(request, "Please fill in all required fields.")
            # Redirect back to the referring page, or fallback to the contact page
            return redirect(request.META.get('HTTP_REFERER', 'admin_pages:contact')) 
        
        ContactMessage.objects.create(
            first_name=request.POST.get("first_name").strip(),
            last_name=request.POST.get("last_name").strip(),
            phone=request.POST.get("phone").strip(),
            email=request.POST.get("email", "").strip() or None,
            message=request.POST.get("message", "").strip()
        )
        
        messages.success(request, "Your message has been sent successfully!")
        # Redirect back to the referring page (e.g., /news/ or /property/...)
        return redirect(request.META.get('HTTP_REFERER', 'admin_pages:contact')) 
    
    return render(request, "frontend/contact.html")

# def contact(request):
#     if request.method == "POST":
#         if not all([request.POST.get("first_name"), 
#                     request.POST.get("last_name"), 
#                     request.POST.get("phone")]):
#             messages.error(request, "Please fill in all required fields.")
#             return redirect("admin_pages:contact")  # Add namespace
        
#         ContactMessage.objects.create(
#             first_name=request.POST.get("first_name").strip(),
#             last_name=request.POST.get("last_name").strip(),
#             phone=request.POST.get("phone").strip(),
#             email=request.POST.get("email", "").strip() or None,
#             message=request.POST.get("message", "").strip()
#         )
        
#         messages.success(request, "Your message has been sent successfully!")
#         return redirect("admin_pages:contact")  # Add namespace
    
#     return render(request, "frontend/contact.html")

# def booking_view(request):
#     if request.method == "POST":
#         # Get data from the form
#         first_name = request.POST.get("first_name")
#         last_name = request.POST.get("last_name")
#         phone = request.POST.get("phone")
#         email = request.POST.get("email")
#         property_id = request.POST.get("property")
        
#         # NEW: Capture the room category selected in the dropdown
#         room_category = request.POST.get("room_category")
        
#         check_in = request.POST.get("check_in")
#         check_out = request.POST.get("check_out")
#         guests = request.POST.get("guests", 2)
#         message_text = request.POST.get("message")

#         # Basic Validation
#         if not all([first_name, last_name, phone, property_id, check_in, check_out]):
#             messages.error(request, "Please fill in all required fields.")
#             return redirect("admin_pages:book_now")

#         try:
#             # Save to database using your updated BookingInquiry model
#             property_obj = get_object_or_404(Property, id=property_id)
#             BookingInquiry.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 phone=phone,
#                 email=email if email else None,
#                 property=property_obj,
                
#                 # NEW: Save the room category to the database
#                 room_category=room_category,
                
#                 check_in=check_in,
#                 check_out=check_out,
#                 guests=int(guests),
#                 message=message_text,
#                 status='pending'
#             )
#             messages.success(request, "Your booking inquiry has been submitted successfully!")
#             return redirect("admin_pages:book_now")
            
#         except Exception as e:
#             messages.error(request, f"An error occurred: {e}")
#             return redirect("admin_pages:book_now")

#     # GET request: Show the form and provide the list of properties
#     properties = Property.objects.all()
#     return render(request, "frontend/booking.html", {"properties": properties})


from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
def booking_view(request):
    if request.method == "POST":
        # 1. Capture Form Data
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email_address = request.POST.get("email", "").strip()
        property_id = request.POST.get("property")
        room_category = request.POST.get("room_category")
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")
        
        # New Guest Fields
        adults = request.POST.get("adults", 1)
        children_8_12 = request.POST.get("children_8_12", 0)
        children_13_plus = request.POST.get("children_13_plus", 0)
        
        message_text = request.POST.get("message", "").strip()
        
        # NEW: Get the source page
        source_page = request.POST.get("source_page", "booking")  # Default to booking page

        # Basic Validation
        if not all([first_name, last_name, phone, property_id, check_in, check_out]):
            messages.error(request, "Please fill in all required fields.")
            
            # Redirect based on source
            if source_page == "property_detail":
                property_obj = get_object_or_404(Property, id=property_id)
                return redirect('admin_pages:property_detail', slug=property_obj.slug)
            return redirect("admin_pages:book_now")

        try:
            # 2. Save to Database
            property_obj = get_object_or_404(Property, id=property_id)
            
            inquiry = BookingInquiry.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email_address if email_address else None,
                property=property_obj,
                room_category=room_category,
                check_in=check_in,
                check_out=check_out,
                adults=int(adults),
                children_8_12=int(children_8_12),
                children_13_plus=int(children_13_plus),
                message=message_text,
                status='pending'
            )

            # 3. Email Logic (keeping your existing code)
            subject = f"New Booking Inquiry - {first_name} {last_name}"
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"></head>
            <body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                                <tr>
                                    <td style="background:#C5A880; padding:30px; text-align:center;">
                                        <h2 style="margin:0; color:#ffffff;">New Booking Inquiry</h2>
                                        <p style="margin:5px 0 0; color:#f9f9f9; font-size:14px;">{property_obj.name}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:30px;">
                                        <p style="color:#555; font-size:15px; margin-bottom:20px;">A new booking inquiry has been submitted through the Liok Hotels website.</p>
                                        
                                        <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e0e0; border-radius:6px; font-size:14px;">
                                            <tr>
                                                <td style="padding:12px; font-weight:bold; width:40%; border-bottom:1px solid #eee;">Guest Name</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{first_name} {last_name}</td>
                                            </tr>
                                            
                                            <tr style="background:#f8f9fa;">
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Property</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{property_obj.name}</td>
                                            </tr>

                                            <tr>
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Phone</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{phone}</td>
                                            </tr>

                                            <tr style="background:#f8f9fa;">
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Email</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{email_address}</td>
                                            </tr>

                                            <tr>
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Dates</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{check_in} to {check_out}</td>
                                            </tr>

                                            <tr style="background:#f8f9fa;">
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Room Category</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{room_category or 'Not Selected'}</td>
                                            </tr>
                                            
                                            <tr>
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Adults</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{adults}</td>
                                            </tr>

                                            <tr style="background:#f8f9fa;">
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Children (8-12)</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{children_8_12}</td>
                                            </tr>

                                            <tr>
                                                <td style="padding:12px; font-weight:bold; border-bottom:1px solid #eee;">Children (13+)</td>
                                                <td style="padding:12px; border-bottom:1px solid #eee;">{children_13_plus}</td>
                                            </tr>
                                        </table>
                                        
                                        <div style="margin-top:25px;">
                                            <p style="font-weight:bold; margin-bottom:5px;">Message:</p>
                                            <p style="background:#f9f9f9; padding:15px; border-radius:4px; color:#555;">{message_text}</p>
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="background:#333; padding:20px; text-align:center;">
                                        <p style="margin:0; font-size:13px; color:#aaa;">&copy; {timezone.now().year} Liok Hotels Admin System</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            
            # Send Email
            plain_message = strip_tags(html_message)
            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER]
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            messages.success(request, "Your booking inquiry has been submitted successfully!")
            
            # Redirect based on source page
            if source_page == "property_detail":
                return redirect('admin_pages:property_detail', slug=property_obj.slug)
            
            return redirect("admin_pages:book_now")
            
        except Exception as e:
            print(f"Booking Error: {e}") 
            messages.error(request, "An error occurred. Please try again.")
            
            # Redirect based on source page
            if source_page == "property_detail":
                property_obj = get_object_or_404(Property, id=property_id)
                return redirect('admin_pages:property_detail', slug=property_obj.slug)
            
            return redirect("admin_pages:book_now")

    # GET request: Show form
    properties = Property.objects.all()
    return render(request, "frontend/booking.html", {"properties": properties})


def nearby_attractions_view(request):
    # Fetch all properties for the category filter buttons
    properties = Property.objects.all()
    
    # Fetch all nearby locations and prefetch property data for performance
    nearby_locations = NearbyLocation.objects.select_related('property').all()
    
    context = {
        'properties': properties,
        'nearby_locations': nearby_locations,
    }
    
    return render(request, "frontend/nearby.html", context)

def frontend_blog_list(request):
    # 1. Main Blog List (Ordered by newest first)
    all_blogs = Blog.objects.all().order_by("-created_at")
    
    # 2. Sidebar Data: Get the 3 most recent posts
    recent_posts = all_blogs[:3]

    # 3. Pagination (Show 4 posts per page)
    paginator = Paginator(all_blogs, 4)
    page_number = request.GET.get("page")
    blogs = paginator.get_page(page_number)

    context = {
        "blogs": blogs,
        "recent_posts": recent_posts,
    }
    
    return render(request, "frontend/news.html", context)

def frontend_blog_detail(request, slug):
    # 1. Fetch the single blog post requested
    blog = get_object_or_404(Blog, slug=slug)
    
    # 2. Sidebar Data: Fetch the 3 most recent posts 
    # (We need this context so the sidebar on the detail page isn't empty)
    recent_posts = Blog.objects.all().order_by("-created_at")[:3]
    
    context = {
        "blog": blog,
        "recent_posts": recent_posts,
    }
    
    return render(request, "frontend/news2.html", context)