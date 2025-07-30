from mcp.server.fastmcp import FastMCP

from commission_setting_mcp import playwright_commission
from shared.error_handler import format_exception_message
from shared.log_util import log_error, log_info
from typing import Dict, List, Any

mcp = FastMCP("commission_setting_mcp_server", port=8089)



async def server_log_info(msg: str):
    """发送信息级别的日志消息"""
    await mcp.get_context().session.send_log_message(
        level="info",
        data=msg,
    )


@mcp.tool()
async def open_product_settlement_page() -> str:
    """商品配置分润方案第一步，打开商品结算设置页面，打开成功才能执行后续步骤"""
    try:
        await server_log_info("正在打开商品结算页面...")
        result = await playwright_commission.open_commission_setting_page()
        await server_log_info(f"打开商品结算页面结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】打开商品结算页面时出错: {str(e)}")
        return format_exception_message("打开商品结算页面时出错", e)



@mcp.tool()
async def complete_product_settlement_workflow(product_id: str, profit_sharing_plan: str = "云集自营-买手") -> str:
    """商品配置分润方案第二步，成功打开商品结算设置页面之后，为指定商品，设置分润方案
    
    Args:
        product_id: 商品ID
        profit_sharing_plan: 供应商名称，例如："云集自营-买手"
    """
    try:
        await server_log_info(f"开始商品 {product_id} 的完整结算配置流程...")
        result = await playwright_commission.set_product_commission_plan(product_id, profit_sharing_plan)
        await server_log_info(f"完整工作流程结果: {result}")
        return result
    except Exception as e:
        await server_log_info(f"【E】完整工作流程执行时出错: {str(e)}")
        return format_exception_message("完整工作流程执行时出错", e)


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
        import importlib.metadata
        version = importlib.metadata.version("commission-setting-mcp")
        return f"当前版本号: {version}"
    except Exception as e:
        await server_log_info(f"【E】获取版本号时出错: {str(e)}")
        return format_exception_message("获取版本号时出错", e)

def main():
    """佣金设置MCP服务入口函数"""
    log_info(f"佣金设置MCP服务启动")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()