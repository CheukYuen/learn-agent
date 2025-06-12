import asyncio
import os
import sys
import tempfile
from pathlib import Path
import psutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

from browser_use import Agent, BrowserSession

api_key = os.getenv('DEEPSEEK_API_KEY', '')
if not api_key:
	raise ValueError('DEEPSEEK_API_KEY is not set')


async def run_sensorsdata_analysis():
	# 方案一：连接到现有Chrome浏览器（需要启动时带debug端口）
	# 首先启动Chrome: /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
	# 或者 chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug (Windows)
	
	# 获取用户数据目录
	user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")  # macOS
	# user_data_dir = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")  # Windows
	# user_data_dir = os.path.expanduser("~/.config/google-chrome")  # Linux
	
	agent = Agent(
		task=(
			'访问 https://family.demo.sensorsdata.cn/dashboard/?project=EbizDemo&product=sbp_family&id=414&dash_type=lego 页面，'
			'如果需要登录，请等待手动登录完成后继续。'
			'然后按以下步骤操作：'
			'1. 在顶部绿色导航栏中找到"分析"菜单项并点击它'
			'2. 在弹出的下拉菜单中，在"行为分析"部分找到"事件分析"选项并点击'
			'3. 等待进入事件分析页面，页面加载完成后'
			'4. 在页面底部找到绿色的"查询"按钮并点击它'
			'请确保每个步骤都完成后再进行下一步。'
		),
		llm=ChatDeepSeek(
			base_url='https://api.deepseek.com/v1',
			model='deepseek-reasoner',
			api_key=SecretStr(api_key),
		),
		use_vision=False,
		max_failures=3,
		max_actions_per_step=1,
		# 方案一选项：连接到现有Chrome实例
		# browser_config={
		# 	"headless": False,
		# 	"user_data_dir": user_data_dir,  # 使用现有用户数据
		# 	"executable_path": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS Chrome路径
		# },
		
		# 方案二选项：保存浏览器数据以保持登录状态
		# browser_config={
		# 	"headless": False,
		# 	"user_data_dir": "/tmp/browser-use-session",  # 持久化用户数据
		# },
		
		# 方案三选项：连接到远程调试端口（如果Chrome已启动）
		# browser_config={
		# 	"connect_to_existing": True,
		# 	"debugging_port": 9222,
		# },
	)

	await agent.run()


# 方案四：手动登录辅助函数
async def run_with_manual_login():
	"""允许手动登录的方案"""
	import time
	
	agent = Agent(
		task=(
			'访问 https://family.demo.sensorsdata.cn/dashboard/?project=EbizDemo&product=sbp_family&id=414&dash_type=lego 页面，'
			'如果出现登录页面，请暂停60秒等待手动登录。'
			'登录完成后继续执行任务。'
		),
		llm=ChatDeepSeek(
			base_url='https://api.deepseek.com/v1',
			model='deepseek-reasoner',
			api_key=SecretStr(api_key),
		),
		use_vision=False,  # 启用视觉以识别登录页面
		max_failures=3,
		max_actions_per_step=1,
	)
	
	print("🔐 如果需要登录，请在浏览器中手动完成登录...")
	print("💡 登录完成后，Agent将自动继续执行任务")
	
	await agent.run()


async def run_with_existing_browser():
    """连接到已经打开并登录的Chrome浏览器"""
    print("🔗 正在连接到已打开的Chrome浏览器...")
    
    # 方法E：通过CDP URL连接
    browser_session = BrowserSession(
        cdp_url="http://localhost:9222"  # 连接到调试端口
    )
    
    agent = Agent(
        task=(
            '在当前已登录的浏览器中执行以下操作：'
            '1. 导航到 https://family.demo.sensorsdata.cn/dashboard/?project=EbizDemo&product=sbp_family&id=414&dash_type=lego'
            '2. 在顶部绿色导航栏中找到"分析"菜单项并点击它'
            '3. 在弹出的下拉菜单中，在"行为分析"部分找到"事件分析"选项并点击'
            '4. 等待进入事件分析页面，页面加载完成后'
            '5. 在页面底部找到绿色的"查询"按钮并点击它'
        ),
        llm=ChatDeepSeek(
            base_url='https://api.deepseek.com/v1',
            model='deepseek-reasoner',
            api_key=SecretStr(api_key),
        ),
        browser_session=browser_session,
        use_vision=False,
        max_failures=3,
        max_actions_per_step=1,
    )
    
    await agent.run()


def get_chrome_debug_pid():
    """获取带有调试端口的Chrome进程PID"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'remote-debugging-port=9222' in cmdline:
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

async def run_with_browser_pid():
    """通过PID连接到已开启的Chrome"""
    chrome_pid = get_chrome_debug_pid()
    
    if not chrome_pid:
        print("❌ 未找到带有调试端口的Chrome进程")
        print("请先启动: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
        return
    
    print(f"✅ 找到Chrome进程，PID: {chrome_pid}")
    
    browser_session = BrowserSession(browser_pid=chrome_pid)
    
    agent = Agent(
        task=(
            '在当前已登录的浏览器中执行以下操作：'
            '1. 导航到 https://family.demo.sensorsdata.cn/dashboard/?project=EbizDemo&product=sbp_family&id=414&dash_type=lego'
            '2. 在顶部绿色导航栏中找到"分析"菜单项并点击它'
            '3. 在弹出的下拉菜单中，在"行为分析"部分找到"事件分析"选项并点击'
            '4. 等待进入事件分析页面，页面加载完成后'
            '5. 在页面底部找到绿色的"查询"按钮并点击它'
        ),
        llm=ChatDeepSeek(
            base_url='https://api.deepseek.com/v1',
            model='deepseek-reasoner',
            api_key=SecretStr(api_key),
        ),
        browser_session=browser_session,
        use_vision=False,
        max_failures=3,
        max_actions_per_step=1,
    )
    
    await agent.run()


if __name__ == '__main__':
	print("🚀 启动方案选择:")
	print("1. 方案一：自动启动浏览器（需要登录）")
	print("2. 方案二：连接到已打开的浏览器（需要先手动启动Chrome）")
	
	choice = input("请输入选择 (1/2): ").strip()
	
	if choice == "2":
		print("\n📋 使用方案二的步骤:")
		print("1. 请先在终端执行以下命令启动Chrome:")
		print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
		print("     --remote-debugging-port=9222 \\")
		print("     --user-data-dir=/tmp/chrome-sensorsdata")
		print("\n2. 在打开的浏览器中手动登录神策数据")
		print("3. 登录完成后，按回车继续...")
		input()
		
		asyncio.run(run_with_existing_browser())
	else:
		asyncio.run(run_sensorsdata_analysis())
