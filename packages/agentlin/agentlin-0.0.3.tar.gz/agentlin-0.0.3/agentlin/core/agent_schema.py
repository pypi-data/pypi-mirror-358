import base64
import copy
import re
import uuid
import datetime
from io import BytesIO

import pandas as pd
import numpy as np
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from xlin import *
from deeplin.inference_engine import build_inference_engine, InferenceEngine
from deeplin.inference_engine.hexin_engine import retry_request
from agentlin.tools.tool_code_interpreter import CodeInterpreter


class ImageUrlData(TypedDict):
    url: str  # base64 or http url


class ContentData(TypedDict):
    type: Literal["text", "image_url"]
    text: Optional[str] = None
    image_url: Optional[ImageUrlData] = None


class DialogData(TypedDict):
    role: Literal["system", "user", "assistant", "tool", "developer"]
    content: list[ContentData]


def temporal_dataframe_to_jsonlist(df: pd.DataFrame):
    """
    Args:
        df (pd.DataFrame): df

    Returns:
        List[Dict[str, str]]: json list: [{"col1": "xxx", "col2": "xxx", ...}, ...]
    """
    json_list = []
    if "date" not in df.columns:
        df = df.reset_index().rename(columns={"index": "date"})
    for i, line in df.iterrows():
        data = dict(line)
        for k in data:
            v = data[k]
            if isinstance(v, np.float64):
                data[k] = float(v)
            elif isinstance(v, np.int64):
                data[k] = int(v)
            elif isinstance(v, np.bool_):
                data[k] = bool(v)
            elif isinstance(v, np.ndarray):
                data[k] = v.tolist()
            elif isinstance(v, (datetime.datetime, pd.Timestamp)):
                data[k] = v.isoformat()
            elif isinstance(v, np.datetime64):
                data[k] = v.astype(str)
            elif isinstance(v, pd.Series):
                data[k] = v.tolist()
            elif isinstance(v, pd.DataFrame):
                data[k] = temporal_dataframe_to_jsonlist(v)
            elif v == np.nan:
                data[k] = None
        json_list.append(data)
    return json_list


def jsonlist_to_temporal_dataframe(json_list: list[dict]):
    """
    Args:
        json_list (list[dict]): [{"col1": "xxx", "col2": "xxx", ...}, ...]

    Returns:
        pd.DataFrame: df
    """
    df = pd.DataFrame(json_list)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    return df


def dataframe_to_markdown(df: pd.DataFrame, columns: Optional[List[str]] = None):
    if not columns:
        columns = list(df.columns)
    df = df[columns]
    markdown = ""

    # Write column headers
    markdown += "|" + "index" + "|" + "|".join(columns) + "|" + "\n"
    markdown += "|" + "---" + "|" + "|".join(["----"] * len(columns)) + "|" + "\n"

    # Write data rows
    for i, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if col == "date":
                if isinstance(value, str):
                    value = pd.to_datetime(value)
                if value.hour == 0 and value.minute == 0 and value.second == 0:
                    value = value.strftime("%Y-%m-%d")
                else:
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif col == "code":
                continue
            elif col == "pct_change":
                if not isinstance(value, str):
                    value = f"{value:.2%}"
            if isinstance(value, str):
                values.append(value)
            elif isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        values_str = "|".join(values)
        markdown += "|" + str(i) + "|" + values_str + "|\n"

    markdown = markdown.strip()
    return markdown


def dataframe_to_json_str(code: str, df: pd.DataFrame, columns: Optional[List[str]] = None):
    if not columns:
        columns = list(df.columns)
    obj = {
        "code": code,
    }
    for col in columns:
        if col == "date":
            if isinstance(df.iloc[0][col], str):
                obj[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d").tolist()
            elif isinstance(df.iloc[0][col], pd.Timestamp):
                obj[col] = df[col].dt.strftime("%Y-%m-%d").tolist()
            else:
                obj[col] = df[col].tolist()
        elif col == "code":
            continue
        elif col == "pct_change":
            values = df[col].tolist()
            # 百分数格式化
            values = [f"{value:.2%}" for value in values]
            obj[col] = values
        else:
            values = df[col].tolist()
            if isinstance(values[0], float):
                values = [round(value, 4) for value in values]
            elif isinstance(values[0], int):
                values = [int(value) for value in values]
            else:
                values = [str(value) for value in values]
            obj[col] = values
    json_str_list = []
    for key, value in obj.items():
        if isinstance(value, list):
            json_str_list.append(f'  "{key}": {value},')
        elif isinstance(value, str):
            json_str_list.append(f'  "{key}": "{value}",')
        else:
            json_str_list.append(f'  "{key}": {value},')
    json_str = "{\n" + "\n".join(json_str_list) + "\n}"
    return json_str


def parse_actions(input_string: str, action_names: List[str]):
    """
    >>> input_string = \"\"\"我将使用Search工具来搜索杭州的实时天气情况。
    ActionList:
    Search: 杭州实时天气1
    Search:杭州实时天气2
    Search：杭州实时天气3\tSearch：杭州实时天气4
    Clarify: 多行澄清
    这一行也属于澄清
    可以用 : 进行选择5
    Search: 下一个动作6\"\"\"

    >>> action_names = ["Search", "Clarify"]
    >>> actionlist = parse_actions(input_string, action_names)
    >>> print(actionlist)
    [('Search', '杭州实时天气1'), ('Search', '杭州实时天气2'), ('Search', '杭州实时天气3'), ('Search', '杭州实时天气4'), ('Clarify', '多行澄清\\n这一行也属于澄清\\n可以用 : 进行选择5'), ('Search', '下一个动作6')]
    """
    # 构建正则表达式：| 作为分隔符，将所有的action名称连接在一起，形成一个正则表达式模式。
    action_pattern = "|".join(map(re.escape, action_names))

    # 正则表达式说明：
    # ({action_pattern}):         匹配action名称及其后面的冒号。
    # ([\s\S]*?)                  匹配action内容，[\s\S]*? 非贪婪匹配所有字符（包括换行符）。
    # (?=({action_pattern}):|$)   使用正向预查，确保匹配到下一个action名称或字符串结尾。
    regex = re.compile(rf"({action_pattern})\s*[:：]*([\s\S]*?)(?=({action_pattern})[:：]|$)")

    # 进行匹配
    matches = regex.findall(input_string)

    # 将匹配结果存入动作列表
    actionlist: list[tuple[str, str]] = []
    for match in matches:
        action_name = match[0]
        action_content = match[1].strip().strip("-").strip("*").strip()
        actionlist.append((action_name, action_content))
    return actionlist


def extract_action_block(text: str) -> str:
    m = re.search(r"(<action>.*?</action>)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_action(text: str) -> str:
    m = re.search(r"<action>(.*?)</action>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""

def parse_text_with_apply(text):
    """
    解析文本，提取 <apply> 标签中的内容

    Example:
    ```python
    test_text = \"\"\"
    xxx
    <apply>
    yyy
    </apply>
    zzz
    \"\"\"
    parsed = parse_text(test_text)
    print(parsed)
    ```
    Output:
    ```python
    [{'type': 'text', 'text': 'xxx'}, {'type': 'apply', 'apply': 'yyy'}, {'type': 'text', 'text': 'zzz'}]
    ```
    """

    # 定义正则表达式模式
    pattern = r'(.*?)(?:<apply>(.*?)</apply>|$)'

    # 使用正则表达式查找所有匹配项
    matches = re.finditer(pattern, text, re.DOTALL)

    result = []

    for match in matches:
        # 提取文本部分
        text_part = match.group(1).strip()
        if text_part:
            result.append({"type": "text", "text": text_part})

        # 提取 apply 部分
        apply_part = match.group(2)
        if apply_part is not None:
            apply_content = apply_part.strip()
            if apply_content:
                result.append({"type": "apply", "apply": apply_content})

    return result


def extract_apply_block(text: str) -> str:
    """
    提取 <apply> 标签中的内容
    """
    m = re.search(r"(<apply>.*?</apply>)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""

def extract_apply(text: str) -> str:
    m = re.search(r"<apply>(.*?)</apply>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def exist_apply(text: str) -> bool:
    """
    检查文本中是否存在 <apply> 标签
    """
    return re.search(r"<apply>.*?</apply>", text, re.DOTALL) is not None

def extract_tool_calls(content: str) -> list[dict]:
    # 提取 <tool_call> 标签中的内容
    tool_calls = []
    start = 0
    while True:
        start = content.find("<tool_call>", start)
        if start == -1:
            break
        end = content.find("</tool_call>", start)
        if end == -1:
            break
        tool_call = content[start + len("<tool_call>") : end]
        try:
            tool_calls.append(json.loads(tool_call))
        except json.JSONDecodeError:
            logger.error(f"无法解析的工具调用: \n{tool_call}")
        except Exception as e:
            logger.error(f"未知错误: {e}")
        start = end + len("</tool_call>")
    return tool_calls


def extract_code(content: str) -> Optional[str]:
    # 提取 <code-interpreter> 标签中的内容
    m = re.search(r"<code-interpreter>(.*?)</code-interpreter>", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_code_block(content: str) -> Optional[str]:
    # 提取 <code-interpreter> 标签中的内容
    m = re.search(r"(<code-interpreter>.*?</code-interpreter>)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_thought(text):
    # 提取 <think> 标签中的内容
    m = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def extract_execution_result(content: str) -> str:
    # 提取 <execution-result> 标签中的内容
    m = re.search(r"<execution-result>(.*?)</execution-result>", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_answer(content: str) -> str:
    # 提取 <answer> 标签中的内容
    m = re.search(r"<answer>(.*?)</answer>", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return content


def remove_thoughts(resposne: str):
    # 移除 <think> 标签中的内容
    m = re.sub(r"<think>.*?</think>", "", resposne, flags=re.DOTALL)
    return m


def remove_answer(resposne: str):
    # 移除 <answer> 标签中的内容
    m = re.sub(r"<answer>.*?</answer>", "", resposne, flags=re.DOTALL)
    return m


def remove_thoughts_in_messages(messages: list[DialogData]) -> list[DialogData]:
    new_messages = []
    for msg in messages:
        if msg["role"] == "assistant":
            content = msg["content"]
            if isinstance(content, list):
                new_content = []
                for part in content:
                    if part["type"] == "text":
                        text = part["text"]
                        text = remove_thoughts(text)
                        new_content.append({"type": "text", "text": text})
                    else:
                        new_content.append(part)
                msg["content"] = new_content
            else:
                msg["content"] = remove_thoughts(content)
        new_messages.append(msg)
    return new_messages


def add_scale_bar_in_messages(messages: list[DialogData]) -> list[DialogData]:
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            if isinstance(content, list):
                for part in content:
                    if part["type"] == "image_url":
                        base64_str = part["image_url"]["url"]
                        image = base64_to_image(base64_str)
                        image = scale_to_fit_and_add_scale_bar(image)  # 缩放图片到目标大小，并添加比例尺
                        base64_str = image_to_base64(image)
                        part["image_url"]["url"] = base64_str
    return messages


def autofix(response: str):
    if not response:
        return "<think>response 为空</think><answer>结束</answer>"
    if response.endswith("</code-interpreter"):
        return response + ">"
    return response


def synthesize_response(thought: str, motivation: str, code: str, response_type: Literal["info", "decision"] = "decision"):
    if response_type == "decision":
        return f"""\
<think>
{thought}
</think>
{motivation}
<action>
{code}
</action>
""".strip()
    elif response_type == "info":
        return f"""\
<think>
{thought}
</think>
{motivation}
<code-interpreter>
{code}
</code-interpreter>
""".strip()
    else:
        raise ValueError(f"Unknown response_type: {response_type}")


def daily_return_to_cumulative_return(time_return, initial_cash=10000):
    returns = []
    cumulative_return = 0
    dates = []
    value = initial_cash
    for date, daily_return in time_return.items():
        cumulative_return += daily_return
        value *= 1 + daily_return
        returns.append((value / initial_cash - 1) * 100)  # 转换为百分比
        dates.append(pd.to_datetime(date))  # 转换为 pandas 时间戳
    return dates, returns


def select_sub_df(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    lookback_window: int = 0,
    lookforward_window: int = 0,
    include_end_date: bool = False,
) -> pd.DataFrame:
    """
    从DataFrame中选择指定日期范围内的子DataFrame。

    Args:
        df (pd.DataFrame): 带有日期索引的DataFrame，index是日期。
        start_date (str): 起始日期，格式'YYYY-MM-DD'。
        end_date (str): 结束日期，格式'YYYY-MM-DD'。
        lookback_window (int): 向后查看的天数，默认为0。
        lookforward_window (int): 向前查看的天数，默认为0。

    Returns:
        pd.DataFrame: 指定日期范围内的子DataFrame。
    """
    # 确保索引是DatetimeIndex类型
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # 确保索引是有序的
    if not df.index.is_monotonic_increasing:
        df = df.sort_index()

    # 获取索引的时区信息
    tz = df.index.tz

    # 创建带时区的切片日期
    start = pd.Timestamp(start_date, tz=tz)
    end = pd.Timestamp(end_date, tz=tz)

    # 选择子DataFrame
    try:
        if lookback_window > 0:
            start = start - pd.Timedelta(days=lookback_window)
        if lookforward_window > 0:
            end = end + pd.Timedelta(days=lookforward_window)
        if include_end_date:
            end = end + pd.Timedelta(days=1)
        sub_df = df[start:end]
    except KeyError:
        print(f"日期 {start_date} 或 {end_date} 不在索引范围内。")
        sub_df = pd.DataFrame()

    return sub_df


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def base64_to_image(base64_str: str) -> Image.Image:
    """
    Convert a base64 string to an image.
    """
    prefix_list = [
        "data:image/png;base64,",
        "data:image/jpeg;base64,",
        "data:image/gif;base64,",
        "data:image/webp;base64,",
    ]
    for prefix in prefix_list:
        if base64_str.startswith(prefix):
            base64_str = base64_str[len(prefix) :]
            break
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    return image


def generate_short_uuid(length=8):
    # 生成标准 UUID
    uuid_value = uuid.uuid4().bytes

    # 使用 Base64 编码并转换为 URL 安全格式
    encoded = base64.urlsafe_b64encode(uuid_value).decode("ascii")

    # 移除可能的填充字符 '='
    encoded = encoded.rstrip("=")

    # 截取指定长度的字符串
    return encoded[:length]


def scale_to_fit(image: Image.Image, target_size: tuple[int, int] = (512, 512)) -> Image.Image:
    """
    将图像缩放到适合目标大小的尺寸，同时保持原始宽高比。

    args:
        image: PIL.Image.Image
            要缩放的图像。
        target_size: tuple[int, int]
            目标大小，格式为 (width, height)。

    return: PIL.Image.Image
        缩放后的图像。
    """
    original_width, original_height = image.size
    target_width, target_height = target_size

    # 计算缩放比例
    width_ratio = target_width / original_width
    height_ratio = target_height / original_height
    scale_ratio = min(width_ratio, height_ratio)
    if scale_ratio >= 1:
        # 如果图像已经小于或等于目标大小，则不需要缩放
        return image

    # 计算新的尺寸
    new_width = round(original_width * scale_ratio)
    new_height = round(original_height * scale_ratio)

    # 缩放图像
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_image


def add_scale_bar(
    image: Image.Image,
    spacing=64,
    color=(0, 0, 0),
    font_size=12,
    left_margin=50,
    top_margin=50,
    tick_length=8,
    tick_width=2,
    text_offset=2,
    origin_size: tuple[int, int] = None,
):
    """
    为图像添加顶部和左侧标尺，并将文字标签放在空白边距中，不与原图重叠。

    args:
        image: PIL.Image.Image
            要添加标尺的图像。
        spacing: int
            刻度之间的间隔，单位为像素。
        color: tuple
            刻度线和文字的颜色，RGB格式。
        font_size: int
            文字的字体大小。
        left_margin: int
            左侧边距的宽度，单位为像素。
        top_margin: int
            顶部边距的高度，单位为像素。
        tick_length: int
            刻度线的长度，单位为像素。
        tick_width: int
            刻度线的宽度，单位为像素。
        text_offset: int
            文字与刻度线之间的距离，单位为像素。
        origin_size: tuple[int, int]
            原图的尺寸，格式为 (width, height)。如果未提供，则使用图像的实际尺寸。
    return: PIL.Image.Image

    示例用法
    ```
    img = Image.open("/Pictures/example.png")
    out = add_scale_bar(
        img,
        spacing=100,
        color=(0, 0, 0),
        font_size=12,
        left_margin=50,
        top_margin=50,
        tick_length=8,
        text_offset=4,
        origin_size=(img.width, img.height)  # 可选，指定原图尺寸
    )
    out
    ```
    """
    # 加载字体
    try:
        font_path = "C:/Windows/Fonts/arial.ttf"
        if not os.path.exists(font_path):
            font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
        if not os.path.exists(font_path):
            font_path = "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf"
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    w, h = image.size
    new_w, new_h = w + left_margin, h + top_margin

    # 创建背景画布并粘贴原图
    mode = image.mode
    bg = (255, 255, 255) if mode == "RGB" else (255,)
    canvas = Image.new(mode, (new_w, new_h), bg)
    canvas.paste(image, (left_margin, top_margin))

    draw = ImageDraw.Draw(canvas)

    # 计算文字宽高的 helper
    def text_dimensions(txt):
        bbox = draw.textbbox((0, 0), txt, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    origin_width, origin_height = origin_size if origin_size else (w, h)

    # 顶部刻度和文字
    x_ticks = range(0, w + 1, spacing)
    for i, x in enumerate(x_ticks):
        # 计算刻度线的 x 坐标
        px = left_margin + x
        if i == len(x_ticks) - 1:
            # 最后一个刻度线在右侧边界
            px = new_w - tick_width
        # 刻度线
        draw.line([(px, top_margin), (px, top_margin - tick_length)], width=tick_width, fill=color)
        # 文字
        origin_x = x * origin_width // w  # 将刻度值映射到原图尺寸
        if i == len(x_ticks) - 1:
            origin_x = origin_width  # 确保最后一个刻度值是原图宽度
        txt = str(origin_x)
        tw, th = text_dimensions(txt)
        tx = px - tw / 2
        if i == len(x_ticks) - 1:
            # 最后一个刻度的文字放在刻度线的左边
            tx = tx - tw / 2
        ty = top_margin - tick_length - th - text_offset
        draw.text((tx, ty), txt, fill=color, font=font)

    # 左侧刻度和文字
    y_ticks = range(0, h + 1, spacing)
    for i, y in enumerate(y_ticks):
        # 计算刻度线的 y 坐标
        py = top_margin + y
        if i == len(y_ticks) - 1:
            # 最后一个刻度线在底部边界
            py = new_h - tick_width
        # 刻度线
        draw.line([(left_margin, py), (left_margin - tick_length, py)], width=tick_width, fill=color)
        # 文字
        origin_y = y * origin_height // h  # 将刻度值映射到原图尺寸
        if i == len(y_ticks) - 1:
            origin_y = origin_height
        txt = str(origin_y)
        tw, th = text_dimensions(txt)
        tx = left_margin - tick_length - tw - text_offset
        ty = py - th / 2
        if i == len(y_ticks) - 1:
            # 最后一个刻度的文字放在刻度线的上边
            ty = ty - th / 3 * 2
        draw.text((tx, ty), txt, fill=color, font=font)

    return canvas


def scale_to_fit_and_add_scale_bar(image: Image.Image, debug=False) -> Image.Image:
    origin_width, origin_height = image.size
    target_width, target_height = 512, 512
    if debug:
        logger.debug(f"原图尺寸: {origin_width}x{origin_height}, 目标尺寸: {target_width}x{target_height}")
    image = scale_to_fit(image, target_size=(target_width, target_height))  # 缩放图片到目标大小，为了省 image tokens
    if debug:
        logger.debug(f"缩放后图片尺寸: {image.size[0]}x{image.size[1]}")
    image = add_scale_bar(image, origin_size=(origin_width, origin_height))  # 保持缩放后的比例尺为原图的比例尺，方便模型在原图上定位坐标和长宽用于裁剪
    if debug:
        logger.debug(f"添加比例尺后图片尺寸: {image.size[0]}x{image.size[1]}")
    return image


def save_jupyter_notebook(history: list[DialogData], thoughts: list[DialogData], path: str):
    cells = []

    def append_raw(text: str):
        if not text or len(text.strip()) == 0:
            return
        cells.append(
            {
                "cell_type": "raw",
                "metadata": {},
                "source": [text],
                "outputs": [],
            }
        )

    def append_markdown(text: str):
        if not text or len(text.strip()) == 0:
            return
        cells.append(
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [text],
                "outputs": [],
            }
        )

    def append_code(code: str):
        if not code or len(code.strip()) == 0:
            return
        cells.append(
            {
                "cell_type": "code",
                "metadata": {},
                "source": [code],
                "outputs": [],
            }
        )

    for i, msg in enumerate(history[:-1] + thoughts + [history[-1]]):
        icon = "🤖" if msg["role"] == "assistant" else "👤"
        append_markdown(f"# {icon}")
        if isinstance(msg["content"], list):
            for part in msg["content"]:
                if part["type"] == "text":
                    text = part["text"]
                    if "code-interpreter" in part and not part["code-interpreter"]:
                        append_markdown(text)
                    else:
                        thought = extract_thought(text)
                        if thought and len(thought.strip()) > 10:
                            append_raw("<think>")
                            append_markdown(thought)
                            append_raw("</think>")
                            text = remove_thoughts(text)
                        code_block = extract_code_block(remove_thoughts(text))
                        if code_block:
                            code = extract_code(code_block)
                            for i, split in enumerate(text.split(code_block)):
                                append_markdown(split)
                                if i < len(text.split(code_block)) - 1:
                                    append_raw("<code-interpreter>")
                                    append_code(code)
                                    append_raw("</code-interpreter>")
                        elif "code-interpreter" in part and part["code-interpreter"]:
                            code = text
                            append_code(code)
                        else:
                            code_block = extract_action_block(remove_thoughts(text))
                            if code_block:
                                code = extract_action(code_block)
                                for i, split in enumerate(text.split(code_block)):
                                    append_markdown(split)
                                    if i < len(text.split(code_block)) - 1:
                                        append_raw("<action>")
                                        append_code(code)
                                        append_raw("</action>")
                            else:
                                code = extract_code(text)
                                if code:
                                    append_code(code)
                                else:
                                    answer = extract_answer(text)
                                    if answer:
                                        append_markdown(answer)
                                    else:
                                        if len(history) - 1 < i < len(history) - 1 + len(thoughts) and msg["role"] == "user":
                                            # planning 阶段的 user 为环境
                                            append_raw(text)
                                        else:
                                            append_markdown(text)
                elif part["type"] == "image_url":
                    image_url = part["image_url"]
                    if isinstance(image_url, dict):
                        image_url = image_url["url"]
                    image = base64_to_image(image_url)
                    origin_image = image
                    image = scale_to_fit_and_add_scale_bar(image)  # 缩放图片到目标大小，并添加比例尺
                    md_text = "| {left_img} | {right_image} |\n| --- | --- |\n| ![模型看到的图片]({image_url}) | ![原始图片]({origin_image_url}) |".format(
                        left_img=f"模型看到的图片尺寸: {image.width}x{image.height}",
                        right_image=f"原始图片 {origin_image.width}x{origin_image.height}",
                        image_url=image_to_base64(image),
                        origin_image_url=image_to_base64(origin_image),
                    )
                    append_markdown(md_text)
                    if "plotly_json" in part:
                        fig_json = part["plotly_json"]
                        cells.append(
                            {
                                "cell_type": "code",
                                "metadata": {},
                                "source": [],
                                "outputs": [
                                    {
                                        "output_type": "display_data",
                                        "data": {
                                            "application/vnd.plotly.v1+json": fig_json,
                                        },
                                        "metadata": {},
                                    }
                                ],
                            }
                        )
        else:
            append_markdown(msg["content"])
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "rft",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3,
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.14",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 2,
    }
    save_json(notebook, path)


def content_to_text(content: list[ContentData] | ContentData | str):
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        type_str = content["type"]
        if type_str == "text":
            return content["text"]
        elif type_str == "image":
            return f"[image]"
        return str(content)
    elif isinstance(content, list):
        return "\n".join([content_to_text(c) for c in content])
    return ""


def messages_to_text(messages: list[DialogData]):
    lines = []
    for msg in messages:
        icon = "🤖" if msg["role"] == "assistant" else "👤"
        content = content_to_text(msg["content"])
        lines.append(f"{icon}【{msg['role']}】: {content}")
    return "\n".join(lines)


class AgentState:
    def __init__(
        self,
        history_messages: list[DialogData] = [],
        decision_messages_list: list[list[DialogData]] = [],
        information_messages_list: list[list[DialogData]] = [],
    ):
        self.history_messages = history_messages
        self.decision_messages_list = decision_messages_list
        self.information_messages_list = information_messages_list

    def append_history_message(self, message: DialogData):
        self.history_messages.append(message)

    def append_decision_messages(self, messages: list[DialogData]):
        self.decision_messages_list.append(messages)

    def append_information_messages(self, messages: list[DialogData]):
        self.information_messages_list.append(messages)


class AgentCore:
    def __init__(self, engine: InferenceEngine, name: str):
        self.simulator: Optional["Simulator"] = None
        self.engine = engine
        self.name = name

    def bind_simulator(self, simulator: "Simulator"):
        self.simulator = simulator

    def inference(self, messages: list[DialogData], **inference_args):
        # 调用推理引擎获取回复
        inference_args.setdefault("max_tokens", 10 * 1024)
        inference_args.setdefault("debug", True)
        inference_args.setdefault("multi_modal", True)
        inference_args.setdefault("max_retry", 3)
        messages = copy.deepcopy(messages)
        messages = remove_thoughts_in_messages(messages)
        messages = add_scale_bar_in_messages(messages)
        @retry_request
        def retry_inference(**inference_args):
            response = self.engine.inference_one(messages, **inference_args)[0]
            if response is not None:
                response = self.autofix(response)
            return response
        response = retry_inference(**inference_args)
        if not response:
            # response is None 的时候，inference 内部已经尽力还是失败了，此时我们自动修复
            return "<think>response 为空</think><action># 观望</action>"
        return response

    def autofix(self, response: str):
        # return None 表示需要重新推理，采样新的response
        # 以下情况，inference 成功了，需要自动修复 response
        if response.endswith("</code-interpreter"):
            return response + ">"
        case1 = re.match(r"^\s*<think>(.*?)</think>\s*<action>(.*?)</action>\s*$", response, re.DOTALL)
        case2 = re.match(r"^\s*<think>(.*?)</think>\s*<code-interpreter>(.*?)</code-interpreter>\s*$", response, re.DOTALL)
        if not case1 and not case2:
            # 如果没有 <think> 和 <action> 或 <code-interpreter> 标签，先考虑think缺失情况
            case3 = re.match(r"^\s*<think>(.*?)</think>\s*$", response, re.DOTALL)
            if case3:
                # think 没有缺失，可能是<action>或<code-interpreter>缺失
                # 我们建议 retry inference，通过 return None 来触发
                return None
            else:
                # 没有 <think> 标签，可能存在 <action> 或 <code-interpreter> 标签
                case4 = re.match(r"^\s*<action>(.*?)</action>\s*$", response, re.DOTALL)
                case5 = re.match(r"^\s*<code-interpreter>(.*?)</code-interpreter>\s*$", response, re.DOTALL)
                # if case4:
                #     # 只有 <action> 标签，直接添加 <think> 标签
                #     response = f"<think>无思考</think><action>{case4.group(1)}</action>"
                # elif case5:
                #     # 只有 <code-interpreter> 标签，直接添加 <think> 标签
                #     response = f"<think>无思考</think><code-interpreter>{case5.group(1)}</code-interpreter>"
                if case4 or case5:
                    # 跳过思考，直接出现 <action> 或 <code-interpreter> 标签
                    # 这是允许的
                    pass
                else:
                    # 既没有 <think> 标签，也没有 <action> 或 <code-interpreter> 标签
                    # 此时 response 里什么也没有，建议 retry inference
                    return None
        return response

    def think_and_answer(
        self,
        history_messages: list[DialogData],
        information_messages: list[DialogData] = [],
        **inference_args,
    ):
        # history_messages 里定义了任务以及足够的上下文
        # 本函数是在 history_messages 的基础上进行深度推理，继续获取更多信息，做出最后的决策
        # information_messages 是额外的信息，可能是从外部数据源获取的. 可以注入 information_messages 来提供更多上下文信息。
        # history_messages 和 information_messages 都是对话消息列表，每个消息是一个字典，包含 "role" 和 "content" 字段。
        # history_messages + information_messages 生成 response，如果response 不是 decision，将 response 拼回 information_messages 中，继续推理。
        # 直到 response 是决策性消息，才将其拼回 history_messages 中。此时 information_messages 是 history_messages 最后一轮对话的中间结果。
        # inference_args 是推理引擎的参数
        debug = inference_args.get("debug", False)
        current_step = 0
        if len(information_messages) > 0:
            current_step = sum([1 for m in information_messages if m["role"] == "assistant"])
        while True:
            current_step += 1
            if debug:
                logger.debug(f"当前推理深度: {current_step}, 历史消息数量: {len(history_messages)}")
            # 调用推理引擎获取回复
            messages = history_messages + information_messages
            response = self.inference(messages, **inference_args)
            if debug:
                logger.debug(f"🤖【assistant】: {response}")

            # 判断是否有代码解释器标记
            code = extract_code(remove_thoughts(response))
            if code:
                # 如果有代码解释器标记，为规划阶段，执行代码
                content_to_gpt, content_to_display = self.simulator.execute(code)
                # logger.info(json.dumps(content_to_gpt, ensure_ascii=False, indent=2))
                information_messages.append({"role": "assistant", "content": [{"type": "text", "text": response}]})
                information_messages.append({"role": "user", "content": content_to_gpt})
            else:
                # 没有代码解释器标记时，为回答阶段，添加到历史记录并返回
                history_messages.append({"role": "assistant", "content": [{"type": "text", "text": response}]})
                break
        return response


class Simulator:
    def __init__(
        self,
        work_dir: str,
        tool_context_for_agent: Optional[str] = None,
        tool_context_for_interpreter: Optional[str] = None,
        debug=False,
    ):
        self.work_dir = work_dir
        self.debug = debug
        self.agent: AgentCore = None
        self._text_tool_context_for_agent = tool_context_for_agent
        self._text_tool_context_for_interpreter = tool_context_for_interpreter
        self.initialize_code_interpreter(work_dir, debug, self._tool_context_for_interpreter())

    def initialize_code_interpreter(self, work_dir: str, debug: bool, initial_code_context: str):
        self.code_interpreter = CodeInterpreter(work_dir, debug)
        self.code_interpreter.execute_code(initial_code_context)

    def execute(self, code: str):
        return self.code_interpreter.execute_code(code)

    def reset(self):
        self.code_interpreter.restart_jupyter_kernel()

    def set_tool_context(self, for_agent: str, for_interpreter: str):
        """
        设置工具的上下文信息。
        Args:
            for_agent (str): 用于 LLM 的提示
            for_interpreter (str): 用于代码解释器实际执行
        """
        self._text_tool_context_for_agent = for_agent
        self._text_tool_context_for_interpreter = for_interpreter
        self.initialize_code_interpreter(self.work_dir, self.debug, self._tool_context_for_interpreter())

    def tool_context_for_agent(self):
        """
        获取工具的上下文信息，用于 LLM 的提示。
        【拼进 prompt 里的】
        Returns:
            str: 工具的上下文信息
        """
        if not self._text_tool_context_for_agent:
            self._text_tool_context_for_agent = load_text("tool_context_for_agent.py")
        return self._text_tool_context_for_agent

    def _tool_context_for_interpreter(self):
        """
        获取工具的上下文信息，用于代码解释器实际执行。
        【实际执行的】
        Returns:
            str: 工具的上下文信息
        """
        if not self._text_tool_context_for_interpreter:
            self._text_tool_context_for_interpreter = load_text("tool_context_for_interpreter.py")
        return self._text_tool_context_for_interpreter

    def bind_agent(self, agent: AgentCore):
        self.agent = agent
