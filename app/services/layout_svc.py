import os
import re
import logging
import gc
from typing import Dict, List, Tuple
import fitz

#全局配置
logger = logging.getLogger("app.services.layout_svc")
# Anchor_ID生成规则：保证ID唯一（文件名_页码_区块索引）
ANCHOR_ID_TPL = "{file_name}_{page_num}_{block_idx}"
# 溯源占位符
ANCHOR_COMMENT_TPL = "<!-- anchor_id:  -->"
PARAGRAPH_SEP = "\n\n"

#提取PDF坐标
def extract_bbox(file_path: str) -> List[Dict]:
    """提取PDF文本块的原始坐标+归一化坐标"""
    logger.info(f"开始提取PDF坐标，文件路径：{file_path}")

    #文件校验
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("仅支持PDF文件坐标提取")
    if not os.path.exists(file_path):
        raise ValueError(f"文件不存在：{file_path}")

    #初始化坐标列表
    bbox_list: List[Dict] = []
    doc = None  # 初始化PDF文档对象，方便finally关闭
    try:
        doc = fitz.open(file_path)
        logger.info(f"PDF共{doc.page_count}页，开始提取坐标")
        #遍历每一页
        for page_idx in range(doc.page_count):
            page = doc[page_idx]  # 获取当前页对象
            page_num = page_idx + 1  # 页码转成人类习惯的1开始
            page_width = page.rect.width  # 页面宽度（用于归一化）
            page_height = page.rect.height  # 页面高度（用于归一化）

            text_dict = page.get_text("dict")

            for block_idx, block in enumerate(text_dict.get("blocks", [])):
                if block.get("type") != 0:
                    continue

                block_text_parts = []
                for line in block.get("lines", []):
                    line_text = "".join(
                        span.get("text", "") for span in line.get("spans", [])
                    ).strip()
                    if line_text:
                        block_text_parts.append(line_text)

                content = "\n".join(block_text_parts).strip()
                if not content:
                    continue

                bbox = block.get("bbox", [])
                if len(bbox) != 4:
                    continue

                raw_bbox = [round(float(x), 4) for x in bbox]
                norm_bbox = [
                    round(raw_bbox[0] / page_width, 4),
                    round(raw_bbox[1] / page_height, 4),
                    round(raw_bbox[2] / page_width, 4),
                    round(raw_bbox[3] / page_height, 4),
                ]

                bbox_info = {
                    "page_num": page_num,
                    "block_idx": block_idx,
                    "raw_bbox": raw_bbox,
                    "norm_bbox": norm_bbox,
                    "content": content,
                    "content_len": len(content),
                }
                bbox_list.append(bbox_info)

        logger.info("坐标提取完成，共提取 %s 个文本块", len(bbox_list))
        return bbox_list

    except Exception as e:
        logger.error("坐标提取失败：%s", str(e), exc_info=True)
        raise
    finally:
        if doc:
            doc.close()
        gc.collect()


#生成Anchor_ID
def generate_anchor_id(file_name: str, page_num: int, block_idx: int) -> str:

    stem = os.path.splitext(file_name)[0]
    clean_name = re.sub(r"[^\w\-]+", "_", stem).strip("_")
    return ANCHOR_ID_TPL.format(file_name=clean_name, page_num=page_num, block_idx=block_idx)


#绑定溯源信息
def bind_trace_info(standard_md: str, bbox_list: List[Dict], file_name: str) -> Tuple[str, List[Dict]]:
    """
    将标准 Markdown 中的 anchor 占位符替换为真实 anchor_id，
    并生成 trace_map。
    """
    logger.info("开始绑定溯源信息，文件名：%s", file_name)

    md_paragraphs = [p.strip() for p in standard_md.split(PARAGRAPH_SEP) if p.strip()]
    valid_bbox = [b for b in bbox_list if b.get("content_len", 0) > 0]

    logger.info("Markdown段落数=%s，文本块数=%s", len(md_paragraphs), len(valid_bbox))
    if len(md_paragraphs) != len(valid_bbox):
        logger.warning("Markdown 段落数与 PDF 文本块数不一致，将按最小长度绑定")

    trace_map: List[Dict] = []
    bound_paragraphs: List[str] = []

    bind_count = min(len(md_paragraphs), len(valid_bbox))

    for para_idx in range(bind_count):
        para = md_paragraphs[para_idx]
        bbox = valid_bbox[para_idx]

        anchor_id = generate_anchor_id(file_name, bbox["page_num"], bbox["block_idx"])
        anchor_comment = f"<!-- anchor_id: {anchor_id} -->"

        if ANCHOR_COMMENT_TPL in para:
            bound_para = para.replace(ANCHOR_COMMENT_TPL, anchor_comment)
        else:
            bound_para = f"{para} {anchor_comment}"

        bound_paragraphs.append(bound_para)

        trace_map.append({
            "anchor_id": anchor_id,
            "page_num": bbox["page_num"],
            "block_idx": bbox["block_idx"],
            "raw_bbox": bbox["raw_bbox"],
            "norm_bbox": bbox["norm_bbox"],
            "content": bbox["content"],
            "para_idx": para_idx,
        })

    if len(md_paragraphs) > bind_count:
        for para in md_paragraphs[bind_count:]:
            bound_paragraphs.append(para)

    final_md = PARAGRAPH_SEP.join(bound_paragraphs)
    logger.info("溯源绑定完成，填充 %s 个 Anchor_ID，生成 %s 条溯源记录", len(trace_map), len(trace_map))
    return final_md, trace_map


#对外主函数
def get_trace_info(file_path: str, standard_md: str) -> Dict:
    """
    模块 II 主入口：提取 PDF 坐标并绑定溯源信息。
    """
    logger.info("开始执行模块II溯源，文件路径：%s", file_path)

    result = {"status": "success", "data": {}, "msg": "溯源成功"}

    try:
        bbox_list = extract_bbox(file_path)
        file_name = os.path.basename(file_path)
        final_md, trace_map = bind_trace_info(standard_md, bbox_list, file_name)

        result["data"] = {
            "file_name": file_name,
            "page_count": max((b["page_num"] for b in bbox_list), default=0),
            "block_count": len(bbox_list),
            "final_md": final_md,
            "trace_map": trace_map,
        }
        return result

    except Exception as e:
        logger.error("模块II溯源失败：%s", str(e), exc_info=True)
        result["status"] = "error"
        result["msg"] = f"溯源失败：{str(e)}"
        return result
    finally:
        gc.collect()



