# meson.build
project('your-project',
  'c', 'cpp',
  version: '0.1.0',
  default_options: [
    'buildtype=release',
    'c_std=c11',
    'cpp_std=c++17',
  ]
)

py_mod = import('python')
py = py_mod.find_installation(
  'python3',
  required: true,
)

# For Python extension modules
subdir('src')
