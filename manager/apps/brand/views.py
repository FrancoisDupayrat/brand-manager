from django.shortcuts import render
from django.views.generic import View
from .models import Brand, BrandOwner, BrandProposal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from .forms import BrandProposalForm
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from random import choice
from string import ascii_lowercase, digits


class OwnerListView(View):
    r"""
    """

    template_name = 'brand/ownerlist.jade'

    def get(self, request):
        search = request.GET.get('search', '')
        if search != '':
            owner_list = BrandOwner.objects.filter(owner_nm__icontains=search)
        else:
            owner_list = BrandOwner.objects.all()
        paginator = Paginator(owner_list, 25)  # Show 25 owners per page

        page = request.GET.get('page')
        try:
            owners = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            owners = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            owners = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {
                      'owners': owners,
                      'search': search})


class OwnerView(View):
    r"""
    """

    template_name = 'brand/owner.jade'

    def get(self, request, cd):
        try:
            owner = BrandOwner.objects.get(owner_cd__iexact=cd)
        except ObjectDoesNotExist:
            return HttpResponseNotFound('<h1>Owner not found</h1>')
        return render(request, self.template_name, {
                      'owner': owner})


class BrandListView(View):
    r"""
    """

    template_name = 'brand/brandlist.jade'

    def get(self, request):
        search = request.GET.get('search', '')
        if search != '':
            brand_list = Brand.objects.filter(brand_nm__icontains=search)
            brand_list = filter(lambda brand: not brand.flag_delete,
                                brand_list)
        else:
            brand_list = Brand.objects.filter(flag_delete=False)
        paginator = Paginator(brand_list, 25)  # Show 25 brands per page

        page = request.GET.get('page')
        try:
            brands = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            brands = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            brands = paginator.page(paginator.num_pages)
        return render(request, self.template_name, {
                      'brands': brands,
                      'search': search})


class BrandView(View):
    r"""
    """

    template_name = 'brand/brand.jade'

    def get(self, request, bsin):
        try:
            brand = Brand.objects.get(bsin=bsin)
        except ObjectDoesNotExist:
            return HttpResponseNotFound('<h1>Brand not found</h1>')
        return render(request, self.template_name, {
                      'brand': brand,
                      'owner': brand.owner_cd})


def generate_random_username(length=16,
                             chars=ascii_lowercase + digits,
                             split=4, delimiter='-'):
    username = ''.join([choice(chars) for i in xrange(length)])
    if split:
        username = delimiter.join(
            [username[start:start + split]
                for start in range(0, len(username), split)])
        try:
            User.objects.get(username=username)
            return generate_random_username(
                length=length, chars=chars,
                split=split, delimiter=delimiter)
        except User.DoesNotExist:
            return username


class BrandProposalView(FormView):
    r"""
    """

    template_name = 'brand/brandproposalplaceholder.jade'
    form_class = BrandProposalForm
    success_url = '/brand/proposed/'

    def get(self, request):
        form = BrandProposalForm() # An unbound form

        return render(request, self.template_name, {
                      'form': form})

    def form_valid(self, form):
        user, created = User.objects.get_or_create(
            email=form.cleaned_data['sender'],
            defaults={
                'username': generate_random_username(),
                'is_staff': False,
                'is_active': False,
                'is_superuser': False})
        if created:
            user.save()
        proposal = BrandProposal(
            brand_nm=form.cleaned_data['brand_nm'],
            owner_nm=form.cleaned_data['owner_nm'],
            brand_link=form.cleaned_data['brand_link'],
            brand_type_cd=form.cleaned_data['brand_type'],
            comments=form.cleaned_data['comments'],
            user=user)
        proposal.save()

        #save the logo after the proposal is created in the DB
        #because upload_to requires the primary key to be set
        proposal.brand_logo = form.cleaned_data['brand_logo']
        proposal.save()
        return super(BrandProposalView, self).form_valid(form)


class BrandProposedView(View):
    r"""
    """

    template_name = 'brand/brandproposed.jade'

    def get(self, request):
        return render(request, self.template_name)
