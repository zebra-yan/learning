# -*- coding: utf-8 -*-
"""Draft defense slides; insert figures from thesis folder manually."""
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.enum.text import PP_ALIGN

def add_title_slide(prs, title, subtitle_lines):
    layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    tf = slide.placeholders[1].text_frame
    tf.clear()
    for i, line in enumerate(subtitle_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(20)
        p.alignment = PP_ALIGN.CENTER


def add_bullet_slide(prs, title, bullets):
    layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    body = slide.placeholders[1].text_frame
    body.clear()
    for i, b in enumerate(bullets):
        p = body.paragraphs[0] if i == 0 else body.add_paragraph()
        p.text = b
        p.level = 0
        p.font.size = Pt(18)


def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    add_title_slide(
        prs,
        "基于深度学习的fMRI视觉信息\n解析重建技术研究",
        [
            "专业：电子信息（全日制）",
            "指导教师：王文举 副教授",
            "学号：213332980",
            "答辩人：严锐鹏",
        ],
    )

    add_bullet_slide(
        prs,
        "汇报提纲",
        [
            "研究背景与意义",
            "国内外现状与技术路线",
            "方法与创新：MUSD 与 CACSD",
            "实验结果与总结展望",
        ],
    )

    add_bullet_slide(
        prs,
        "1 研究背景与意义",
        [
            "【图表】论文图1.1：fMRI视觉信息解析重建示意",
            "神经解码：从体素活动恢复自然图像，服务脑机接口与医学影像等应用",
            "任务价值：理解视觉皮层编码，推动非侵入式脑机接口",
        ],
    )

    add_bullet_slide(
        prs,
        "1.1 核心挑战（示意）",
        [
            "【图表】双栏对比图：fMRI（高维/噪声/低频） vs 自然图像（高频/结构）",
            "表示鸿沟：跨模态分布差异大",
            "评价矛盾：像素保真与高层语义难以同时最优",
        ],
    )

    add_bullet_slide(
        prs,
        "1.2 研究现状概览",
        [
            "【图表】分类思维导图：重建型 vs 生成型（各3–4个代表方法）",
            "重建型：回归/自监督，细节尚可但语义对齐不足",
            "生成型：扩散/CLIP 条件，真实感强但条件粗、易耦合干扰",
        ],
    )

    add_bullet_slide(
        prs,
        "1.3 本文思路与技术路线",
        [
            "【图表】论文图1.2：特征提取→多模态解码→条件控制→高清合成",
            "先 MUSD：共享空间分阶段对齐 + 掩码自监督",
            "再 CACSD：多层级条件自适应注入 Stable Diffusion",
        ],
    )

    add_bullet_slide(
        prs,
        "1.4 论文结构与创新点",
        [
            "第2章：Transformer、扩散、自监督；GODD/NSD 与评价指标",
            "创新1：MUSD + 一致性损失（PVC + MDR）",
            "创新2：CACSD + CPDAU + 两阶段协同训练",
        ],
    )

    add_bullet_slide(
        prs,
        "2 MUSD 方法总览",
        [
            "【图表】论文图3.1：多模态统一分阶段解码器框架",
            "统一掩码与向量化 → 单模态提取 / 跨模态对齐 / 掩码合成",
            "输出完整视觉表征 → 线性头重建图像",
        ],
    )

    add_bullet_slide(
        prs,
        "2.1 MUSD 损失与训练要点",
        [
            "【图表】小示意图：PVC（对比对齐） + MDR（掩码重建）→ 加权",
            "训练：12层 Transformer，分 5+3+4 阶段；掩码率图像75%/fMRI25%（训练）",
            "测试：图像掩码100% 仅 fMRI 输入解码",
        ],
    )

    add_bullet_slide(
        prs,
        "2.2 MUSD 定量结果",
        [
            "【图表】柱状图：表3.1、表3.2 的 PixCorr / SSIM（GODD & NSD）",
            "GODD：PixCorr 0.320，SSIM 0.590",
            "NSD：PixCorr 0.289，SSIM 0.552（像素/结构指标领先对比方法）",
        ],
    )

    add_bullet_slide(
        prs,
        "2.3 MUSD 可视化与消融",
        [
            "【图表】论文图3.8、图3.8：与 ICGAN/LDM/MindVis/NeuroAdapter 对比",
            "【图表】表3.3、3.4 要点：去 PVC 或去掩码合成阶段 → 语义/细节显著下降",
        ],
    )

    add_bullet_slide(
        prs,
        "3 CACSD 动机与框架",
        [
            "【图表】论文图4.1：条件自适应控制 + Stable Diffusion",
            "MUSD 三阶段特征 → 卷积对齐为 64×64 条件特征图",
            "并行注入 U-Net 去噪，继承扩散先验",
        ],
    )

    add_bullet_slide(
        prs,
        "3.1 条件自适应控制与 CPDAU",
        [
            "【图表】论文图4.3、图4.4：零卷积 + CPDAU 流程",
            "通道池化（均值/方差/L2）驱动动态超参，减轻多条件耦合",
        ],
    )

    add_bullet_slide(
        prs,
        "3.2 两阶段训练策略",
        [
            "【图表】时间轴：自监督图像预训练 → fMRI-图像有监督微调",
            "目标：条件分支先学会视觉统计，再对齐神经信号",
        ],
    )

    add_bullet_slide(
        prs,
        "3.3 CACSD 定量结果",
        [
            "【图表】雷达图或表格缩略：表4.1、表4.2（NSD / GOD）",
            "NSD：EffNet 0.659，SwAV 0.410；CLIP/Inception 两两识别约 0.928 / 0.938",
            "GOD：EffNet 0.684，SwAV 0.456",
        ],
    )

    add_bullet_slide(
        prs,
        "3.4 CACSD 可视化与消融",
        [
            "【图表】论文图4.7、4.8：与 LDM、BD、NeuroAdapter、MUSD、GT 对比",
            "【图表】表4.3、4.4、4.5：多条件、激活函数、池化策略消融结论",
        ],
    )

    add_bullet_slide(
        prs,
        "4 总结与展望",
        [
            "总结：MUSD 强化跨模态对齐与细节；CACSD 在扩散框架下协同语义与高频",
            "展望：结构/颜色先验、跨被试泛化、低场强临床数据鲁棒性",
        ],
    )

    add_bullet_slide(prs, "致谢", ["感谢导师王文举副教授的悉心指导", "感谢各位专家，请批评指正"])

    out = r"d:\repos\learning\fMRI_答辩PPT_严锐鹏_草案.pptx"
    prs.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
