from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import NewsArticle, RecruitmentSettings


class PortalApiTests(TestCase):
    def setUp(self):
        self.article = NewsArticle.objects.create(
            title='测试资讯', summary='测试摘要', category='赛报', body='<p>正文</p>',
            status=NewsArticle.Status.PUBLISHED, published_at=timezone.now(), cover='news/test.jpg',
        )

    def test_public_news_and_deduplicated_view(self):
        self.assertEqual(self.client.get(reverse('portal:news-list')).json()['items'][0]['slug'], self.article.slug)
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
