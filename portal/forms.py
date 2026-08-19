from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import RecruitmentApplication


class RichTextWidget(forms.Textarea):
    class Media:
        js = ('portal/richtext.js',)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        textarea = super().render(name, value, attrs, renderer)
        editor_id = f"rich-{attrs.get('id', name)}"
        return format_html(
            '<div class="prime-richtext" data-target="#{0}"><div class="prime-richtext-toolbar">'
            '<button type="button" data-command="bold">加粗</button><button type="button" data-command="italic">斜体</button>'
            '<button type="button" data-command="formatBlock" data-value="h2">小标题</button>'
            '<button type="button" data-command="insertUnorderedList">列表</button></div>'
            '<div id="{1}" class="prime-richtext-editor" contenteditable="true">{2}</div></div>{3}',
            attrs.get('id', name), editor_id, mark_safe(value or ''), textarea,
        )


class RecruitmentApplicationForm(forms.ModelForm):
    intended_groups = forms.MultipleChoiceField(choices=RecruitmentApplication.GROUPS)

    class Meta:
        model = RecruitmentApplication
        fields = ('name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class', 'intended_groups', 'introduction', 'experience', 'availability', 'resume', 'consent')

    def save(self, commit=True):
        application = super().save(commit=False)
        # 兼容早期后台导出的字段，新的报名信息以拆分后的联系方式为准。
        application.contact = f'QQ：{application.qq}；微信：{application.wechat}；邮箱：{application.email}；电话：{application.phone}'
        application.major = application.major_class
        application.grade = '已合并填写'
        if commit:
            application.save()
            self.save_m2m()
        return application

    def clean_consent(self):
        if not self.cleaned_data['consent']:
            raise forms.ValidationError('请先同意个人信息仅用于本次招新。')
        return True
