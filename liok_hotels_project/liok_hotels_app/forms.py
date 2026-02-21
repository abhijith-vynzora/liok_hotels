from django import forms
from django.forms import inlineformset_factory
from .models import (
    Property, RoomCategory, NearbyLocation,
    Blog, Testimonial, Category, GalleryImage,
    ContactMessage, BookingInquiry
)

# ==========================================
# 1. PROPERTY MANAGEMENT FORMS
# ==========================================

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "name", 
            "overview", 
            "address", 
            "map_embed_code", 
            "whatsapp_number", 
            "contact_phone", 
            "cover_image", 
            "amenities_list"
        ]
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 4}),
            'map_embed_code': forms.Textarea(attrs={'rows': 3}),
            'amenities_list': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Wifi, Pool, Spa...'}),
        }


class RoomCategoryForm(forms.ModelForm):
    class Meta:
        model = RoomCategory
        fields = ["property", "name", "description", "price_per_night", "max_occupancy", "image"]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class NearbyLocationForm(forms.ModelForm):
    class Meta:
        model = NearbyLocation
        fields = ["property", "name", "distance", "description", "image"]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["image", "title", "description"]


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "image", "review"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ["category", "title", "image"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "phone", "email", "message"]


class BookingInquiryForm(forms.ModelForm):
    class Meta:
        model = BookingInquiry
        fields = [
            "first_name", "last_name", "phone", "email", 
            "property", "check_in", "check_out", "guests", "message"
        ]
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }