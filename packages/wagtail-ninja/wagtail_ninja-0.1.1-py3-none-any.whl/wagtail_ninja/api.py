import inspect
import sys
from typing import Any, ClassVar

import orjson
from ninja import ModelSchema, NinjaAPI, Router
from ninja.renderers import BaseRenderer

from django.core.exceptions import FieldDoesNotExist
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, get_page_models
from wagtail.rich_text import expand_db_html

from wagtail_ninja.schema import BasePageSchema, StreamFieldSchema


def serialize_streamfield(sfield: StreamField, context):
    cntnt = sfield.stream_block.get_api_representation(sfield, context)
    return cntnt


class WagtailRouter(Router):
    @staticmethod
    def _create_page_schema(page_model: Page):
        def __create_richtext_resolver(_field: str):
            return staticmethod(
                lambda page, context: expand_db_html(getattr(page, _field))
            )

        def __create_streamfield_resolver(_field: str):
            return staticmethod(
                lambda page, context: serialize_streamfield(
                    getattr(page, _field), context
                )
            )

        def __create_method_resolver(_field: str):
            return staticmethod(lambda page, context: getattr(page, _field)())

        api_fields = getattr(page_model, "api_fields", [])

        props = {
            "__module__": sys.modules[__name__].__name__,
            "__annotations__": {},
        }

        relevant_fields = []
        for field in api_fields:
            # print(field)
            try:
                model_field = page_model._meta.get_field(field)

                # print(model_field)
                if isinstance(model_field, StreamField):
                    props["__annotations__"][field] = StreamFieldSchema
                    props[f"resolve_{field}"] = __create_streamfield_resolver(field)

                if isinstance(model_field, RichTextField):
                    props["__annotations__"][field] = str
                    props[f"resolve_{field}"] = __create_richtext_resolver(field)

                relevant_fields.append(field)
            except FieldDoesNotExist:
                ex_fnc = getattr(page_model, field, None)

                signature = inspect.signature(ex_fnc)
                return_annotation = signature.return_annotation

                if callable(ex_fnc):
                    # print(field, ex_fnc)
                    props["__annotations__"][field] = (
                        Any
                        if return_annotation is inspect._empty
                        else return_annotation
                    )
                    props[f"resolve_{field}"] = __create_method_resolver(field)

        # print(relevant_fields)
        meta = type(
            "Meta", (), {"model": page_model, "fields": relevant_fields or ["title"]}
        )
        props["Meta"] = meta
        props["__annotations__"]["Meta"] = ClassVar[type[meta]]

        new_class = type(str(page_model.__name__), (BasePageSchema, ModelSchema), props)
        return new_class

    def _create_pages_schemas(self):
        schemas = None
        for model in get_page_models():
            if model == Page:
                continue

            page_schema = self._create_page_schema(model)
            if not schemas:
                schemas = page_schema
            else:
                schemas |= page_schema

        return schemas

    def autodetect(self, **kwargs):
        def list_pages(request: "HttpRequest"):
            return Page.objects.live().public()

        def get_page(request: "HttpRequest", page_id: int):
            return get_object_or_404(Page, id=page_id).specific

        all_page_schemas = self._create_pages_schemas()
        self.add_api_operation(
            "/pages/", ["GET"], list_pages, response=list[BasePageSchema]
        )
        self.add_api_operation(
            "/pages/{page_id}/", ["GET"], get_page, response=all_page_schemas
        )


router = WagtailRouter()
router.autodetect()


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data)


api = NinjaAPI(renderer=ORJSONRenderer(), default_router=router)
