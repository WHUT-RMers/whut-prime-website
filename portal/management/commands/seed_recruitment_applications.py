from __future__ import annotations

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from reportlab.pdfgen import canvas

from portal.models import RecruitmentApplication, RecruitmentAttachment


GROUPS = ('mechanical', 'electrical', 'algorithm', 'operations')
STATUSES = ('pending', 'screened', 'interview', 'accepted', 'rejected', 'talent_pool')
SURNAMES = ('张', '李', '王', '刘', '陈', '杨', '黄', '赵', '周', '吴')


def blank_pdf() -> bytes:
    stream = BytesIO()
    document = canvas.Canvas(stream)
    document.setTitle('PRIME 招新测试简历')
    document.showPage()
    document.save()
    return stream.getvalue()


class Command(BaseCommand):
    help = '生成指定数量的 PRIME 招新测试报名；每份含同一份空白 PDF 附件。'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100)

    def handle(self, *args, **options):
        count = max(1, options['count'])
        pdf = blank_pdf()
        for index in range(count):
            primary = GROUPS[index % len(GROUPS)]
            adjusted = index % 3 != 0
            second = GROUPS[(GROUPS.index(primary) + 1 + index % 3) % len(GROUPS)] if adjusted else ''
            application = RecruitmentApplication.objects.create(
                name=f'{SURNAMES[index % len(SURNAMES)]}测试同学{index + 1:03d}',
                qq=f'20{index + 100000:06d}', wechat=f'prime-test-{index + 1:03d}',
                email=f'prime.test.{index + 1:03d}@example.com', phone=f'138{index + 10000000:08d}',
                college=('自动化学院', '计算机与人工智能学院', '机械工程学院', '管理学院')[index % 4],
                major_class=f'测试专业 {index % 4 + 1} 班', primary_choice=primary,
                accepts_adjustment=adjusted, second_choice=second,
                intended_groups=[primary] + ([second] if second else []),
                introduction='用于后台筛选、分组导出与材料归档的测试报名数据。',
                experience='测试用竞赛经历。', availability=f'每周 {8 + index % 10} 小时',
                consent=True, status=STATUSES[index % len(STATUSES)],
            )
            filename = '统一测试简历.pdf'
            application.resume.save(filename, ContentFile(pdf), save=True)
            RecruitmentAttachment.objects.create(
                application=application,
                file=ContentFile(pdf, name=filename),
                original_name=filename,
            )
        self.stdout.write(self.style.SUCCESS(f'已生成 {count} 份测试报名，每份含统一空白 PDF 附件。'))
