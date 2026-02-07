from typing import List, Dict, Optional

class VisualStyle:
    def __init__(self, id: str, name_cn: str, name_en: str, description: str, style_prompt: str, icon: Optional[str] = None):
        self.id = id
        self.name_cn = name_cn
        self.name_en = name_en
        self.description = description
        self.style_prompt = style_prompt
        self.icon = icon

    def to_dict(self):
        return {
            "id": self.id,
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "description": self.description,
            "style_prompt": self.style_prompt,
            "icon": self.icon
        }

PRESET_STYLES = [
    VisualStyle(
        id="cinematic",
        name_cn="电影感",
        name_en="Cinematic",
        description="高对比度，专业光影，电影质感",
        style_prompt="Cinematic lighting, high resolution, 8k, detailed textures, masterpiece, professional cinematography, anamorphic lens flares, depth of field."
    ),
    VisualStyle(
        id="3d_cartoon",
        name_cn="3D卡通",
        name_en="3D Cartoon",
        description="皮克斯风格，精致3D渲染",
        style_prompt="3D render, Pixar style, Disney style, Unreal Engine 5, Octane render, volumetric lighting, vibrant colors, cute and expressive characters, smooth textures."
    ),
    VisualStyle(
        id="anime",
        name_cn="日系动漫",
        name_en="Anime",
        description="新海诚风格，清新手绘感",
        style_prompt="Anime style, Japanese animation, Makoto Shinkai style, high quality, vibrant colors, clean lines, detailed backgrounds, emotional atmosphere."
    ),
    VisualStyle(
        id="cyberpunk",
        name_cn="赛博朋克",
        name_en="Cyberpunk",
        description="霓虹都市，未来科技感",
        style_prompt="Cyberpunk aesthetic, neon city, futuristic, rainy night, high-tech, glowing elements, purple and cyan lighting, synthwave style."
    ),
    VisualStyle(
        id="chinese_ink",
        name_cn="国风水墨",
        name_en="Chinese Ink",
        description="传统水墨意境，缥缈灵动",
        style_prompt="Traditional Chinese ink wash painting, ethereal, brush strokes, artistic, elegant, black and white with subtle colors, rice paper texture."
    ),
    VisualStyle(
        id="realism",
        name_cn="现实主义",
        name_en="Realism",
        description="极高还原度，写实风格",
        style_prompt="Photorealistic, hyper-realistic, high detail, sharp focus, natural lighting, documentary style, 4k, realistic skin textures."
    ),
    VisualStyle(
        id="sketch",
        name_cn="素描风",
        name_en="Sketch",
        description="铅笔线条，艺术草图感",
        style_prompt="Pencil sketch, hand-drawn, graphite, monochromatic, artistic lines, rough texture, cross-hatching, charcoal style."
    ),
    VisualStyle(
        id="oil_painting",
        name_cn="古典油画",
        name_en="Oil Painting",
        description="浓重色彩，笔触可见",
        style_prompt="Classical oil painting, Van Gogh style, thick impasto, visible brushstrokes, rich colors, canvas texture, museum quality."
    ),
    VisualStyle(
        id="pixel_art",
        name_cn="像素风",
        name_en="Pixel Art",
        description="复古8位机，怀旧风格",
        style_prompt="Pixel art style, 8-bit, retro gaming aesthetic, blocky textures, limited color palette, clean grid."
    )
]

def get_style_by_id(style_id: str) -> Optional[VisualStyle]:
    for style in PRESET_STYLES:
        if style.id == style_id:
            return style
    return None

def get_style_prompt(style_input: str) -> str:
    """
    根据用户输入的 style (可能是 ID 或名称) 获取对应的 style prompt。
    如果匹配不到，则原样返回。
    """
    style = get_style_by_id(style_input)
    if style:
        return style.style_prompt
    
    # 也尝试匹配中文/英文名
    for s in PRESET_STYLES:
        if style_input in [s.name_cn, s.name_en]:
            return s.style_prompt
            
    return style_input
