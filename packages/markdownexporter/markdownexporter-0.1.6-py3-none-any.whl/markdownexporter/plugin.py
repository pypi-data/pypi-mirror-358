# src/markdownexporter/plugin.py
import os
import time
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files

class MarkdownExporter(BasePlugin):
    config_scheme = (
        ('output_file', config_options.Type(str, default='combined_docs_for_llm.md')),
        ('enabled', config_options.Type(bool, default=True)),
    )

    def __init__(self):
        """类的构造函数，在实例创建时运行。"""
        # 使用你实际的插件名，让日志更清晰
        self.log_prefix = "[markdownexporter]" 
        self.instance_id = int(time.time() * 1000)
        print(f"{self.log_prefix} 🕵️  New instance created with ID: {self.instance_id}")
        
        # 提前初始化，避免 AttributeError
        self.nav_paths = []
        self.pages_content = {}
        super().__init__()

    def on_config(self, config: MkDocsConfig):
        print(f"{self.log_prefix} on_config called for instance ID: {self.instance_id}")
        
        # 更新 self.nav_paths
        self.nav_paths = self._get_nav_paths(config.get('nav', []))
        
        if not self.nav_paths:
            print(f"{self.log_prefix} WARNING: No 'nav' configuration found or it's empty.")
        return config

    def _get_nav_paths(self, nav_structure):
        paths = []
        for item in nav_structure:
            if isinstance(item, str):
                paths.append(item)
            elif isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        paths.append(value)
                    elif isinstance(value, list):
                        paths.extend(self._get_nav_paths(value))
        return paths

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
        if not self.config.get('enabled'):
            return markdown
        
        self.pages_content[page.file.src_path] = markdown
        return markdown

    def on_post_build(self, config: MkDocsConfig):
        print(f"{self.log_prefix} on_post_build called for instance ID: {self.instance_id}")

        if not self.config.get('enabled'):
            print(f"{self.log_prefix} Plugin disabled, skipping export for instance ID: {self.instance_id}.")
            return

        # 因为我们在 __init__ 中已经初始化了 nav_paths，所以不再需要 hasattr 检查
        # 直接检查 nav_paths 是否有内容即可
        if not self.nav_paths:
            print(f"{self.log_prefix} WARNING on instance ID: {self.instance_id}. "
                  "The 'nav_paths' attribute is empty. This might be due to a missing 'nav' in mkdocs.yml "
                  "or an unexpected re-instantiation of the plugin.")
        
        project_root = os.path.dirname(os.path.abspath(config['config_file_path']))
        output_path = os.path.join(project_root, self.config['output_file'])
        
        print(f"{self.log_prefix} Exporting combined markdown to: {output_path}")

        exported_count = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            site_name = config.get('site_name', 'Project')
            f.write(f"# {site_name} - Combined Documentation\n\n")

            for path in self.nav_paths:
                if path in self.pages_content:
                    content = self.pages_content[path]
                    f.write(f"\n\n---\n\n")
                    f.write(f"<!-- Original File: {path} -->\n")
                    f.write(f"## (Content from: {path})\n\n")
                    f.write(content)
                    exported_count += 1
            
        print(f"{self.log_prefix} ✅ Export successful! Exported {exported_count} pages for instance ID: {self.instance_id}")
