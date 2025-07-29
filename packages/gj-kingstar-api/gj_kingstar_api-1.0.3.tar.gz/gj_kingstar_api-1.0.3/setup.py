from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gj_kingstar_api',  # 你的包名
    version='1.0.3',  # 版本号
    description='金仕达行情封装',  # 包的简要描述
    long_description=long_description,  # 包的详细描述
    long_description_content_type='text/markdown',  # 描述文件的类型
    include_package_data=True,  # 包含包数据
    author='diy',  # 作者姓名
    author_email='471293853@qq.com',  # 作者邮箱
    packages=find_packages(exclude=['demo*','test*']),  # 自动查找包目录
    python_requires='>3.6',  # python版本要求
    install_requires=[
        'protobuf>=4.24.4',
        'websockets>=11.0.3',
    ],  # 依赖库列表 (除开python自带的包外的其他依赖库(代码中如果缺少了对应的库会导致无法运行的包))
)
