from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.6',
  'Programming Language :: Python :: 3.7',
  'Programming Language :: Python :: 3.8',
  'Programming Language :: Python :: 3.9',
  'Programming Language :: Python :: 3.10'
]
 
setup(
  name='ViswamAuth',
  version='0.0.1',
  description='ViswamAuth is a lightweight Python module for user authentication, featuring secure sign-up, login, passcode verification, and Gmail-based password recovery. Designed for Windows console applications, it is ideal for small projects, prototypes, and educational use.',
  long_description=(
    open('README.md', encoding='utf-8').read()
    + '\n\n'
    + open('CHANGELOG.txt', encoding='utf-8').read()
    ),
  long_description_content_type='text/markdown',  
  author='Viswam Groups and Technologies',
  author_email='viswamgroupstechnologies@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='authorization,signin,login,password,viswam', 
  packages=find_packages(),
  install_requires=[
    'google-auth-oauthlib',
    'google-api-python-client'
    ]
)