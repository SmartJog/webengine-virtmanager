dnl Process this file with autoconf to produce a configure script.
AC_PREREQ([2.67])
AC_INIT([webengine-virtmanager],[0.1.0])

AM_INIT_AUTOMAKE([foreign])
AM_PATH_PYTHON([2.5])

AC_PATH_PROG(TXT2TAGS, [txt2tags])

AC_SUBST([webenginedir], [\$\(datadir\)/webengine])
AC_SUBST([webenginesysconfdir], [\$\(sysconfdir\)/webengine])
AC_SUBST([webengineappdir], [\$\(webenginedir\)/app/webengine])
AC_SUBST([virtmanagerdir], [\$\(webengineappdir\)/virtmanager])

AC_CONFIG_FILES([
	Makefile
])
AC_OUTPUT
