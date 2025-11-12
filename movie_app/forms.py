from django import forms
from .models import Movie

class MovieForm(forms.ModelForm):
    SAVE_CHOICES = [
        ('db', 'Сохранить в базу данных'),
        ('json', 'Сохранить в JSON файл'),
        ('xml', 'Сохранить в XML файл'),
    ]
    
    save_to = forms.ChoiceField(
        choices=SAVE_CHOICES,
        initial='db',
        widget=forms.RadioSelect,
        label="Куда сохранить данные?"
    )
    
    class Meta:
        model = Movie
        fields = ['title', 'director', 'year', 'genre', 'duration', 'rating', 
                 'description', 'cast', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'director': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cast': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0 or rating > 10:
            raise forms.ValidationError("Рейтинг должен быть от 0 до 10")
        return rating
    
    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 1895 or year > 2030:
            raise forms.ValidationError("Год должен быть между 1895 и 2030")
        return year

class JSONUploadForm(forms.Form):
    json_file = forms.FileField(
        label="JSON файл",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    save_to = forms.ChoiceField(
        choices=MovieForm.SAVE_CHOICES,
        initial='db',
        widget=forms.RadioSelect,
        label="Куда сохранить данные?"
    )