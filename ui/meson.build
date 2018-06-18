pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'cablegram')
gnome = import('gnome')

gnome.compile_resources('ui',
  'cablegram.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)