import asyncio
from playwright.async_api import Page, Locator
from shared.log_util import log_debug, log_info, log_error
from shared.browser_manager import get_playwright


async def is_element_visible(locator: Locator, timeout: int = 5000) -> bool:
    """判断元素是否可见，如果可见返回True，否则返回False，最多等待timeout毫秒
    
    Args:
        locator: Playwright元素定位器
        timeout: 等待超时时间，默认5秒
        
    Returns:
        bool: 元素存在且可见返回True，超时返回False
    """
    try:
        await locator.wait_for(state="visible", timeout=timeout)
        return True
    except Exception as e:
        log_debug(f"等待元素可见超时: {e}")
        return False


async def open_commission_setting_page():
    """打开聚宝赞商品结算设置页面"""
    _, _, page = await get_playwright()
    log_debug(f"open_commission_setting_page:{page}")
    
    # 聚宝赞商品结算设置页面URL
    open_url = "https://m.sesuntech.cn/main_menu/?siteId=12777#%E5%95%86%E5%93%81/%E5%95%86%E5%93%81%E5%BA%93/%E5%95%86%E5%93%81%E7%BB%93%E7%AE%97%E8%AE%BE%E7%BD%AE"
    
    # 打开佣金设置页面
    await page.goto(open_url)

    # await page.pause()
    login_button = page.get_by_role("button", name="登录")
    if await is_element_visible(login_button, timeout=3000):
        return "请用户先手动登录，再重新打开原网址进行后续操作！"
    return "已打开聚宝赞商品结算设置页面"


async def set_product_commission_plan(product_id: str, profit_sharing_plan: str):
    """设置商品分润方案
    
    Args:
        product_id: 商品ID
    """
    _, _, page = await get_playwright()
    log_debug(f"set_product_commission_plan for product_id:{product_id}")

    # await page.pause()

    alert_element = page.get_by_role("alert").locator("div").nth(2)
    if await is_element_visible(alert_element, 2000):
        await alert_element.click()

    label_element = page.get_by_label("", exact=True).get_by_role("img")
    # label_element_count = await label_element.count()
    if await is_element_visible(label_element, 2000):
        await label_element.click()
    await page.get_by_role("menuitem", name="商品", exact=True).click()
    await page.get_by_text("商品结算设置").nth(1).click()

    iframe = page.locator("#iframe_active").content_frame
    await iframe.get_by_role("textbox", name="请输入商品ID").click()
    await iframe.get_by_role("textbox", name="请输入商品ID").fill(product_id)
    await iframe.get_by_role("button", name="查询").click()
    await iframe.get_by_text("奖励配置").nth(1).click()
    
    # 等待系统默认设置控件出现
    system_default_radio = iframe.get_by_role("radio", name="系统默认设置")
    
    # 使用封装的等待方法，等待10秒
    if not await is_element_visible(system_default_radio):
        log_error("等待系统默认设置控件超时")
        return '未找到"系统默认设置收益规则"，设置佣金失败'
    

    await system_default_radio.click()
    log_info(f"system_default_radio is selected1: {await system_default_radio.is_checked()}")
    # 检查system_default_radio是否被选中，如果未被选中，等待一秒然后点击，点击完后再次检查，还未选中则重复上述操作，最多循环5次
    await asyncio.sleep(1)
    log_info(f"system_default_radio is selected2: {await system_default_radio.is_checked()}")
    for i in range(5):
        if not await system_default_radio.is_checked():
            await asyncio.sleep(1)
            await system_default_radio.click()
            if i == 4:
                log_error("system_default_radio未被选中，请用户手动处理")
                return f"system_default_radio未被选中，请用户手动处理"
        else:
            break
    
    await iframe.get_by_role("radio", name="否").click()
    await iframe.get_by_role("textbox", name="请选择").click()
    # await asyncio.sleep(1)  # 等待下拉框加载
    item_list = iframe.get_by_role("listitem").filter(has_text=profit_sharing_plan)
    
    # 使用封装的等待方法等待下拉列表加载完成
    if not await is_element_visible(item_list):
        log_error("等待下拉列表加载超时")
        return f"下拉列表加载失败，无法为商品 {product_id} 设置分润方案"
    
    await item_list.click()
    # await iframe.get_by_role("button", name="保存").click()
    save_button_count = await iframe.get_by_role("button", name="保存").count()
    print(f"save_button_count: {save_button_count}")
    
    return f"已为商品 {product_id} 设置分润方案，请用户确认后手动点击保存"
