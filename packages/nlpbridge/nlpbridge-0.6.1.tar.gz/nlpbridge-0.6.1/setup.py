from setuptools import setup, find_packages

setup(
    name='nlpbridge',  # 包名
    version='0.6.1',           # 版本号
    packages=find_packages(),  # 包含所有src中的包
    install_requires=[         # 依赖列表
    ],
    python_requires='>=3.10',   # Python版本要求
    entry_points={             # 安装后将创建的脚本
        'console_scripts': [
            'your_script = your_package.module:function'
        ]
    },
    author='',
    author_email='',
    description='NLP Bridge',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # 描述文件的格式
    url='https://github.com/GZU4AI/nlpbridge/tree/vitalis',  # 项目地址
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
