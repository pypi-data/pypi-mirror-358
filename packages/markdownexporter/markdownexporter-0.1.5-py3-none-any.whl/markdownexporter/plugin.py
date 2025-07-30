# src/mkdocs_llm_exporter/plugin.py

import os
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig

# (可以添加一些类型提示，让代码更健壮)
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

class MarkdownExporter(BasePlugin):
    config_scheme = (
        ('output_file', config_options.Type(str, default='combined_docs_for_llm.md')),
        ('enabled', config_options.Type(bool, default=True)),
    )

    def on_config(self, config: MkDocsConfig):
        if not self.config.get('enabled'):
            return config
        self.pages_content = {}
        self._get_nav_paths(config.get('nav', []))
        return config

    def _get_nav_paths(self, nav_structure):
        # ... (递归获取 nav 路径的函数，和之前一样)
        # 最好在这里存储起来
        pass # 实现和之前一样

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
        if not self.config.get('enabled'):
            return markdown
        # ... (捕获 markdown 的逻辑，和之前一样)
        self.pages_content[page.file.src_path] = markdown
        return markdown

    def on_post_build(self, config: MkDocsConfig):
        if not self.config.get('enabled'):
            return

        # --- 开始修改 ---
        
        # 1. 获取 mkdocs.yml 所在的目录，这就是我们的项目根目录
        project_root = os.path.dirname(os.path.abspath(config['config_file_path']))
        
        # 2. 在项目根目录下构建输出文件的绝对路径
        output_file_name = self.config['output_file']
        output_path = os.path.join(project_root, output_file_name)

        # --- 结束修改 ---
        print("\n\n[llm-exporter] --- DIAGNOSTICS ---")
        print(f"[llm-exporter] Paths from nav config: {self.nav_paths}")
        print(f"[llm-exporter] Pages captured by on_page_markdown: {list(self.pages_content.keys())}")
        print("[llm-exporter] --- END DIAGNOSTICS ---\n")
        print(f"\n[llm-exporter] Exporting combined markdown to: {output_path}")

        # 使用新的 output_path 变量
        with open(output_path, 'w', encoding='utf-8') as f:
            # ... 写入文件的逻辑保持不变 ...
            site_name = config.get('site_name', 'Project')
            f.write(f"# {site_name} - Combined Documentation\n\n")
            # ... a's'd'f
        
        print(f"[llm-exporter] ✅ Export successful!")