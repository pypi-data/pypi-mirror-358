#########################################################################
#             GNU HEALTH HOSPITAL MANAGEMENT - GTK CLIENT               #
#                      https://www.gnuhealth.org                        #
#########################################################################
#       The GNUHealth HMIS client based on the Tryton GTK Client        #
#########################################################################
#
# SPDX-FileCopyrightText: 2008-2024 The Tryton Community <info@tryton.org>
# SPDX-FileCopyrightText: 2017-2024 GNU Health Community <info@gnuhealth.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This file is part of GNU Health.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import configparser
import gettext
import locale
import logging
import optparse
import os
import shutil
import sys
import tempfile

from gi.repository import GdkPixbuf

from gnuhealth import __version__

logger = logging.getLogger(__name__)
_ = gettext.gettext

# Create the GNU Health plugins directory at $HOME
GH_PLUGINS_DIR = os.path.join(os.environ['HOME'], 'gnuhealth_plugins')
if not os.path.isdir(GH_PLUGINS_DIR):
    os.makedirs(GH_PLUGINS_DIR, 0o700)


def _reverse_series_iterator(starting_version):
    major, minor = map(int, starting_version.split('.'))
    while major >= 0 and minor >= 0:
        yield f"{major}.{minor}"
        if minor == 0:
            major -= 1
            minor = 8
        else:
            minor -= 2 if not minor % 2 else 1


def copy_previous_configuration(config_element):
    current_version = __version__.rsplit('.', 1)[0]
    config_dir = get_config_root()
    for version in _reverse_series_iterator(current_version):
        config_path = os.path.join(config_dir, version, config_element)
        if version == current_version and os.path.exists(config_path):
            break
        elif os.path.exists(config_path):
            if os.path.isfile(config_path):
                shutil.copy(config_path, get_config_dir())
            elif os.path.isdir(config_path):
                shutil.copytree(
                    config_path,
                    os.path.join(get_config_dir(), config_element))
            break


def get_config_root():
    config_path = os.path.expanduser(os.getenv(
        'XDG_CONFIG_HOME', os.path.join('~', '.config')))
    return os.path.join(config_path, 'gnuhealth')


def get_config_dir():
    # Allow releases in the form of major.minor.patch (X.Y.N)
    # and Release Candidate versions X.YrcN
    # Returns: X.Y
    return os.path.join(
        os.environ['HOME'], '.config', 'gnuhealth',
        '.'.join(__version__.split('.', 2)[:2]).split('rc')[0])


os.makedirs(get_config_dir(), mode=0o700, exist_ok=True)


class ConfigManager(object):
    "Config manager"

    def __init__(self):
        short_version = '.'.join(__version__.split('.', 2)[:2])
        demo_server = 'federation.gnuhealth.org'
        demo_database = 'health%s' % short_version
        self.defaults = {
            'login.profile': demo_server,
            'login.login': 'demo',
            'login.service': '',
            'login.service.port': 8001,
            'login.host': demo_server,
            'login.db': demo_database,
            'login.expanded': False,
            'client.title': 'GNU Health HIS GTK Client',
            'client.toolbar': 'default',
            'client.save_tree_width': True,
            'client.save_tree_state': True,
            'client.spellcheck': False,
            'client.code_scanner_sound': True,
            'client.lang': locale.getdefaultlocale()[0],
            'client.language_direction': 'ltr',
            'client.email': '',
            'client.limit': 1000,
            'client.bus_timeout': 10 * 60,
            'icon.colors': '#11b0b8',
            'tree.colors': '#777,#dff0d8,#fcf8e3,#f2dede',
            'calendar.colors': '#fff,#3465a4',
            'graph.color': '#3465a4',
            'image.max_size': 10 ** 6,
            'image.cache_size': 1024,
            'doc.url': 'https://docs.gnuhealth.org/his',
            'bug.url': 'https://codeberg.org/gnuhealth/his/',
            'download.url': 'https://downloads.gnuhealth.org/',
            'menu.pane': 320,
        }
        self.config = {}
        self.options = {}
        self.arguments = []

    def parse(self):
        parser = optparse.OptionParser(
            version=("GNUHealth %s" % __version__),
            usage="Usage: %prog [options] [url]")
        parser.add_option(
            "-c", "--config", dest="config",
            help=_("specify alternate config file"))
        parser.add_option(
            "-d", "--dev", action="store_true",
            default=False, dest="dev", help=_("development mode"))
        parser.add_option(
            "-v", "--verbose", action="store_true",
            default=False, dest="verbose",
            help=_("logging everything at INFO level"))
        parser.add_option(
            "-l", "--log-level", dest="log_level",
            help=_("specify the log level: "
                   "DEBUG, INFO, WARNING, ERROR, CRITICAL"))
        parser.add_option(
            "-o", "--log-ouput", dest="log_output", default=None,
            help=_("specify the file used to output logging information"))
        parser.add_option(
            "-u", "--user", dest="login",
            help=_("specify the login user"))
        parser.add_option(
            "-s", "--server", dest="host",
            help=_("specify the server hostname:port"))
        parser.add_option(
            '--no-thread', default=True, action='store_false', dest='thread',
            help=_("disable thread usage"))
        opt, self.arguments = parser.parse_args()
        self.rcfile = opt.config or os.path.join(
            get_config_dir(), 'gnuhealth.conf')
        self.load()

        logging_config = {}
        if opt.log_output:
            logging_config['filename'] = opt.log_output

        loglevels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
            }
        if not opt.log_level:
            if opt.verbose:
                opt.log_level = 'INFO'
            else:
                opt.log_level = 'ERROR'
        logging_config['level'] = loglevels[opt.log_level.upper()]
        logging.basicConfig(**logging_config)

        self.options['dev'] = opt.dev
        for arg in ['login', 'host']:
            if getattr(opt, arg):
                self.options['login.' + arg] = getattr(opt, arg)
        self.options['thread'] = opt.thread

    def save(self):
        try:
            parser = configparser.ConfigParser()
            for entry in list(self.config.keys()):
                if not len(entry.split('.')) == 2:
                    continue
                section, name = entry.split('.')
                if not parser.has_section(section):
                    parser.add_section(section)
                parser.set(section, name, str(self.config[entry]))
            with open(self.rcfile, 'w') as fp:
                parser.write(fp)
        except IOError:
            logger.warn("Unable to write config file %s", self.rcfile)
            return False
        return True

    def load(self):
        parser = configparser.ConfigParser()
        try:
            parser.read([self.rcfile])
        except configparser.Error:
            config_dir = os.path.dirname(self.rcfile)
            with tempfile.NamedTemporaryFile(
                    delete=False, prefix='gnuhealth_', suffix='.conf',
                    dir=config_dir) as temp_file:
                temp_name = temp_file.name
            shutil.copy(self.rcfile, temp_name)
            logger.error(
                f"Failed to parse {self.rcfile}. "
                f"A backup can be found at {temp_name}", exc_info=True)
            return
        for section in parser.sections():
            for (name, value) in parser.items(section):
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                if section == 'client' and name == 'limit':
                    # First convert to float to be backward compatible with old
                    # configuration
                    value = int(float(value))
                self.config[section + '.' + name] = value
        return True

    def __setitem__(self, key, value, config=True):
        self.options[key] = value
        if config:
            self.config[key] = value

    def __getitem__(self, key):
        return self.options.get(
            key, self.config.get(key, self.defaults.get(key)))


CONFIG = ConfigManager()
CURRENT_DIR = os.path.dirname(__file__)
if not isinstance(CURRENT_DIR, str):
    CURRENT_DIR = str(CURRENT_DIR, sys.getfilesystemencoding())

PIXMAPS_DIR = os.path.join(CURRENT_DIR, 'data', 'pixmaps', 'gnuhealth')
if not os.path.isdir(PIXMAPS_DIR):
    try:
        import importlib.resources
        ref = importlib.resources.files('gnuhealth') / 'data/pixmaps/gnuhealth'
        with importlib.resources.as_file(ref) as path:
            PIXMAPS_DIR = path
    except ImportError:
        import pkg_resources
        PIXMAPS_DIR = pkg_resources.resource_filename(
            'gnuhealth', 'data/pixmaps/gnuhealth')
SOUNDS_DIR = os.path.join(CURRENT_DIR, 'data', 'sounds')
if not os.path.isdir(SOUNDS_DIR):
    try:
        import importlib.resources
        ref = importlib.resources.files('gnuhealth') / 'data/sounds'
        with importlib.resources.as_file(ref) as path:
            SOUNDS_DIR = path
    except ImportError:
        import pkg_resources
        SOUNDS_DIR = pkg_resources.resource_filename(
            'gnuhealth', 'data/sounds')

GNUHEALTH_ICON = GdkPixbuf.Pixbuf.new_from_file(
    os.path.join(PIXMAPS_DIR, 'gnuhealth-icon.png'))

GH_ABOUT = GdkPixbuf.Pixbuf.new_from_file(
    os.path.join(PIXMAPS_DIR, 'gnuhealth-hmis-about.png'))

BANNER = 'banner.png'
