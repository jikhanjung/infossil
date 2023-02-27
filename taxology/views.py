from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Taxon, TaxonRank, TaxonAuthor, Author, Reference
from .forms import TaxonForm, TaxonAuthorForm, AuthorForm, ReferenceForm, ReferenceAuthorForm
from django.urls import reverse, reverse_lazy
import json

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

ITEMS_PER_PAGE = 20

def get_user_obj(request):
    user_obj = None
    if request.user.is_authenticated:
        user_obj = request.user
    return user_obj

def index(request):
    return HttpResponseRedirect(reverse('taxon_list'))
    return HttpResponse("Hello, world. You're at the taxology index.")


def author_list(request):
    user_obj = get_user_obj( request )

    order_by = request.GET.get('order_by', 'abbreviation_e')
    filter1 = request.GET.get('filter1','')
    #print(order_by, filter1, filter2)
    order_by_list = []
    #if order_by != 'title':
    if order_by.find('abbreviation') > -1:
        if order_by[0] == '-':
            order_by_list.append('-abbreviation_e')
            order_by_list.append('-abbreviation_k')
        else:
            order_by_list.append('abbreviation_e')
            order_by_list.append('abbreviation_k')
    #print(order_by_list,order_by)

    au_list = Author.objects.all()
    if filter1 != '':
        au_list = au_list.filter(Q(abbreviation_e__contains=filter1)|Q(abbreviation_k__contains=filter1)|Q(affiliation__contains=filter1)).distinct()

    author_list = au_list.order_by(*order_by_list)

    #author_list = Author.objects.order_by('lastname_e', 'firstname_e','lastname_k','firstname_k')
    paginator = Paginator(author_list, ITEMS_PER_PAGE) # Show ITEMS_PER_PAGE contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'taxology/author_list.html', {'author_list': author_list, 'page_obj': page_obj, 'user_obj': user_obj,'order_by': order_by, 'filter1': filter1})

def author_detail(request,pk):
    user_obj = get_user_obj( request )

    author = get_object_or_404(Author, pk=pk)
    pk_list = [pk]

    if author.is_primary:
        for aka in author.also_known_as.all():
            pk_list.append(aka.id)
    
    reference_list = [] #[ ra.reference for ra in ReferenceAuthor.objects.filter(author__in=pk_list).order_by('reference__year') ]

    return render(request, 'taxology/author_detail.html', {'author': author, 'reference_list': reference_list, 'user_obj': user_obj} )

#@login_required(login_url=LOGIN_URL)
def author_add(request):
    user_obj = get_user_obj( request )
    # if this is a POST request we need to process the form data
    operation = "New"
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AuthorForm(request.POST)

        #form = AuthorForm(request.POST,instance=author)
        # check whether it's valid:
        if form.is_valid():
            author = form.save(commit=False)
            author.created_by = user_obj.username
            author.generate_abbreviation()
            author.save()
            return HttpResponseRedirect(reverse('author_detail',args=(form.instance.id,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AuthorForm()
        #form = AuthorForm(instance=author)

    return render(request, 'taxology/author_form.html', {'form': form,'op':operation, 'user_obj': user_obj})

#@login_required(login_url=LOGIN_URL)
def author_edit(request,pk):
    user_obj = get_user_obj( request )
    # if this is a POST request we need to process the form data
    author=None
    author = get_object_or_404(Author, pk=pk)
    operation = "Edit"

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AuthorForm(request.POST,instance=author)

        #form = AuthorForm(request.POST,instance=author)
        # check whether it's valid:
        if form.is_valid():
            author = form.save(commit=False)
            author.modified_by = user_obj.username
            author.generate_abbreviation()
            author.save()
            return HttpResponseRedirect(reverse('author_detail',args=(form.instance.id,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AuthorForm(instance=author)
        #form = AuthorForm(instance=author)

    return render(request, 'taxology/author_form.html', {'form': form,'op':operation, 'user_obj': user_obj})

#@login_required(login_url=LOGIN_URL)
def author_delete(request, pk):
    user_obj = get_user_obj( request )
    author = get_object_or_404(Author, pk=pk)
    author.delete()
    return HttpResponseRedirect(reverse('author_list'))


def taxon_list(request):
    user_obj = get_user_obj( request )
    #reference = get_object_or_404(Reference, pk=reference_id)

    filter1 = request.GET.get('filter1')
    taxon_list = Taxon.objects.all()

    if filter1:
        taxon_list = taxon_list.filter(Q(name__contains=filter1)).distinct()
        #print(ref_list)

    taxon_list = taxon_list.order_by("name")


    #taxon_list = Taxon.objects.order_by('scientific_name')
    paginator = Paginator(taxon_list, ITEMS_PER_PAGE) # Show ITEMS_PER_PAGE contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'taxology/taxon_list.html', {'taxon_list': taxon_list, 'page_obj': page_obj, 'user_obj': user_obj,'filter1':filter1})

def taxon_detail(request,pk):
    user_obj = get_user_obj( request )
    taxon = get_object_or_404(Taxon, pk=pk)
    children_list = taxon.children.all()
    return render(request, 'taxology/taxon_detail.html', {'taxon': taxon, 'user_obj': user_obj, 'children_list': children_list} )

#@login_required(login_url=LOGIN_URL)
def taxon_add(request):
    user_obj = get_user_obj( request )
    # if this is a POST request we need to process the form data
    taxon = None
    operation = "New"
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TaxonForm(request.POST)
        AuthorFormSet = inlineformset_factory(Taxon, TaxonAuthor, form=TaxonAuthorForm)
        author_formset = AuthorFormSet(request.POST, instance=taxon)
        # check whether it's valid:
        if form.is_valid():
            print("form valid")
            #print(form.instance
            taxon = form.save()
            return HttpResponseRedirect(reverse('taxon_list'))
            #taxon.save()
        else:
            print("form invalid")
            print(form.errors)
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaxonForm()
        AuthorFormSet = inlineformset_factory(Taxon,TaxonAuthor, form=TaxonAuthorForm, extra=5)
        author_formset = AuthorFormSet(queryset=TaxonAuthor.objects.none())
        #print(author_formset.management_form)

    return render(request, 'taxology/taxon_form.html', {'form': form,'op':operation,'author_formset':author_formset, 'user_obj': user_obj})

#@login_required(login_url=LOGIN_URL)
def taxon_edit(request,pk):
    user_obj = get_user_obj( request )
    # if this is a POST request we need to process the form data
    taxon = None
    taxon = get_object_or_404(Taxon, pk=pk)
    operation = "Edit"
    #print("ref edit")
    if request.method == 'POST':    
        #print("ref edit post")
        # create a form instance and populate it with data from the request:
        form = TaxonForm(request.POST,request.FILES,instance=taxon)
        AuthorFormSet = inlineformset_factory(Taxon, TaxonAuthor, form=TaxonAuthorForm)
        author_formset = AuthorFormSet(request.POST, instance=taxon)

        #form = taxonForm(request.POST,instance=taxon)
        # check whether it's valid:
        if form.is_valid():
            #print("form valid")
            taxon = form.save()
            return HttpResponseRedirect(reverse('taxon_detail',args=(taxon.id,)))
        else:
            print("form invalid")
            #print(form.errors)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TaxonForm(instance=taxon)

    return render(request, 'taxology/taxon_form.html', {'form': form,'op':operation,'user_obj': user_obj})

#@login_required(login_url=LOGIN_URL)
def taxon_delete(request, pk):
    user_obj = get_user_obj( request )
    sciname = get_object_or_404(Taxon, pk=pk)
    sciname.delete()
    return HttpResponseRedirect(reverse('taxon_list'))

def taxon_view(request, pk=None):
    user_obj = get_user_obj( request )
    if pk is None:
        taxon = Taxon.objects.filter(parent=None).first()
    else:
        taxon = get_object_or_404(Taxon, pk=pk)
    json_data = []
    children_data = []
    children_list = taxon.children.all()
    for child in children_list:
        children_data.append( { "id": child.id, "name": child.name, "author": child.authorship, "year": child.year, "parent": child.parent_id } )
    json_data.append( { "id": taxon.id, "name": taxon.name, "author":taxon.authorship, "year": taxon.year, "parent": taxon.parent_id, "children": children_data } )

    json_str = json.dumps(json_data, separators=(',', ':'))

    return render(request, 'taxology/taxon_view.html', {'taxon': taxon, 'user_obj': user_obj, 'json_str':json_str, 'children_list':children_list} )


#@login_required(login_url=LOGIN_URL)
def referencetaxon_edit(request,pk):
    user_obj = get_user_obj( request )
    # if this is a POST request we need to process the form data
    #print("referencetaxon_add")
    reference = get_object_or_404(Reference, pk=pk)
    operation = "New"
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        ReferenceTaxonFormSet = inlineformset_factory(Reference, ReferenceTaxon, form=ReferenceTaxonForm)
        taxon_formset = ReferenceTaxonFormSet(request.POST, instance=reference)
        # check whether it's valid:
        if taxon_formset.is_valid():
            taxon_formset.save()
        else:
            print("taxon form invalid")
            print(taxon_formset.errors)
        return HttpResponseRedirect(reverse('reference_detail',args=(pk,)))
    # if a GET (or any other method) we'll create a blank form
    else:
        ReferenceTaxonFormSet = inlineformset_factory(Reference, ReferenceTaxon, form=ReferenceTaxonForm, extra=5)
        taxon_formset = ReferenceTaxonFormSet(instance=reference)
        #print(author_formset.management_form)
    #print(operation)

    return render(request, 'taxology/referencetaxon_form.html', {'reference': reference,'op':operation,'taxon_formset':taxon_formset, 'user_obj': user_obj})