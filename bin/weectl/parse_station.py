#
#    Copyright (c) 2009-2023 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your rights.
#
"""Entry point for the "station" subcommand."""
import sys

import weectl
import weewx
import weecfg.station_config

station_create_usage = """weectl station create [--config=CONFIG-PATH] 
                             [--driver=DRIVER]
                             [--location=LOCATION]
                             [--altitude=ALTITUDE,{foot|meter}]
                             [--latitude=LATITUDE] [--longitude=LONGITUDE]
                             [--register={y,n} [--station-url=STATION_URL]]
                             [--units={us,metricwx,metric}]
                             [--skin-root=SKIN_ROOT]
                             [--sqlite-root=SQLITE_ROOT]
                             [--html-root=HTML_ROOT] 
                             [--no-prompt]
"""
station_reconfigure_usage = """weectl station reconfigure [--config=CONFIG-PATH] 
                                  [--driver=DRIVER]
                                  [--location=LOCATION]
                                  [--altitude=ALTITUDE,{foot|meter}]
                                  [--latitude=LATITUDE] [--longitude=LONGITUDE]
                                  [--register={y,n} [--station-url=STATION_URL]]
                                  [--units={us,metricwx,metric}]
                                  [--skin-root=SKIN_ROOT]
                                  [--sqlite-root=SQLITE_ROOT]
                                  [--html-root=HTML_ROOT] 
                                  [--no-prompt]
"""
station_upgrade_usage = 'weectl station upgrade [--config=CONFIG-PATH]'
station_upgrade_skins_usage = 'weectl station upgrade-skins [--config=CONFIG-PATH]'

station_usage = '\n       '.join((station_create_usage, station_reconfigure_usage,
                                  station_upgrade_usage, station_upgrade_skins_usage))

CREATE_DESCRIPTION = 'In what follows, WEEWX_ROOT is the directory that contains the ' \
                     'configuration file. For example, if "--config=/home/weewx/weewx.conf", ' \
                     'then WEEWX_ROOT will be "/home/weewx".'


def add_subparser(subparsers):
    """Add the parsers used to implement the 'station' command. """
    station_parser = subparsers.add_parser('station',
                                           usage=station_usage,
                                           description='Manages the configuration file and skins',
                                           help='Create, modify, or upgrade a config file')
    action_parser = station_parser.add_subparsers(dest='action',
                                                  title='Which action to take')

    # ---------- Action 'create' ----------
    create_station_parser = action_parser.add_parser('create',
                                                     description=CREATE_DESCRIPTION,
                                                     usage=station_create_usage,
                                                     help='Create a station config file')
    create_station_parser.add_argument('--config',
                                       metavar='CONFIG-PATH',
                                       help=f'Path to configuration file. It must not already '
                                            f'exist. Default is "{weectl.default_config_path}".')
    _add_common_args(create_station_parser)
    create_station_parser.set_defaults(func=create_station)

    # ---------- Action 'reconfigure' ----------
    reconfigure_station_parser = action_parser.add_parser('reconfigure',
                                                          usage=station_reconfigure_usage,
                                                          help='Reconfigure a station config file')

    reconfigure_station_parser.add_argument('--config',
                                            metavar='CONFIG-PATH',
                                            help='Path to configuration file. Default is '
                                                 '"/home/weewx/weewx.conf".')
    _add_common_args(reconfigure_station_parser)
    reconfigure_station_parser.set_defaults(func=reconfigure_station)

    # Action 'upgrade'
    upgrade_station_parser = action_parser.add_parser('upgrade',
                                                      usage=station_upgrade_usage,
                                                      help='Upgrade a station config file')

    # Action 'upgrade-skins'
    upgrade_skins_parser = action_parser.add_parser('upgrade-skins',
                                                    usage=station_upgrade_skins_usage,
                                                    help='Upgrade the skins')


def create_station(namespace):
    try:
        weecfg.station_config.create_station(config_path=namespace.config,
                                             driver=namespace.driver,
                                             location=namespace.location,
                                             altitude=namespace.altitude,
                                             latitude=namespace.latitude,
                                             longitude=namespace.longitude,
                                             register=namespace.register,
                                             unit_system=namespace.unit_system,
                                             skin_root=namespace.skin_root,
                                             sqlite_root=namespace.sqlite_root,
                                             html_root=namespace.html_root,
                                             no_prompt=namespace.no_prompt)
    except weewx.ViolatedPrecondition as e:
        sys.exit(e)


def reconfigure_station(namespace):
    try:
        weecfg.station_config.reconfigure_station(config_path=namespace.config,
                                                  driver=namespace.driver,
                                                  location=namespace.location,
                                                  altitude=namespace.altitude,
                                                  latitude=namespace.latitude,
                                                  longitude=namespace.longitude,
                                                  register=namespace.register,
                                                  unit_system=namespace.unit_system,
                                                  skin_root=namespace.skin_root,
                                                  sqlite_root=namespace.sqlite_root,
                                                  html_root=namespace.html_root,
                                                  no_prompt=namespace.no_prompt)
    except weewx.ViolatedPrecondition as e:
        sys.exit(e)


def _add_common_args(parser):
    """Add common arguments"""
    parser.add_argument('--driver',
                        help='Driver to use. Default is "weewx.drivers.simulator".')
    parser.add_argument('--location',
                        help='A description of the station. This will be used '
                             'for report titles. Default is "WeeWX".')
    parser.add_argument('--altitude', metavar='ALTITUDE,{foot|meter}',
                        help='The station altitude in either feet or meters. '
                             'For example, "750,foot" or "320,meter". '
                             'Default is "0, foot".')
    parser.add_argument('--latitude',
                        help='The station latitude in decimal degrees. '
                             'Default is 0.00.')
    parser.add_argument('--longitude',
                        help='The station longitude in decimal degrees. '
                             'Default is 0.00.')
    parser.add_argument('--register', choices=['y', 'n'],
                        help='Register this station in the weewx registry? '
                             'Default is "n" (do not register).')
    parser.add_argument('--station-url',
                        help='Unique URL to be used if registering the station. '
                             'Required if the station is to be registered.')
    parser.add_argument('--units', choices=['us', 'metricwx', 'metric'],
                        dest='unit_system',
                        help='Set display units to us, metricwx, or metric. '
                             'Default is "us".')
    parser.add_argument('--skin-root',
                        help='Where the skins will be located, relatve to '
                             'WEEWX_ROOT.')
    parser.add_argument('--sqlite-root',
                        help='Set the location of the sqlite directory, relative '
                             'to WEEWX_ROOT.')
    parser.add_argument('--html-root',
                        help='Where generated HTML and images will go, relative '
                             'to WEEWX_ROOT.')
    parser.add_argument('--no-prompt', type=bool,
                        help='If true, suppress prompts. Default values will be '
                             'used.')
