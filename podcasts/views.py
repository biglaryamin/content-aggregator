from django.shortcuts import render
from django.views.generic import ListView
from .models import Episode


class ListPodcasts(ListView):
    model        =Episode
    template_name="index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["episodes"] = Episode.objects.filter().order_by("-pub_date")[:10]
        return context