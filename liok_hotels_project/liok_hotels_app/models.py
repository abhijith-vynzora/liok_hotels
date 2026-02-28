from django.db import models
from django.utils.text import slugify


class Property(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, help_text="URL-friendly name (e.g. liok-resort-kerala)") 
    overview = models.TextField(help_text="Full description of the property")
    address = models.CharField(max_length=255) 
    map_embed_code = models.TextField(blank=True, help_text="Paste the Google Maps HTML embed code here")
    whatsapp_number = models.CharField(max_length=20, help_text="Number for the direct booking button (e.g. +919876543210)") 
    contact_phone = models.CharField(max_length=20, blank=True)
    cover_image = models.ImageField(upload_to='properties/covers/')
    amenities_list = models.TextField(help_text="List amenities separated by commas (e.g. Wifi, Pool, Spa, Parking)") 
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RoomCategory(models.Model):
    property = models.ForeignKey(Property, related_name='rooms', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g. Deluxe Suite, Ocean View Villa")
    description = models.TextField(blank=True, help_text="Brief description of the room category")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in your currency")
    max_occupancy = models.IntegerField(default=2)
    image = models.ImageField(upload_to='properties/rooms/')
    
    def __str__(self):
        return f"{self.property.name} - {self.name}"

class NearbyLocation(models.Model):
    property = models.ForeignKey(Property, related_name='nearby_locations', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text="Name of the attraction (e.g. Athirappilly Waterfalls)")
    distance = models.CharField(max_length=50, blank=True, help_text="Distance from property (e.g. '5 km' or '15 min drive')")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="properties/nearby/", blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} (near {self.property.name})"


class Blog(models.Model):
    image = models.ImageField(upload_to="blogs/", help_text="Blog cover image")
    slug = models.SlugField(unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Testimonial(models.Model):
    name = models.CharField(
        max_length=100, help_text="Name of the person giving the testimonial"
    )
    image = models.ImageField(
        upload_to="testimonials/", blank=True, null=True, help_text="Profile picture"
    )
    review = models.TextField(help_text="Customer or client review")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image_fields = ["image"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="images"
    )
    title = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to="gallery/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title if self.title else f"Image {self.id}"


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True) 
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"


class BookingInquiry(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    room_category = models.CharField(max_length=100, blank=True, null=True, help_text="The type of room selected by the guest")

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="bookings")


    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField(default=2)
    
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} - {self.property.name}"