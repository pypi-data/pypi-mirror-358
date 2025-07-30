# src/markdownexporter/plugin.py
import os
import re
import time
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig

# 这个模块可能需要手动安装： pip install mkdocstrings
# 或者在你的插件依赖中声明它
from mkdocstrings.plugin import MkdocstringsPlugin

class MarkdownExporter(BasePlugin):
    config_scheme = (
        ('output_file', config_options.Type(str, default='llm_docs_final.md')),
        ('enabled', config_options.Type(bool, default=True)),
    )

    def __init__(self):
        self.log_prefix = "[markdownexporter]"
        self.handler = None
        self.nav_paths = []
        print(f"{self.log_prefix} 🕵️  Plugin instance created.")
        super().__init__()

    def on_config(self, config: MkDocsConfig):
        print(f"{self.log_prefix} on_config hook running...")
        
        # 获取 mkdocstrings 插件的实例，这是核心！
        try:
            mkdocstrings_plugin = config['plugins']['mkdocstrings']
            if isinstance(mkdocstrings_plugin, MkdocstringsPlugin):
                self.handler = mkdocstrings_plugin.get_handler('python')
                print(f"{self.log_prefix} ✅ Successfully obtained 'python' handler from mkdocstrings.")
            else:
                 print(f"{self.log_prefix} ❌ ERROR: Could not get a valid mkdocstrings plugin instance.")
        except KeyError:
            print(f"{self.log_prefix} ❌ ERROR: 'mkdocstrings' plugin not found in config. This plugin depends on it.")

        # 获取 nav 路径
        self.nav_paths = self._get_nav_paths(config.get('nav', []))
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

    # 我们不再需要 on_page_markdown 钩子了，可以删除它

    def on_post_build(self, config: MkDocsConfig):
        print(f"{self.log_prefix} on_post_build hook running...")

        if not self.config.get('enabled') or not self.handler:
            if not self.handler:
                print(f"{self.log_prefix} Skipping export because mkdocstrings handler is not available.")
            else:
                print(f"{self.log_prefix} Skipping export because plugin is disabled.")
            return

        project_root = os.path.dirname(os.path.abspath(config['config_file_path']))
        docs_dir = config.get('docs_dir', 'docs')
        output_path = os.path.join(project_root, self.config['output_file'])
        
        # 用于查找 ::: identifier 模式的正则表达式
        # 它会匹配 ':::', 后面可能跟一些空格, 然后是标识符
        identifier_regex = re.compile(r':::[\s]*([\w\._-]+)')

        print(f"{self.log_prefix} Exporting combined and rendered markdown to: {output_path}")
        
        exported_count = 0
        with open(output_path, 'w', encoding='utf-8') as f_out:
            site_name = config.get('site_name', 'Project')
            f_out.write(f"# {site_name} - Combined Documentation\n\n")

            for page_path in self.nav_paths:
                full_path = os.path.join(docs_dir, page_path)
                if not os.path.exists(full_path):
                    print(f"{self.log_prefix} ⚠️  File not found, skipping: {full_path}")
                    continue

                f_out.write(f"\n\n---\n\n")
                f_out.write(f"<!-- Original File: {page_path} -->\n")
                f_out.write(f"## (Content from: {page_path})\n\n")

                with open(full_path, 'r', encoding='utf-8') as f_in:
                    content = f_in.read()
                
                # 查找并替换所有 mkdocstrings 占位符
                def render_match(match):
                    identifier = match.group(1)
                    print(f"{self.log_prefix}   -> Rendering identifier: {identifier}")
                    try:
                        # 使用 handler.render() 来获取渲染后的 Markdown!
                        rendered_markdown = self.handler.render(identifier, {})
                        return rendered_markdown
                    except Exception as e:
                        print(f"{self.log_prefix}   ❌ ERROR rendering {identifier}: {e}")
                        return f"Failed to render `{identifier}`."

                # 使用 re.sub 和一个回调函数来替换所有匹配项
                processed_content = identifier_regex.sub(render_match, content)
                
                f_out.write(processed_content)
                exported_count += 1
                print(f"{self.log_prefix}  - Appended and processed: {page_path}")
        
        print(f"{self.log_prefix} ✅ Export successful! Exported {exported_count} pages.")