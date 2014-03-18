from setuptools import setup

setup(name='xmsgs-tools',
      version='0.2.1',
      description='Helper command line tools for parsing large Xilinx ISE FPGA build output logs',
      url='http://github.com/leaflabs/xmsgs-tools/',
      author='Bryan Newbold',
      author_email='bnewbold@leaflabs.com',
      license='MIT',
      packages=['xmsgs'],
      scripts=['xmsgsdiff', 'xmsgsprint'],
      zip_safe=False)
