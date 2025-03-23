import logging

from dashboard.models import Dashboard, DashboardSlot
from pptx import Presentation
from pptx.util import Inches, Pt
from reporter_agent.utils.chart_data import create_pptx_chart

logger = logging.getLogger("reportassistant.default")

def create_presentation(dashboard: Dashboard):
    dashboard_slots = DashboardSlot.objects.filter(
        dashboard=dashboard
    ).order_by('row_num', 'col_num')
    prs = Presentation()

    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    title_slide_layout = prs.slide_layouts[0]
    title_slide = prs.slides.add_slide(title_slide_layout)

    title = title_slide.shapes.title
    subtitle = title_slide.placeholders[1]

    title.text = dashboard.title
    subtitle.text = dashboard.description

    for slot in dashboard_slots:
        slide_layout = prs.slide_layouts[5]
        slide = prs.slides.add_slide(slide_layout)

        title_shape = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.5), Inches(12), Inches(1)
        )
        title_frame = title_shape.text_frame
        title_frame.text = f"{slot.chart.title}"
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.size = Pt(24)

        if slot.chart.description:
            notes_slide = slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            text_frame.text = slot.chart.description

        x, y = Inches(1), Inches(1.5)
        cx, cy = Inches(11), Inches(5)

        try:
            create_pptx_chart(
                chart=slot.chart,
                slide=slide,
                x=x,
                y=y,
                cx=cx,
                cy=cy
            )
        except Exception as e:
            logger.error(f"Error creating chart {slot.chart.id}: {str(e)}")

    return prs