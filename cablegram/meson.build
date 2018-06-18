pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'cablegram')
gnome = import('gnome')

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)
#conf.set('pythondir', meson.source_root())
#conf.set('pyexecdir', meson.source_root())

configure_file(
  input: 'cablegram.in',
  output: 'cablegram',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

cablegram_sources = [
  '__init__.py',
  'gi_composites.py',
  'main.py',
  'login.py',
  'universe_window.py',
  'sidebar.py',
  'chat_view.py'
]

install_data(cablegram_sources, install_dir: moduledir)

wrapper_sources = [
  'wrapper/__init__.py',
  'wrapper/universe.py',
  'wrapper/dialog.py'
]

install_data(wrapper_sources, install_dir: join_paths(moduledir, 'wrapper'))