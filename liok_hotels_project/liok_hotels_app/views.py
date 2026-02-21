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

from .models import (
    Property, Blog, Testimonial, Category, GalleryImage,
    ContactMessage, BookingInquiry, NearbyLocation, RoomCategory
)

from .forms import (
    PropertyForm, BlogForm, TestimonialForm,NearbyLocationForm, RoomCategoryForm,
    CategoryForm, GalleryImageForm
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
def view_contacts(request):
    contacts = ContactMessage.objects.all().order_by("-created_at")
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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
            return redirect("admin_pages:testimonial_list")
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