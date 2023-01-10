import validators

from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import render

from .utils import WebClawler


class UrlForm(forms.Form):
    url = forms.CharField(label="URL", required=True)


class Main:
    def __get_validation_error(self, msg: str):
        return ValidationError(
            msg,
            code='invalid'
        )

    def __get_context(self, form: UrlForm):
        if not form.is_valid():
            form.add_error('url', self.__get_validation_error('Invalid form!'))
            return {"form": form}

        URL: str = form.cleaned_data["url"]
        is_valid_url = validators.url(URL)
        if not is_valid_url or not URL.startswith('http'):
            form.add_error(
                'url', self.__get_validation_error('Incorrect value! Expect valid URL with protocol (http / https)'))
            return {"form": form}

        crawler = WebClawler()
        result = crawler.get_links(URL)

        if result is None:
            form.add_error('url', self.__get_validation_error(
                'Could not get data from the remote server!'))
            return {"form": form}

        return {
            "data": result,
            "form": form
        }

    def index(self, request):
        context = {"form": UrlForm()}

        if request.method == "POST":
            context = self.__get_context(UrlForm(request.POST))

        return render(request, "index.html", context)
