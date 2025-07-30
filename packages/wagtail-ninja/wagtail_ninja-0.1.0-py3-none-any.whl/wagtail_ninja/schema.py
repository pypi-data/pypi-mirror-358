from datetime import datetime
from typing import Any

from ninja import ModelSchema, Schema
from pydantic import RootModel

from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.rich_text import expand_db_html


def serialize_streamfield(field: StreamField, context):
    cntnt = field.stream_block.get_api_representation(field, context)
    return cntnt


class Breadcrumb(Schema):
    title: str
    url: str | None = None


class PageMeta(Schema):
    type: str
    detail_url: str
    html_url: str
    slug: str
    show_in_menus: bool
    seo_title: str
    search_description: str
    first_published_at: datetime
    # alias_of: None  TODO
    # parent:   TODO
    locale: str


class StreamBlock(Schema):
    type: str
    value: Any
    id: str


class StreamFieldSchema(RootModel):
    root: list[StreamBlock] = []


class BasePageSchema(ModelSchema):
    # url: str | None = Field(None, alias="get_url")
    meta: PageMeta
    # breadcrumbs: list[Breadcrumb] = Field(list, alias="get_breadcrumbs")
    breadcrumbs: list[Breadcrumb]

    @staticmethod
    def resolve_meta(page: Page, context) -> PageMeta:
        m_type = f"{page.specific_class._meta.app_label}.{type(page).__name__}"

        return PageMeta(
            type=m_type,
            detail_url="asdf",  # TODO
            # html_url=get_full_url(context["request"], page.get_url(context["request"])),
            html_url="asdfasdfasdf",
            slug=page.slug,
            show_in_menus=page.show_in_menus,
            seo_title=page.seo_title,
            search_description=page.search_description,
            first_published_at=page.first_published_at,
            # alias_of=None,
            locale=page.locale.language_code,
        )

    @staticmethod
    def resolve_breadcrumbs(page: HeaderPageMixin, context) -> str:
        return page.breadcrumbs()

    class Config:
        model = Page
        model_fields = ["id", "title"]


class HeaderPageMixinSchema(ModelSchema):
    header_images: StreamFieldSchema

    class Config:
        model = HeaderPageMixin
        model_fields = ["lead"]

    @staticmethod
    def resolve_header_images(page: HeaderPageMixin, context) -> StreamFieldSchema:
        return serialize_streamfield(page.header_images, context)

    @staticmethod
    def resolve_lead(page: HeaderPageMixin, context) -> str:
        return expand_db_html(page.lead)


class ContentPageSchema(BasePageSchema, HeaderPageMixinSchema, ModelSchema):
    class Meta:
        model = ContentPage
        fields = ["content"]

    @staticmethod
    def resolve_content(page: ContentPage, context):
        return serialize_streamfield(page.content, context)


class HomePageSchema(BasePageSchema, HeaderPageMixinSchema, ModelSchema):
    class Meta:
        model = HomePage
        fields = ["content"]

    @staticmethod
    def resolve_content(page: HomePage, context):
        return serialize_streamfield(page.content, context)


class ProjectsAndCountiesPageSchema(BasePageSchema, HeaderPageMixinSchema, ModelSchema):
    class Meta:
        model = ProjectsAndCountiesPage
        fields = ["content"]

    @staticmethod
    def resolve_content(page: ProjectsAndCountiesPage, context):
        return serialize_streamfield(page.content, context)


class ProjectsPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = ProjectsPage


class ProjectPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = ProjectPage
        fields = ["contact_person", "content"]

    @staticmethod
    def resolve_content(page: ProjectPage, context):
        return serialize_streamfield(page.content, context)


class ProjectCountriesPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = ProjectCountriesPage
        fields = ["content"]

    @staticmethod
    def resolve_content(page: ProjectCountriesPage, context):
        return serialize_streamfield(page.content, context)


class ProjectCountryPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = ProjectCountryPage
        fields = ["country", "content"]

    @staticmethod
    def resolve_content(page: ProjectCountryPage, context):
        return serialize_streamfield(page.content, context)


class MembersPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = MembersPage
        fields = ["content", "members", "member_dimensions"]

    @staticmethod
    def resolve_content(page: MembersPage, context):
        return serialize_streamfield(page.content, context)

    @staticmethod
    def resolve_members(page: MembersPage, context):
        return page.members()

    @staticmethod
    def resolve_member_dimensions(page: MembersPage, context):
        return page.member_dimensions()


class MediaLibraryPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = MediaLibraryPage
        fields = ["content"]

    @staticmethod
    def resolve_content(page: MediaLibraryPage, context):
        return serialize_streamfield(page.content, context)


class MediaPageSchema(BasePageSchema, HeaderPageMixinSchema):
    class Meta:
        model = MediaPage
        fields = ["content"]

    @staticmethod
    def resolve_content(page: MediaPage, context):
        return serialize_streamfield(page.content, context)
