import os
import tempfile
from playwright.async_api import async_playwright
from shared.log_util import log_debug, log_info, log_error

# 浏览器路径配置
CHROME_PATH = None
CHROME_USER_DATA_DIR = None

# 全局变量用于缓存playwright实例
_playwright_instance = None
_browser_instance = None
_page_instance = None


def reset_playwright_cache():
    """重置playwright缓存，以便创建新的浏览器和页面实例"""
    log_info("reset playwright cache")
    global _playwright_instance, _browser_instance, _page_instance
    _playwright_instance = None
    _browser_instance = None
    _page_instance = None


async def remove_lock_files():
    """删除浏览器用户数据目录下的锁文件，防止浏览器打不开"""
    if not CHROME_USER_DATA_DIR:
        log_info("使用默认chromium浏览器，无需清理缓存")
        return
        
    lock_files_to_remove = ["SingletonLock", "SingletonCookie", "SingletonSocket"]
    if os.path.exists(CHROME_USER_DATA_DIR):
        for file_name in lock_files_to_remove:
            file_path = os.path.join(CHROME_USER_DATA_DIR, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    log_info(f"Successfully removed lock file: {file_path}")
                except OSError as e:
                    log_info(f"Error removing lock file {file_path}: {e}")
    else:
        log_info(f"User data directory not found, skipping lock file cleanup: {CHROME_USER_DATA_DIR}")


async def create_playwright(user_data_dir_name: str = "office_assistant_mcp_chrome_user_data"):
    """创建playwright实例
    
    Args:
        user_data_dir_name: 用户数据目录名称，不同业务可以使用不同的目录
    """
    global CHROME_USER_DATA_DIR
    
    # 如果CHROME_USER_DATA_DIR为空，则在临时目录下创建一个固定的用户数据目录
    if CHROME_USER_DATA_DIR is None:
        temp_dir = os.path.join(tempfile.gettempdir(), user_data_dir_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        CHROME_USER_DATA_DIR = temp_dir
        log_info(f"使用Chrome临时用户数据目录: {CHROME_USER_DATA_DIR}")
        
    await remove_lock_files()
    p = await async_playwright().start()
    
    # 浏览器启动参数
    launch_options = {
        'user_data_dir': CHROME_USER_DATA_DIR,
        'headless': False,  # 显示浏览器界面
        'args': ['--start-maximized']  # 浏览器全屏启动
    }
    
    # 如果CHROME_PATH不为空，则使用指定的浏览器路径
    if CHROME_PATH:
        launch_options['executable_path'] = CHROME_PATH
    
    browser = await p.chromium.launch_persistent_context(**launch_options)
    return p, browser


async def get_playwright():
    """获取playwright对象,如果没有则新建，有则返回全局缓存的对象"""
    global _playwright_instance, _browser_instance, _page_instance

    if _playwright_instance is None or _browser_instance is None:
        log_debug(f"获取playwright，创建新实例")
        _playwright_instance, _browser_instance = await create_playwright()
        _page_instance = await _browser_instance.new_page()
        _page_instance.set_default_timeout(5000)
    else:
        log_debug(f"获取playwright，使用缓存")
    return _playwright_instance, _browser_instance, _page_instance


async def close_playwright():
    """关闭并清除缓存的playwright和browser实例"""
    log_debug(f"close playwright")
    global _playwright_instance, _browser_instance, _page_instance

    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None

    if _playwright_instance:
        await _playwright_instance.stop()
        _playwright_instance = None

    _page_instance = None