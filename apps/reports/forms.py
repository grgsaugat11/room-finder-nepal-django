from django import forms
from .models import ListingReport


class ListingReportForm(forms.ModelForm):
    class Meta:
        model = ListingReport
        fields = [
            'reason',
            'description',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Explain what seems fake, suspicious, or incorrect...'
            })
        }