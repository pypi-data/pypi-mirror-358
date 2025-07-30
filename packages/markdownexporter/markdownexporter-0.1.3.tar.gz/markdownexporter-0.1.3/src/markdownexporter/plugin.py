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
        # ... (合并并写入文件的逻辑，和之前一样)
        print("[llm-exporter] Exporting combined markdown...")
        # ...
        print("[llm-exporter] ✅ Export successful!")