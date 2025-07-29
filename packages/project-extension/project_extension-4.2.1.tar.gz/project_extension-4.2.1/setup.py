from setuptools import setup, find_packages
with open('README.md', encoding='utf-8') as f:
  long_description=f.read()
setup(
  name='project_extension',                  # 项目名称
  version='4.2.1',                   # 版本号
  packages=find_packages(),          # 自动发现所有包和子包
  install_requires=[                 # 依赖项
      'requests>=2.25.1',
  ],
  author='Guoyingxu',
  author_email='Guoyx@itshixun.com',
  description='A short description',
  long_description =long_description,
  long_description_content_type='text/markdown',
  url='',
  classifiers=[                      # 项目分类信息
      'Programming Language :: Python :: 3',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
  ],
  python_requires='>=3.6',            # Python 版本要求
)
 