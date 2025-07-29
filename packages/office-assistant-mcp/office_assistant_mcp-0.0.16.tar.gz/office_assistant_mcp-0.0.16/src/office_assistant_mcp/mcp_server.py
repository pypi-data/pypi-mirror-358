from mcp.server.fastmcp import FastMCP
import random
from office_assistant_mcp import playwright_util
from office_assistant_mcp import playwright_message
from office_assistant_mcp.prompt import get_planning_customer_group_prompt, get_planning_message_plan_prompt
from mcp.server.fastmcp.prompts import base
import os
import re

from shared.log_util import log_error, log_info


from shared.error_handler import format_exception_message

mcp = FastMCP("mcp_demo_server", port=8088)


async def server_log_info(msg: str):
    """发送信息级别的日志消息"""
    await mcp.get_context().session.send_log_message(
        level="info",
        data=msg,
    )


@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "这是应用的全部配置"

#  定义动态 Resource


@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"用户全部信息： {user_id}"


# @mcp.tool()
# def ask_weather(city: str) -> dict[str, str]:
#     """返回指定城市的天气"""
#     return {"city": city, "weather": "晴天", "temperature": 25}


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


@mcp.tool()
async def login_sso() -> str:
    """如果需要授权登录，则使用本工具进行飞书SSO登录"""
    try:
        await server_log_info("【T】开始飞书SSO登录")
        result = await playwright_util.login_sso()
        await server_log_info(f"【T】登录结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】飞书SSO登录出错: {str(e)}")
        return format_exception_message("登录过程中出错", e)


@mcp.tool()
async def planning_create_customer_group(user_query: str) -> str:
    """创建客群的第1步，根据用户输入，检查输入信息是否完整，如果完整则规划创建客群的详细步骤。    
    Args:
        user_query: 用户输入的创建客群的原样指令
    """
    try:
        await server_log_info(f"【T】开始规划创建客群: {user_query}")
        
        # 构建发送给LLM的提示词
        prompt = get_planning_customer_group_prompt(user_query)
        
        # 调用LLM获取规划结果
        result = await playwright_util.send_llm_request(prompt)
        await server_log_info(f"【T】规划创建客群结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】规划创建客群时出错: {str(e)}")
        log_error(f"规划创建客群时出错: {str(e)}")
        
        # 检查是否是因为llm_key未设置导致的错误
        if "llm_key" in str(e) and "not found" in str(e).lower():
            return "请先设置llm_key！"
        
        return "检查参数和创建规划异常，跳过规划直接执行"


@mcp.tool()
async def planning_create_message_plan(user_query: str) -> str:
    """创建短信计划的第1步，必须先创建短信计划的参数检查和规划，才能执行后续的具体步骤。根据用户输入，检查输入信息是否完整，如果完整则规划创建短信计划的详细步骤。    
    Args:
        user_query: 用户输入的创建短信计划的原样指令
    """
    try:
        await server_log_info(f"【T】开始规划创建短信计划: {user_query}")
        
        # 构建发送给LLM的提示词
        prompt = get_planning_message_plan_prompt(user_query)
        
        # 调用LLM获取规划结果
        result = await playwright_util.send_llm_request(prompt)
        await server_log_info(f"【T】规划创建短信计划结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】规划创建短信计划时出错: {str(e)}")
        log_error(f"规划创建短信计划时出错: {str(e)}")
        
        # 检查是否是因为llm_key未设置导致的错误
        if "llm_key" in str(e) and "not found" in str(e).lower():
            return "请先设置llm_key！"
            
        return "检查参数和创建规划异常，跳过规划直接执行"

@mcp.tool()
async def open_create_customer_group_page() -> str:
    """打开客群页面并点击新建客群按钮"""
    try:
        await server_log_info("【T】开始打开客群页面")
        result = await playwright_util.open_create_customer_group_page()
        return f"客群页面已打开: {result}"
    except Exception as e:
        await server_log_info(f"【E】打开客群页面时出错: {str(e)}")
        return format_exception_message("打开客群页面时出错", e)

@mcp.tool()
async def fill_customer_group_info(group_name: str, business_type: str="活动运营") -> str:
    """填写客群基本信息

    Args:
        group_name: 客群名称
        business_type: 业务类型，可选值：社群运营、用户运营、活动运营、商品运营、内容运营、游戏运营
    """
    try:
        await server_log_info(f"【T】开始填写客群信息: {group_name}, {business_type}")
        result = await playwright_util.fill_customer_group_info(group_name, business_type)
        return f"客群信息填写成功: {result}"
    except Exception as e:
        await server_log_info(f"【E】填写客群信息时出错: {str(e)}")
        return format_exception_message("填写客群信息时出错", e)


@mcp.tool()
async def fill_customer_group_user_tag_set_basic_info(
    identity_types: list[str] = None,
    v2_unregistered: str = None
) -> str:
    """新增客群时填写客群用户标签中的基础信息，包括用户身份及是否推客用户。
    
    Args:
        identity_types: 新制度用户身份，可多选，例如 ["P1", "V3"]
                       可选值包括: "P1", "P2", "P3", "P4", "V1", "V2", "V3", "VIP"
                       不区分大小写，如"p1"也会被识别为"P1"
        v2_unregistered: V2以上未注册推客用户，可选值: "是", "否"
    """
    try:
        await server_log_info("【T】开始填写客群用户标签基础信息")
        result = await playwright_util.fill_customer_group_user_tag_set_basic_info(
            identity_types=identity_types,
            v2_unregistered=v2_unregistered
        )
        await server_log_info(f"【T】填写基础信息结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】填写客群用户标签基础信息时出错: {str(e)}")
        return format_exception_message("填写基础信息时出错", e)


@mcp.tool()
async def fill_customer_click_add_behavior_tag_button(tag_position: str = "left") -> str:
    """添加一个用户行为标签。

    用于构建用户行为逻辑结构，标签的添加顺序与嵌套结构决定逻辑表达的语义。

    Args:
        tag_position: 当前标签在逻辑结构中的层级位置。可选值：
            - "left"：表示当前标签是一个新的“一级标签”，与上一标签处于并列关系。
            - "right"：表示当前标签是上一个标签的“子标签”，用于表示嵌套逻辑。

    说明：
        - 若标签是独立条件（A 且 B 且 C 或 A 或 B），则使用 "left"
        - 若某个标签是在另一个标签的内部逻辑块中（如 A 或 (B 且 C)），则 B 为 "left"，C 为 "right"
        - 是否使用 "right" 取决于逻辑结构是否存在嵌套，而非语义内容是否相似
    """
    try:
        await server_log_info(f"【T】开始点击添加行为标签按钮: position={tag_position}")
        result = await playwright_util.click_add_behavior_tag_button(tag_position)
        await server_log_info(f"【T】点击添加行为标签按钮结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】点击添加行为标签按钮时出错: {str(e)}")
        return format_exception_message("点击添加行为标签按钮时出错", e)


@mcp.tool()
async def fill_customer_fill_behavior_tag_form(
    row_index: int = 0,
    time_range_type: str = "最近",
    time_range_value: str = None,
    action_type: str = "做过",
    theme: str = "购买", 
    dimension: str = None, 
    dimension_condition: str = None,
    dimension_value: str = None,
    metric: str = None,
    metric_condition: str = None,
    metric_value: str = None,
    metric_value_end: str = None 
) -> str:
    """填写指定行的行为标签表单，在点击完所有添加按钮后调用此函数填写表单内容
    
    Args:
        row_index: 要填写的标签行索引，从0开始计数。例如：填写第二个标签，row_index=1。
        time_range_type: 时间范围类型："最近"或"任意时间"，必选，没有指定具体时间范围，则选"任意时间"。
        time_range_value: 时间范围值，天数，如："7"，可选，只有选择了"最近"类型时才填写。
        action_type: 行为类型："做过"或"没做过"，必选。
        theme: 主题："购买"或"搜索"等，必选。
        dimension: 维度选项，可选但重要，用于精确指定购买的物品、类目、品牌等信息。当用户提及特定商品或类目时，必须提取并传入。当theme="购买"时可用：
            - 类目相关：["后台一级类目", "后台二级类目", "后台三级类目", "后台四级类目"]
              (条件均为=或!=，值为字符串，支持下拉列表多选)
            - 商品相关：["商品品牌", "商品名称", "商品id"] 
              (条件均为=或!=，品牌需从下拉列表选择，其他为字符串)
            - 其他："统计日期"。
        dimension_condition: 维度条件，当指定了dimension时必须同时提供，通常为=或!=，部分情况支持"包含"等
        dimension_value: 维度值，当指定了dimension时必须同时提供，多个值可用逗号(,或，)分隔
        metric: 指标名称，必填。当theme="购买"时可用：
            ["购买金额", "购买件数", "购买净金额", "购买订单数"]
            (所有指标条件均支持=, >=, <=, <, >，值均为数字)。
            其它指标相关定义：老客：任意时间购买件数>=1的用户；未消费：没有做过，购买，购买金额>=1；
        metric_condition: 指标条件，必填：=, >=, <=, <, >, 介于
        metric_value: 指标值，必填：数字类型，当metric_condition="介于"时为范围开始值
        metric_value_end: 指标范围结束值，必填：仅当metric_condition="介于"时使用
    """
    try:
        await server_log_info(f"【T】开始填写第{row_index+1}行{theme}用户行为标签表单")
        result = await playwright_util.fill_behavior_tag_form(
            row_index=row_index,
            time_range_type=time_range_type,
            time_range_value=time_range_value,
            action_type=action_type,
            theme=theme,
            dimension=dimension,
            dimension_condition=dimension_condition,
            dimension_value=dimension_value,
            metric=metric,
            metric_condition=metric_condition,
            metric_value=metric_value,
            metric_value_end=metric_value_end
        )
        await server_log_info(f"【T】填写用户行为标签表单结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】填写用户行为标签表单时出错: {str(e)}")
        return format_exception_message("填写用户行为标签表单时出错", e)


@mcp.tool()
async def fill_customer_toggle_behavior_tag_relation_to_or(relation_position: int = 0) -> str:
    """将行为标签之间的默认“且”关系修改为“或”关系。

    默认所有标签之间的关系均为“且”，如需要将某组标签设为“或”，需调用本函数。

    Args:
        relation_position: 表示要修改的第几个“且”关系，编号从 0 开始。
            - 所有结构中的“且”关系按逻辑结构从上到下、从左到右编号
            - 包括最外层和所有嵌套层在内，全部参与编号（不再跳过外层）
            - 编号依据逻辑结构中“且”关系的先后顺序，不依据函数调用顺序

    示例：
        - 结构 “A 或 B 或 C”：三个标签为同级关系，仅包含一个“且”需要修改 → relation_position=0
        - 结构 “(A 或 B) 且 (C 或 D)”：
            - relation_position=0 → 最外层第一层级的(A 或 B)与(C 或 D)
            - relation_position=1 → A 与 B
            - relation_position=2 → C 与 D
    """
    try:
        await server_log_info(f"【T】开始切换第{relation_position+1}个用户行为标签关系")
        result = await playwright_util.toggle_relation_to_or(relation_position)
        await server_log_info(f"【T】切换用户行为标签关系结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】切换用户行为标签关系时出错: {str(e)}")
        return format_exception_message("切换用户行为标签关系时出错", e)

@mcp.tool()
async def estimate_customer_group_size() -> str:
    """预估客群人数。
    
    成功填写所有客群创建表单后，点击预估客群人数按钮，获取预估的客群规模。
    """
    try:
        await server_log_info("【T】开始预估客群人数")
        result = await playwright_util.estimate_customer_group_size()
        await server_log_info(f"【T】预估客群人数结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】预估客群人数时出错: {str(e)}")
        return format_exception_message("预估客群人数时出错", e)

@mcp.tool()
async def open_create_message_plan_page() -> str:
    """打开创建短信计划页面，以便创建短信计划"""
    try:
        await server_log_info("【T】开始打开短信计划页面")
        result = await playwright_message.open_create_message_plan_page()
        await server_log_info(f"【T】打开短信计划页面结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】打开短信计划页面时出错: {str(e)}")
        return format_exception_message("打开短信计划页面时出错", e)


@mcp.tool()
async def fill_message_group_id(group_id: str) -> str:
    """创建短信计划，填写指定的客群id
    
    Args:
        group_id: 客群ID，格式为数字字符串
    """
    try:
        await server_log_info(f"【T】开始搜索并选择客群: {group_id}")
        result = await playwright_message.fill_message_group_id(group_id)
        await server_log_info(f"【T】选择客群结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】搜索并选择客群时出错: {str(e)}")
        return format_exception_message("搜索并选择客群时出错", e)


@mcp.tool()
async def fill_message_plan_info(plan_name: str, send_date: str, send_time: str) -> str:
    """填写短信计划的标题、发送日期和时间
    
    Args:
        plan_name: 计划名称，格式为字符串，例如："0412高质量用户圣牧纯牛奶"
        send_date: 发送日期，格式为"YYYY-MM-DD"，例如："2025-04-12"
        send_time: 发送时间，格式为"HH:MM:SS"，例如："18:00:00"
    """
    try:
        await server_log_info(f"【T】开始填写短信计划基本信息: {plan_name}, {send_date} {send_time}")
        result = await playwright_message.fill_message_plan_info(plan_name, send_date, send_time)
        await server_log_info(f"【T】填写短信计划基本信息结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】填写短信计划基本信息时出错: {str(e)}")
        return format_exception_message("填写短信计划基本信息时出错", e)


@mcp.tool()
async def fill_message_content(content: str, product_id: str) -> str:
    """设置发送短信的文本内容，通过商品id生成并插入商品链接
    
    Args:
        content: 短信内容，格式为字符串
        product_id: 商品ID，格式为数字字符串
    """
    try:
        await server_log_info(f"【T】开始设置短信内容和商品链接: 内容长度:{len(content)}, 商品ID:{product_id}")
        result = await playwright_message.fill_message_content(content, product_id)
        # 总长70字符，短链占25个字符，固定文案10个字符
        sms_length_check_result = "【T】注意短信长度超过限制" if len(content) > 35 else ""
        await server_log_info(f"【T】设置短信内容和商品链接结果: {result}")
        
        department_result = await playwright_message.set_department_info()
        await server_log_info(f"【T】设置默认费用归属部门结果: {department_result}")
        
        return result + "\n" + sms_length_check_result + "\n" + department_result
    except Exception as e:
        await server_log_info(f"【E】设置短信内容和商品链接时出错: {str(e)}")
        return format_exception_message("设置短信内容和商品链接时出错", e)


@mcp.tool()
async def get_current_time() -> str:
    """获取当前时间字符串，格式为YYYY-MM-DD HH:MM:SS"""
    try:
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"当前时间: {current_time}"
    except Exception as e:
        await server_log_info(f"【E】获取当前时间时出错: {str(e)}")
        return format_exception_message("获取当前时间时出错", e)


@mcp.tool()
async def get_current_version() -> str:
    """获取当前工具的版本号"""
    try:
        version = playwright_util.get_current_version()
        return f"当前版本号: {version}"
    except Exception as e:
        await server_log_info(f"【E】获取版本号时出错: {str(e)}")
        return format_exception_message("获取版本号时出错", e)


@mcp.tool()
async def judge_category_brand_or_product(keyword: str) -> str:
    """判断关键词是属于类目、品牌还是商品名
    
    当不清楚用户输入的词是属于哪个级别的类目，或者是否是品牌，或者是商品名时使用此工具。
    工具会返回以下情况之一：
    1. 类目类型：返回具体的类目级别和名称
    2. 品牌类型：返回"品牌：品牌名称"
    3. 商品名：不属于上述两类则返回"商品名：商品名称"
    
    Args:
        keyword: 需要判断的关键词，如"面膜"、"素野"等
    """
    try:
        await server_log_info(f"【T】开始判断关键词类型: {keyword}")
        result = playwright_message.judge_category_or_brand_type(keyword)
        await server_log_info(f"【T】判断结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】判断关键词类型时出错: {str(e)}")
        return format_exception_message("判断关键词类型时出错", e)


def main():
    """MCP服务入口函数"""
    log_info(f"服务启动")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
