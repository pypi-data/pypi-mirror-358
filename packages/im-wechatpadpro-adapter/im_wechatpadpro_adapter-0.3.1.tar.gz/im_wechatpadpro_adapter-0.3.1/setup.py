from setuptools import setup, find_packages
import io
import os

version = os.environ.get('RELEASE_VERSION', '0.3.1'
'').lstrip('v')

setup(
    name="im_wechatpadpro_adapter",
    version=version,
    packages=find_packages(),
    include_package_data=True,  # 这行很重要
    package_data={
        "im_wechatpadpro_adapter": ["example/*.yaml", "example/*.yml", "assets/*.png"],
    },
    install_requires=["kirara-ai>=3.2.0","pydantic", "moviepy"
    ],
    entry_points={
        'chatgpt_mirai.plugins': [
            'im_wechatpadpro_adapter = im_wechatpadpro_adapter:WeChatAdapterPlugin'
        ]
    },
    author="chuanSir",
    author_email="416448943@qq.com",

    description="im_wechatpadpro_adapter  for lss233/kirara-ai",
    long_description=io.open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/chuanSir123/kirara-ai-wechat",
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU Affero General Public License v3',
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/chuanSir123/kirara-ai-wechat/issues",
        "Documentation": "https://github.com/chuanSir123/kirara-ai-wechat/wiki",
        "Source Code": "https://github.com/chuanSir123/kirara-ai-wechat",
    },
    python_requires=">=3.8",
)
