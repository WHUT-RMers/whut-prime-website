from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html

from .models import RecruitmentApplication, RecruitmentAttachment, validate_image, validate_recruitment_attachment


class CarouselImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleAttachmentField(forms.FileField):
    widget = CarouselImageInput(attrs={'multiple': True})

    def clean(self, data, initial=None):
        # Individual file validation happens when RecruitmentAttachment is saved.
        return data


class CarouselImageField(forms.Field):
    widget = CarouselImageInput(attrs={
        'accept': 'image/jpeg,image/png,image/webp', 'multiple': True,
        'class': 'portal-carousel-input',
    })

    def to_python(self, value):
        return list(value or [])

    def validate(self, value):
        super().validate(value)
        for image in value:
            try:
                validate_image(image)
            except ValidationError as error:
                raise forms.ValidationError(error.messages[0]) from error


class RichTextWidget(forms.Textarea):
    class Media:
        css = {'all': ('portal/editor/prime-editor.css',)}
        js = ('portal/editor/prime-editor.js',)

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(self.attrs, attrs or {})
        textarea = super().render(name, value, final_attrs, renderer)
        upload_url = final_attrs.get('data-upload-url', '')
        article_id = final_attrs.get('data-article-id', '')
        cover_images = final_attrs.get('data-cover-images', '[]')
        return format_html(
            '<div class="prime-editor-workbench" data-upload-url="{0}" data-article-id="{1}" data-cover-images="{2}">'
            '<section class="prime-editor-pane"><header><div><strong>正文编辑</strong><span>所见即所得，可拖入或粘贴图片</span></div>'
            '<div class="prime-editor-stats"><span data-word-count>0 字</span><span data-read-time>约 1 分钟</span></div></header>{3}</section>'
            '<aside class="prime-preview-pane"><header><div><strong>官网实时预览</strong><span>电脑端正文效果</span></div>'
            '<button type="button" data-preview-toggle>收起预览</button></header><div class="prime-preview-canvas">'
            '<article><div class="prime-preview-meta"><span data-preview-category>战队资讯</span><time data-preview-date>预览状态</time></div>'
            '<h1 data-preview-title>文章标题</h1><p class="prime-preview-summary" data-preview-summary>文章摘要会显示在这里。</p>'
            '<section class="prime-preview-cover is-empty" data-preview-cover aria-label="封面轮播预览">'
            '<div class="prime-preview-cover-stage" data-preview-cover-stage></div>'
            '<div class="prime-preview-cover-empty" data-preview-cover-empty><b>封面轮播</b><span>添加图片后将在这里实时预览</span></div>'
            '<div class="prime-preview-cover-controls" data-preview-cover-controls hidden>'
            '<div class="prime-preview-cover-dots" data-preview-cover-dots></div><span data-preview-cover-counter></span></div></section>'
            '<p class="prime-preview-cover-caption" data-preview-cover-caption hidden></p>'
            '<div class="prime-preview-reading-mark"><span>PRIME · NEWS</span><i></i></div>'
            '<div class="prime-preview-body" data-preview-body></div></article></div></aside></div>',
            upload_url, article_id, cover_images, textarea,
        )


class RecruitmentApplicationForm(forms.ModelForm):
    primary_choice = forms.ChoiceField(choices=RecruitmentApplication.GROUPS, required=False)
    accepts_adjustment = forms.BooleanField(required=False)
    second_choice = forms.ChoiceField(choices=[('', '接受战队统筹安排')] + RecruitmentApplication.GROUPS, required=False)
    attachments = MultipleAttachmentField(required=False, widget=CarouselImageInput(attrs={'multiple': True, 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.webp,.bmp,.txt,.md,.csv,.json,.mp4,.mov,.webm,.mp3,.wav,.m4a,.zip,.rar,.7z'}))

    class Meta:
        model = RecruitmentApplication
        fields = ('name', 'qq', 'wechat', 'email', 'phone', 'college', 'major_class', 'primary_choice', 'accepts_adjustment', 'second_choice', 'introduction', 'experience', 'availability', 'consent')

    def clean(self):
        cleaned = super().clean()
        primary = cleaned.get('primary_choice')
        if not primary:
            legacy_groups = self.data.getlist('intended_groups')
            primary = legacy_groups[0] if legacy_groups else ''
            cleaned['primary_choice'] = primary
        if primary not in dict(RecruitmentApplication.GROUPS):
            self.add_error('primary_choice', '请选择第一志愿。')
        accepts = cleaned.get('accepts_adjustment')
        second = cleaned.get('second_choice')
        files = self.files.getlist('attachments')
        if legacy_resume := self.files.get('resume'):
            files.append(legacy_resume)
        if accepts and second and second == primary:
            self.add_error('second_choice', '第二志愿不能与第一志愿相同。')
        if not accepts:
            cleaned['second_choice'] = ''
        has_existing_material = bool(self.instance and self.instance.pk and (self.instance.attachments.exists() or self.instance.resume))
        if not has_existing_material and not files:
            self.add_error('attachments', '请至少上传一份报名材料。')
        for file in files:
            try:
                validate_recruitment_attachment(file)
            except ValidationError as error:
                self.add_error('attachments', error)
        return cleaned

    def save(self, commit=True):
        application = super().save(commit=False)
        # 兼容早期后台导出的字段，新的报名信息以拆分后的联系方式为准。
        application.contact = f'QQ：{application.qq}；微信：{application.wechat}；邮箱：{application.email}；电话：{application.phone}'
        application.major = application.major_class
        application.grade = '已合并填写'
        application.intended_groups = [application.primary_choice] + ([application.second_choice] if application.accepts_adjustment and application.second_choice else [])
        files = self.files.getlist('attachments')
        if legacy_resume := self.files.get('resume'):
            files.append(legacy_resume)
        resume = next((file for file in files if file.name.lower().endswith('.pdf')), None)
        if resume:
            application.resume = resume
        if commit:
            application.save()
            for file in files:
                RecruitmentAttachment.objects.create(application=application, file=file, original_name=file.name[:255])
            self.save_m2m()
        return application

    def clean_consent(self):
        if not self.cleaned_data['consent']:
            raise forms.ValidationError('请先同意个人信息仅用于本次招新。')
        return True
