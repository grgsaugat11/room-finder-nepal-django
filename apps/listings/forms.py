from django import forms

from .models import Listing, ListingFacility, ListingDocument


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            "multiple": True
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]

        return single_file_clean(data, initial)


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'property_type',

            'province',
            'district',
            'city',
            'area',
            'ward_number',
            'exact_address',
            'latitude',
            'longitude',

            'monthly_rent',
            'security_deposit',
            'bills_water_included',
            'bills_electricity_included',
            'bills_internet_included',

            'furnished_status',
            'available_date',
            'rules',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write at least 100 characters about the room/property...'
            }),
            'rules': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Example: No loud music after 10 PM, no smoking, etc.'
            }),
            'available_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'latitude': forms.NumberInput(attrs={
                'step': '0.000001',
                'placeholder': 'Example: 27.717245'
            }),
            'longitude': forms.NumberInput(attrs={
                'step': '0.000001',
                'placeholder': 'Example: 85.323959'
            }),
        }


class ListingFacilityForm(forms.ModelForm):
    class Meta:
        model = ListingFacility
        exclude = ['listing']


class ListingDocumentForm(forms.ModelForm):
    class Meta:
        model = ListingDocument
        fields = [
            'citizenship_front',
            'citizenship_back',
            'lalpurja',
            'selfie_with_citizenship',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            for field in self.fields.values():
                field.required = False


class MultipleImageUploadForm(forms.Form):
    images = MultipleFileField(required=True)

    def clean_images(self):
        images = self.files.getlist('images')

        if len(images) < 3:
            raise forms.ValidationError("Please upload at least 3 property images.")

        if len(images) > 15:
            raise forms.ValidationError("You can upload maximum 15 property images.")

        for image in images:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Each image must be less than 5MB.")

            valid_content_types = [
                'image/jpeg',
                'image/png',
                'image/jpg',
                'image/webp',
            ]

            if image.content_type not in valid_content_types:
                raise forms.ValidationError("Only JPG, PNG, and WEBP images are allowed.")

        return images