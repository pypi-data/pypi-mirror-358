import argparse
import requests
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm.rich import tqdm
from pathlib import Path
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from queue import Queue
import time

class WebScraper:
    def __init__(self, output_dir, browser_type='edge'):
        self._init_logger()
        self.logger.info("初始化下载器...")
        
        # 初始化基本参数
        self.output_dir = Path(output_dir)
        self.browser_type = browser_type.lower()
        self.visited_urls = set()
        self.session = requests.Session()
        self.file_extensions = [
            '.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', 
            '.ico', '.svg', '.py', '.sb', '.sb2', '.sb3', '.cpp', 
            '.java', '.c', '.ini', '.cfg', '.txt'
        ]
        
        # 初始化浏览器驱动
        self.driver = self._init_selenium()
        
        # 初始化任务队列和线程池
        self.executor = ThreadPoolExecutor(max_workers=15)
        self.url_queue = Queue()
        self.pending_tasks = set()

    def _init_logger(self):
        """初始化日志配置"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _init_selenium(self):
        """初始化浏览器驱动"""
        self.logger.info(f"正在初始化 {self.browser_type} 浏览器驱动...")
        try:
            if self.browser_type == 'edge':
                options = EdgeOptions()
                options.use_chromium = True
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--ignore-certificate-errors")
                return webdriver.Edge(
                    service=EdgeService(EdgeChromiumDriverManager().install()),
                    options=options
                )
            elif self.browser_type == 'chrome':
                options = ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--ignore-certificate-errors")
                return webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options
                )
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {str(e)}")
            raise

    def _normalize_url(self, url):
        """标准化URL格式"""
        parsed = urlparse(url)
        if not parsed.scheme:
            url = f"https://{url}"
        return urljoin(url, urlparse(url).path)

    def _get_absolute_url(self, base, link):
        """生成绝对URL"""
        return urljoin(base, link)

    def _should_download(self, url):
        """判断是否需要下载该资源"""
        # 去重检查
        if url in self.visited_urls:
            return False
        
        # 扩展名检查
        parsed = urlparse(url)
        path = parsed.path.lower()
        return any(path.endswith(ext) for ext in self.file_extensions)

    def _get_save_path(self, url):
        """生成文件保存路径"""
        parsed = urlparse(url)
        path = parsed.path
        
        # 处理无路径的情况
        if not path or path == '/':
            path = '/index.html'
        # 处理目录路径
        elif path.endswith('/'):
            path += 'index.html'
        
        # 清理查询参数和锚点
        clean_path = Path(path.split('?')[0].split('#')[0])
        return self.output_dir / parsed.netloc / clean_path.relative_to('/')

    def _save_file(self, content, save_path):
        """保存文件到本地"""
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(content)
        self.logger.debug(f"已保存: {save_path}")

    def _download_resource(self, url):
        """下载单个资源"""
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            save_path = self._get_save_path(url)
            self._save_file(response.content, save_path)
            
            # 返回HTML内容用于后续解析
            if save_path.suffix == '.html':
                return response.text
            return None
        except Exception as e:
            self.logger.warning(f"下载失败 {url}: {str(e)}")
            return None

    def _process_page(self, html, base_url):
        """解析页面并提取新链接"""
        soup = BeautifulSoup(html, 'html.parser')
        new_links = set()

        # 提取所有可能包含链接的元素
        for tag in ['a', 'link', 'script', 'img']:
            for element in soup.find_all(tag):
                attr = 'href' if tag in ['a', 'link'] else 'src'
                if url := element.get(attr):
                    absolute_url = self._get_absolute_url(base_url, url)
                    normalized_url = self._normalize_url(absolute_url)
                    if self._should_download(normalized_url):
                        new_links.add(normalized_url)

        return new_links

    def _add_to_queue(self, urls):
        """将新链接添加到队列"""
        for url in urls:
            if url not in self.visited_urls:
                self.url_queue.put(url)
                self.visited_urls.add(url)
                self.logger.debug(f"发现新链接: {url}")

    def start_crawling(self, start_url):
        """启动爬取流程"""
        start_url = self._normalize_url(start_url)
        self.url_queue.put(start_url)
        self.visited_urls.add(start_url)

        # 初始化增强版进度条
        with tqdm(
            desc="总进度",
            total=1,  # 初始至少1个任务
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{remaining} remaining]",
            dynamic_ncols=True
        ) as main_pbar:
            start_time = time.time()
            try:
                while not self.url_queue.empty() or self.pending_tasks:
                    # 计算处理速度
                    elapsed = time.time() - start_time
                    speed = main_pbar.n / elapsed if elapsed > 0 else 0
                    
                    # 更新描述信息
                    main_pbar.set_postfix({
                        'speed': f'{speed:.1f} pages/s',
                        'queue': self.url_queue.qsize()
                    })

                    # 提交队列任务
                    current_queue_size = self.url_queue.qsize()
                    while not self.url_queue.empty() and len(self.pending_tasks) < 100:
                        url = self.url_queue.get()
                        future = self.executor.submit(self._process_url, url)
                        self.pending_tasks.add(future)
                        
                        # 动态更新总任务数
                        new_total = current_queue_size + len(self.pending_tasks)
                        main_pbar.total = max(new_total, 1)
                        main_pbar.refresh()

                    # 处理完成的任务
                    done, _ = as_completed(self.pending_tasks, timeout=5), set()
                    for future in done:
                        self.pending_tasks.remove(future)
                        main_pbar.update(1)
                        if result := future.result():
                            self._add_to_queue(result)
                            main_pbar.total = self.url_queue.qsize() + len(self.pending_tasks)
                            main_pbar.refresh()

                    time.sleep(0.5)
            except KeyboardInterrupt:
                self.logger.warning("用户中断操作，正在完成剩余任务...")
                # 等待现有任务完成
                while len(self.pending_tasks) > 0:
                    done, _ = as_completed(self.pending_tasks, timeout=5), set()
                    for future in done:
                        self.pending_tasks.remove(future)
                        main_pbar.update(1)
            finally:
                # 显式关闭进度条并计算总耗时
                main_pbar.close()
                total_time = time.time() - start_time
                self.logger.info(f"任务完成！总计处理 {main_pbar.n} 个页面，耗时 {total_time:.1f} 秒")

    def _process_url(self, url):
        """处理单个URL"""
        self.logger.info(f"正在处理: {url}")
        try:
            # 使用Selenium加载动态内容
            self.driver.get(url)
            time.sleep(2)  # 等待动态加载
            html = self.driver.page_source
            
            # 保存主页面
            save_path = self._get_save_path(url)
            self._save_file(html.encode(), save_path)
            
            # 提取并返回新链接
            return self._process_page(html, url)
        except Exception as e:
            self.logger.error(f"处理失败 {url}: {str(e)}")
            return set()

    def shutdown(self):
        """关闭资源"""
        self.logger.info("正在清理资源...")
        self.executor.shutdown()
        self.driver.quit()
        self.logger.info("资源清理完成")

def main():
    parser = argparse.ArgumentParser(description="全站下载工具")
    parser.add_argument('url', help="目标网站URL")
    parser.add_argument('-o', '--output', default='htyy-download-output',
                       help="输出目录（默认：htyy-download-output）")
    parser.add_argument('-b', '--browser', choices=['edge', 'chrome'],
                       default='edge', help="浏览器选择（默认：edge）")
    
    args = parser.parse_args()
    
    scraper = WebScraper(args.output, args.browser)
    try:
        scraper.start_crawling(args.url)
    except KeyboardInterrupt:
        scraper.logger.warning("用户中断操作！")
    finally:
        scraper.shutdown()
    scraper.logger.info(f"下载完成！文件保存在：{args.output}")

if __name__ == '__main__':
    main()