from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Taxon, TaxonRank, TaxonAuthor
from .forms import TaxonForm, TaxonAuthorForm
from django.urls import reverse, reverse_lazy

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
    return HttpResponse("Hello, world. You're at the taxology index.")

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
    #author_list = taxon.author.all().order_by('taxonauthor__author_order')
    return render(request, 'taxology/taxon_detail.html', {'taxon': taxon, 'user_obj': user_obj} )

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

    return render(request, 'kprdb/referencetaxon_form.html', {'reference': reference,'op':operation,'taxon_formset':taxon_formset, 'user_obj': user_obj})