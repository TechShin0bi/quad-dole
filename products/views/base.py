from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin

# Common imports for all views
from products.models import Product, Brand, Category, ProductModel
from products.forms import ProductForm, BrandForm, CategoryForm, ProductModelForm

# Common mixins can be defined here if needed
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is staff member"""
    def test_func(self):
        return self.request.user.is_staff
