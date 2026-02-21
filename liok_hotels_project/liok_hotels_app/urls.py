from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'admin_pages'

urlpatterns = [
    
    # ==============================Authentication URLs=========================
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),

    # ==============================dashboard & analytics=========================
    path("dashboard/", views.admin_dashboard, name="admin-dashboard"),

    # ==============================Poperty Management URLs=========================
    path("dashboard/properties/", views.property_list, name="property_list"),
    path("dashboard/properties/add/", views.property_create, name="property_create"),
    path("dashboard/properties/update/<int:pk>/", views.property_update, name="property_update"),
    path("dashboard/properties/delete/<int:pk>/", views.property_delete, name="property_delete"),

    # ==============================nearby locations=========================
    path("dashboard/nearby/", views.nearby_location_list, name="nearby_list"),
    path("dashboard/nearby/add/", views.nearby_location_create, name="nearby_create"),
    path("dashboard/nearby/update/<int:pk>/", views.nearby_location_update, name="nearby_update"),
    path("dashboard/nearby/delete/<int:pk>/", views.nearby_location_delete, name="nearby_delete"),

    # ==============================Room Categories=========================
    path("dashboard/rooms/", views.room_category_list, name="room_list"),
    path("dashboard/rooms/add/", views.room_category_create, name="room_create"),
    path("dashboard/rooms/update/<int:pk>/", views.room_category_update, name="room_update"),
    path("dashboard/rooms/delete/<int:pk>/", views.room_category_delete, name="room_delete"),

    # ==============================booking & contact management=========================
    path("dashboard/bookings/", views.view_bookings, name="view_bookings"),
    path("dashboard/bookings/delete/<int:pk>/", views.delete_booking, name="delete_booking"),
    path("dashboard/contacts/", views.view_contacts, name="view_contacts"),
    path("dashboard/contacts/delete/<int:pk>/", views.delete_contact, name="delete_contact"),


   # ==============================blogs & categories management=========================
    path("dashboard/blogs/", views.blog_list, name="blog_list"),
    path("dashboard/blogs/add/", views.blog_create, name="blog_create"),
    path("dashboard/blogs/update/<int:pk>/", views.blog_update, name="blog_update"),
    path("dashboard/blogs/delete/<int:pk>/", views.blog_delete, name="blog_delete"),


    # ==============================gallery & images management=========================
    path("dashboard/gallery/", views.gallery_images, name="list_image"),
    path("dashboard/gallery/add/", views.add_image, name="add_image"),
    path("dashboard/gallery/delete/<int:image_id>/", views.delete_image, name="delete_image"),

    path("dashboard/categories/", views.category_list, name="category_list"),
    path("dashboard/categories/add/", views.add_category, name="add_category"),
    path("dashboard/categories/update/<int:pk>/", views.update_category, name="update_category"),
    path("dashboard/categories/delete/<int:pk>/", views.delete_category, name="delete_category"),


    # ==============================testimonials & reviews management=========================
    path("dashboard/testimonials/", views.testimonial_list, name="review_list"),
    path("dashboard/testimonials/add/", views.testimonial_create, name="testimonial_create"),
    path("dashboard/testimonials/<int:pk>/edit/",views.testimonial_update,name="testimonial_update"),
    path("dashboard/testimonials/<int:pk>/delete/",views.testimonial_delete,name="testimonial_delete"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)