project('cablegram',         version: '0.1.0',
  meson_version: '>= 0.40.0',
)

i18n = import('i18n')

subdir('data')
subdir('cablegram')
subdir('po')
subdir('ui')
subdir('style')

meson.add_install_script('build-aux/meson/postinstall.py')