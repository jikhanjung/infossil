from django import forms
from django.forms import ModelForm, inlineformset_factory, modelformset_factory
from .models import Taxon, TaxonRank, TaxonAuthor, Reference, ReferenceAuthor, Author, Journal
from dal import autocomplete

class JournalForm(ModelForm):
    class Meta:
        model = Journal
        fields = ['title_k', 'title_e', 'publisher', 'since', 'issn']

class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ['firstname_k', 'lastname_k', 'firstname_e', 'lastname_e', 'affiliation', 'is_primary', 'redirect_to', 'remarks']



class ReferenceAuthorForm(ModelForm):
    class Meta:
        model = ReferenceAuthor
        fields = ['reference', 'author', 'author_order']
        widgets = {
            'author_order': forms.TextInput(attrs={'size': 3}),
            'author':  autocomplete.ModelSelect2(url='author_autocomplete',attrs={'style':'width:200px'}),
        }

class ReferenceForm(ModelForm):
    class Meta:
        model = Reference
        fields = ['type', 'type2', 'title_e', 'title_k', 'year', 'volume', 'issue', 'pages', 'journal', 'abstract', 'language', 
                    'doi', 'data', 'fossilgroup_macro', 'fossilgroup_micro', 'fossilgroup_ichno', 'remarks']

        textinput_size=60
        textarea_cols=60
        textarea_rows=3
        widgets = {
            'title_e': forms.Textarea(attrs={'cols': textarea_cols, 'rows': textarea_rows}),
            'title_k': forms.Textarea(attrs={'cols': textarea_cols, 'rows': textarea_rows}),
            'abstract': forms.Textarea(attrs={'cols': textarea_cols, 'rows': textarea_rows}),
            'remarks': forms.Textarea(attrs={'cols': textarea_cols, 'rows': textarea_rows}),            
            #'commonname': forms.TextInput(attrs={'size': textinput_size}),
            'journal':  autocomplete.ModelSelect2(url='journal_autocomplete',attrs={'style':'width:600px'}),
        }

class TaxonForm(ModelForm):
    class Meta:
        model = Taxon
        fields = ['name', 'rank', 'parent', 'authorship', 'year', 'sensu', 'remarks']
        textinput_size=60
        textarea_cols=60
        textarea_rows=3
        widgets = {
            'remarks': forms.Textarea(attrs={'cols': textarea_cols, 'rows': textarea_rows}),            
        }

class TaxonAuthorForm(ModelForm):
    class Meta:
        model = TaxonAuthor
        fields = ['taxon', 'author', 'author_order']
        widgets = {
            'author_order': forms.TextInput(attrs={'size': 3}),
            'author':  autocomplete.ModelSelect2(url='author_autocomplete',attrs={'style':'width:200px'}),
        }
