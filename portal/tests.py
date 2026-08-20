from io import BytesIO
import zipfile

from openpyxl import load_workbook

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import NewsArticle, NewsCoverSlide, NewsImage, RecruitmentApplication, RecruitmentSettings


class PortalApiTests(TestCase):
    def setUp(self):
        self.article = NewsArticle.objects.create(
            title='测试资讯', summary='测试摘要', category='赛报', body='<p>正文</p>',
            status=NewsArticle.Status.PUBLISHED, published_at=timezone.now(), cover='news/test.jpg',
            cover_caption='机器人在赛场进行调试',
        )

    def test_public_news_and_deduplicated_view(self):
        item = self.client.get(reverse('portal:news-list')).json()['items'][0]
        self.assertEqual(item['slug'], self.article.slug)
        self.assertEqual(item['cover_images'][0]['caption'], '机器人在赛场进行调试')
        url = reverse('portal:news-view', args=[self.article.slug])
        self.client.post(url)
        self.client.post(url)
        self.article.refresh_from_db()
        self.assertEqual(self.article.view_count, 1)

    def test_closed_recruitment_rejects_submission(self):
        RecruitmentSettings.current()
        response = self.client.post(reverse('portal:recruitment-submit'), {})
        self.assertEqual(response.status_code, 403)

    def test_open_recruitment_accepts_pdf(self):
        settings = RecruitmentSettings.current(); settings.is_open = True; settings.save()
        response = self.client.post(reverse('portal:recruitment-submit'), {
            'name': '张同学', 'qq': '12345678', 'wechat': 'prime-zhang', 'email': 'zhang@example.com', 'phone': '13800000000',
            'college': '计算机学院', 'major_class': '软件工程 2301 班',
            'intended_groups': ['algorithm'], 'introduction': '热爱机器人', 'experience': '', 'availability': '每周 12 小时', 'consent': 'true',
            'resume': SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test', content_type='application/pdf'),
        })
        self.assertEqual(response.status_code, 201, response.content.decode())

    def test_recruitment_choices_attachments_and_grouped_export(self):
        settings = RecruitmentSettings.current(); settings.is_open = True; settings.save()
        response = self.client.post(reverse('portal:recruitment-submit'), {
            'name': '李同学', 'qq': '12345678', 'wechat': 'prime-li', 'email': 'li@example.com', 'phone': '13900000000',
            'college': '自动化学院', 'major_class': '自动化 2301 班', 'primary_choice': 'algorithm',
            'accepts_adjustment': 'true', 'second_choice': 'electrical', 'introduction': '热爱机器人',
            'availability': '每周 12 小时', 'consent': 'true',
            'attachments': [SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test', content_type='application/pdf'), SimpleUploadedFile('award.pdf', b'%PDF-1.4 award', content_type='application/pdf')],
        })
        self.assertEqual(response.status_code, 201, response.content.decode())
        application = RecruitmentApplication.objects.get(name='李同学')
        self.assertEqual(application.primary_choice, 'algorithm')
        self.assertEqual(application.second_choice, 'electrical')
        self.assertEqual(application.attachments.count(), 2)
        user = get_user_model().objects.create_superuser('recruit-exporter', 'recruit@example.com', 'safe-password-123')
        self.client.force_login(user)
        export = self.client.get(reverse('admin:portal_recruitment_export_all'))
        self.assertEqual(export.status_code, 200)
        with zipfile.ZipFile(BytesIO(b''.join(export.streaming_content))) as archive:
            names = archive.namelist()
            workbook = load_workbook(BytesIO(archive.read('报名信息.xlsx')))
        self.assertIn('报名信息.xlsx', names)
        self.assertTrue(any(name.startswith('算法组/') and name.endswith('resume.pdf') for name in names))
        self.assertEqual(workbook.sheetnames, ['报名汇总'])
        self.assertTrue(any('算法组' in str(row[0].value) for row in workbook['报名汇总'].iter_rows()))

    def test_staff_can_preview_recruitment_materials(self):
        application = RecruitmentApplication.objects.create(
            name='预览同学', qq='7654321', wechat='preview-prime', email='preview@example.com', phone='13700000000',
            college='计算机学院', major_class='软件工程 2301 班', primary_choice='algorithm', intended_groups=['algorithm'],
            introduction='用于验证后台附件预览。', availability='每周 10 小时', consent=True,
            resume=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 preview', content_type='application/pdf'),
        )
        attachment = application.attachments.create(
            original_name='award.pdf',
            file=SimpleUploadedFile('award.pdf', b'%PDF-1.4 award', content_type='application/pdf'),
        )
        user = get_user_model().objects.create_superuser('preview-admin', 'preview-admin@example.com', 'safe-password-123')
        self.client.force_login(user)
        preview = self.client.get(reverse('admin:portal_recruitment_attachment_file', args=[application.pk, attachment.pk]))
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.headers['Content-Type'], 'application/pdf')
        self.assertNotIn('attachment', preview.headers.get('Content-Disposition', ''))
        self.assertEqual(
            self.client.get(reverse('admin:portal_recruitment_resume_preview', args=[application.pk])).status_code,
            200,
        )

    def test_staff_can_preview_common_office_and_archive_materials(self):
        from docx import Document
        from openpyxl import Workbook

        application = RecruitmentApplication.objects.create(
            name='材料同学', qq='6654321', wechat='materials-prime', email='materials@example.com', phone='13600000000',
            college='自动化学院', major_class='自动化 2301 班', primary_choice='electrical', intended_groups=['electrical'],
            introduction='用于验证常见文件预览。', availability='每周 10 小时', consent=True,
            resume=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 preview', content_type='application/pdf'),
        )
        document_buffer = BytesIO(); document = Document(); document.add_paragraph('Word 文档预览内容'); document.save(document_buffer)
        spreadsheet_buffer = BytesIO(); workbook = Workbook(); workbook.active.title = '报名信息'; workbook.active.append(['姓名', '组别']); workbook.active.append(['小王', '电控组']); workbook.save(spreadsheet_buffer)
        archive_buffer = BytesIO()
        with zipfile.ZipFile(archive_buffer, 'w') as archive:
            archive.writestr('作品/说明.txt', '作品说明')
        attachments = [
            application.attachments.create(original_name='portfolio.docx', file=SimpleUploadedFile('portfolio.docx', document_buffer.getvalue())),
            application.attachments.create(original_name='works.xlsx', file=SimpleUploadedFile('works.xlsx', spreadsheet_buffer.getvalue())),
            application.attachments.create(original_name='materials.zip', file=SimpleUploadedFile('materials.zip', archive_buffer.getvalue())),
        ]
        user = get_user_model().objects.create_superuser('materials-admin', 'materials-admin@example.com', 'safe-password-123')
        self.client.force_login(user)
        expected_kinds = ['document', 'spreadsheet', 'archive']
        for attachment, expected_kind in zip(attachments, expected_kinds):
            response = self.client.get(reverse('admin:portal_recruitment_attachment_preview_data', args=[application.pk, attachment.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['kind'], expected_kind)

    def test_staff_can_upload_an_inline_body_image(self):
        user = get_user_model().objects.create_superuser('editor', 'editor@example.com', 'safe-password-123')
        self.client.force_login(user)
        buffer = BytesIO()
        Image.new('RGB', (1200, 675), '#2de2a6').save(buffer, 'JPEG')
        upload = SimpleUploadedFile('inline.jpg', buffer.getvalue(), content_type='image/jpeg')
        response = self.client.post(reverse('admin:portal_news_upload_inline_image'), {
            'image': upload, 'article_id': self.article.pk,
        })
        self.assertEqual(response.status_code, 200, response.content.decode())
        self.assertEqual(NewsImage.objects.filter(article=self.article).count(), 1)
        self.assertTrue(response.json()['url'].startswith('/api/news/'))
        self.assertIn('/content-images/', response.json()['url'])
        image_response = self.client.get(response.json()['url'])
        self.assertEqual(image_response.status_code, 200)
        self.assertEqual(image_response.headers['Content-Type'], 'image/jpeg')
        self.client.logout()
        self.assertEqual(self.client.get(response.json()['url']).status_code, 200)

    def test_new_article_editor_can_upload_image_before_first_save(self):
        user = get_user_model().objects.create_superuser('new-body-editor', 'new-body@example.com', 'safe-password-123')
        self.client.force_login(user)
        buffer = BytesIO()
        Image.new('RGB', (1000, 700), '#4da3ff').save(buffer, 'JPEG')
        upload = SimpleUploadedFile('draft-inline.jpg', buffer.getvalue(), content_type='image/jpeg')
        response = self.client.post(reverse('admin:portal_news_upload_inline_image'), {'image': upload})
        self.assertEqual(response.status_code, 200, response.content.decode())
        image = NewsImage.objects.get(pk=response.json()['id'])
        self.assertIsNone(image.article_id)
        self.assertEqual(self.client.get(response.json()['url']).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(response.json()['url']).status_code, 404)

    def test_news_editor_has_the_unified_carousel_manager(self):
        user = get_user_model().objects.create_superuser('carousel-editor', 'carousel@example.com', 'safe-password-123')
        self.client.force_login(user)
        response = self.client.get(reverse('admin:portal_newsarticle_change', args=[self.article.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'portal-carousel-input')
        self.assertContains(response, 'portal/carousel_manager.css')
        self.assertContains(response, 'portal/editor/prime-editor.js')
        self.assertContains(response, '官网实时预览')

    def test_news_add_page_opens_without_existing_images(self):
        user = get_user_model().objects.create_superuser('add-editor', 'add@example.com', 'safe-password-123')
        self.client.force_login(user)
        response = self.client.get(reverse('admin:portal_newsarticle_add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id_carousel_uploads')
        self.assertContains(response, 'multiple')
        self.assertContains(response, 'portal/carousel_manager.js')
        self.assertContains(response, reverse('admin:portal_news_upload_inline_image'))
        expected = f'<div class="prime-editor-workbench" data-upload-url="{reverse("admin:portal_news_upload_inline_image")}"'
        self.assertIn(expected.encode(), response.content)

    def test_editor_appends_multiple_carousel_images_in_upload_order(self):
        user = get_user_model().objects.create_superuser('batch-editor', 'batch@example.com', 'safe-password-123')
        self.client.force_login(user)

        def image_upload(name, color):
            buffer = BytesIO()
            Image.new('RGB', (1200, 675), color).save(buffer, 'JPEG')
            return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')

        response = self.client.post(reverse('admin:portal_newsarticle_change', args=[self.article.pk]), {
            'title': self.article.title, 'slug': self.article.slug, 'summary': self.article.summary,
            'category': self.article.category, 'body': self.article.body, 'status': 'published',
            'published_at': timezone.localtime(self.article.published_at).strftime('%Y-%m-%dT%H:%M'),
            'image_focus': 'center', 'external_url': '',
            'carousel_uploads': [image_upload('first.jpg', '#e2a62d'), image_upload('second.jpg', '#2da6e2')],
            'carousel_upload_captions': ['第一张追加图片说明', '第二张追加图片说明'],
            'carousel_saved_caption_cover': '更新后的首图说明',
            '_save': '保存',
        })
        self.assertEqual(response.status_code, 302, response.content.decode())
        slides = NewsCoverSlide.objects.filter(article=self.article).order_by('sort_order')
        self.assertEqual(slides.count(), 2)
        self.article.refresh_from_db()
        self.assertEqual(self.article.cover_caption, '更新后的首图说明')
        self.assertEqual(list(slides.values_list('caption', flat=True)), ['第一张追加图片说明', '第二张追加图片说明'])
        with Image.open(slides[0].image) as first, Image.open(slides[1].image) as second:
            self.assertGreater(first.getpixel((0, 0))[0], first.getpixel((0, 0))[2])
            self.assertGreater(second.getpixel((0, 0))[2], second.getpixel((0, 0))[0])

    def test_editor_can_create_article_with_multiple_carousel_images(self):
        user = get_user_model().objects.create_superuser('new-editor', 'new@example.com', 'safe-password-123')
        self.client.force_login(user)

        def image_upload(name, color):
            buffer = BytesIO()
            Image.new('RGB', (1200, 675), color).save(buffer, 'JPEG')
            return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')

        response = self.client.post(reverse('admin:portal_newsarticle_add'), {
            'title': '后台新增的多图资讯', 'slug': '', 'summary': '用于验证新增流程。',
            'category': '日常', 'body': '<p>正文</p>', 'status': 'draft',
            'published_at': '', 'image_focus': 'center', 'external_url': '',
            'carousel_uploads': [image_upload('one.jpg', '#e2a62d'), image_upload('two.jpg', '#2da6e2')],
            'carousel_upload_captions': ['首图说明', '第二张说明'],
            '_save': '保存',
        })
        self.assertEqual(response.status_code, 302, response.content.decode())
        article = NewsArticle.objects.get(title='后台新增的多图资讯')
        self.assertTrue(article.cover.name)
        self.assertEqual(article.cover_caption, '首图说明')
        slide = NewsCoverSlide.objects.get(article=article)
        self.assertEqual(slide.caption, '第二张说明')

    def test_first_save_attaches_temporary_body_images(self):
        user = get_user_model().objects.create_superuser('attach-editor', 'attach@example.com', 'safe-password-123')
        self.client.force_login(user)

        def image_upload(name, color, size=(1200, 675)):
            buffer = BytesIO()
            Image.new('RGB', size, color).save(buffer, 'JPEG')
            return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')

        upload_response = self.client.post(reverse('admin:portal_news_upload_inline_image'), {
            'image': image_upload('body.jpg', '#2de2a6', (1000, 700)),
        })
        self.assertEqual(upload_response.status_code, 200)
        image = NewsImage.objects.get(pk=upload_response.json()['id'])
        body = f'<p>开头</p><figure class="image"><img src="{upload_response.json()["url"]}"></figure>'
        response = self.client.post(reverse('admin:portal_newsarticle_add'), {
            'title': '带正文插图的资讯', 'slug': '', 'summary': '用于验证图片归属。',
            'category': '日常', 'body': body, 'status': 'draft', 'published_at': '',
            'external_url': '', 'carousel_uploads': [image_upload('cover.jpg', '#4da3ff')], '_save': '保存',
        })
        self.assertEqual(response.status_code, 302, response.content.decode())
        image.refresh_from_db()
        self.assertEqual(image.article.title, '带正文插图的资讯')
from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
