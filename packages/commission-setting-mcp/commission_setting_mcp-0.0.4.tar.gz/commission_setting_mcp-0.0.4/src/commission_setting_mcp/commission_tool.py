"""佣金设置工具类，基于playwright_commission模块的简化版本"""

from shared.log_util import log_info, log_error
from shared.error_handler import format_exception_message
from . import playwright_commission


class CommissionSettingTool:
    """佣金设置工具类"""
    
    async def open_commission_setting_page(self) -> str:
        """打开聚宝赞商品结算设置页面"""
        try:
            log_info("正在打开聚宝赞商品结算设置页面...")
            result = await playwright_commission.open_commission_setting_page()
            log_info(result)
            return result
        except Exception as e:
            log_error(f"打开聚宝赞商品结算设置页面失败: {str(e)}")
            return format_exception_message("打开聚宝赞商品结算设置页面失败", e)
    
    async def set_product_commission_plan(self, product_id: str, profit_sharing_plan: str) -> str:
        """设置商品分润方案
        
        Args:
            product_id: 商品ID
        """
        try:
            log_info(f"正在为商品 {product_id} 设置分润方案...")
            result = await playwright_commission.set_product_commission_plan(product_id, profit_sharing_plan)
            log_info(result)
            return result
        except Exception as e:
            log_error(f"设置商品分润方案失败: {str(e)}")
            return format_exception_message("设置商品分润方案失败", e)