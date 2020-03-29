from discodos import log
import time
import yaml
from pathlib import Path
import os

# util: checks for numbers
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

# util: print a UI message
def print_help(message):
    print(''+str(message)+'\n')

# util: ask user for some string
def ask_user(text=""):
    return input(text)

# read yaml
def read_yaml(yamlfile):
    """expects path/file"""
    try:
        with open(str(yamlfile), "r") as fyamlfile:
            return yaml.load(fyamlfile, Loader=yaml.SafeLoader)
    except IOError as errio:
        log.error("Can't find %s.", yamlfile)
        #raise errio
        #raise SystemExit(3)
        return False
    except yaml.parser.ParserError as errparse:
        log.error("ParserError in %s.", yamlfile)
        #raise errparse
        raise SystemExit(3)
    except yaml.scanner.ScannerError as errscan:
        log.error("ScannerError in %s.", yamlfile)
        #raise errscan
        raise SystemExit(3)
    except Exception as err:
        log.error(" trying to load %s.", yamlfile)
        raise err
        #raise SystemExit(3)

def join_sep(iterator, seperator):
    it = map(str, iterator)
    seperator = str(seperator)
    string = next(it, '')
    for s in it:
        string += seperator + s
    return string

class Config():
    def __init__(self):
        # path handling
        discodos_lib = Path(os.path.dirname(os.path.abspath(__file__)))
        self.discodos_root = discodos_lib.parents[0]
        log.info("Config.discodos_root: {}".format(self.discodos_root))
        # config.yaml handling
        self.conf = read_yaml( self.discodos_root / "config.yaml")
        if not self.conf:
            self.create_conf()
            raise SystemExit()
        # db file handling
        db_file = self._get_config_entry('discobase_file') # maybe configured?
        if not db_file: # if not set default value
            db_file = 'discobase.db'
        self.discobase = self.discodos_root / db_file
        log.info("Config.discobase: {}".format(self.discobase))

        try: # optional setting log_level
            self.log_level = self.conf["log_level"]
            log.info("config.yaml entry log_level is {}.".format(
                self.log_level))
        except KeyError:
            self.log_level = "WARNING"
            log.warn("config.yaml entry log_level not set, will take from cli option or default.")
        # then other settings
        self.discogs_token = self._get_config_entry('discogs_token', False)
        self.discogs_appid = 'DiscoDOS/1.0 +https://github.com/JOJ0/discodos'
        self.musicbrainz_appid = ['1.0', 'DiscoDOS https://github.com/JOJ0/discodos']
        self.dropbox_token = self._get_config_entry('dropbox_token')
        self.musicbrainz_user = self._get_config_entry('musicbrainz_user')
        self.musicbrainz_password = self._get_config_entry('musicbrainz_password')
        self.webdav_user = self._get_config_entry('webdav_user')
        self.webdav_password = self._get_config_entry('webdav_password')
        self.webdav_url = self._get_config_entry('webdav_url')

    def _get_config_entry(self, yaml_key, optional = True):
        if optional:
            try:
                if self.conf[yaml_key] == '':
                    value = ''
                    log.info("config.yaml entry {} is empty.".format(yaml_key))
                else:
                    value = self.conf[yaml_key]
                    log.info("config.yaml entry {} is set.".format(yaml_key))
            except KeyError:
                value = ''
                log.info("config.yaml entry {} is missing.".format(yaml_key))
            return value
        else:
            try: # essential settings entries should error and exit
                value = self.conf[yaml_key]
            except KeyError as ke:
                log.error("Missing essential entry in config.yaml: {}".format(ke))
                raise SystemExit(3)
            return value

    # install cli command (disco) into discodos_root
    def install_cli(self):
        log.info('Config.cli: We are on a "{}" OS'.format(os.name))
        if os.name == 'posix':
            disco_file = self.discodos_root / 'disco'
            venv_act = Path(os.getenv('VIRTUAL_ENV')) / 'bin' / 'activate'
            script_contents = '#!/bin/bash\n'
            script_contents+= '# This is the DiscoDOS cli wrapper.\n'
            script_contents+= 'source "{}"\n'.format(venv_act)
            script_contents+= '"{}" "$@"\n'.format(self.discodos_root / 'cli.py')
            sysinst = self.discodos_root / 'install_cli_system.sh'
            sysinst_contents = 'sudo -p "Need your users password to allow '
            sysinst_contents+= 'systemwide installation of disco cli command: " '
            sysinst_contents+=  'cp {} /usr/local/bin\n'.format(disco_file)
        elif os.name == 'nt':
            disco_file = self.discodos_root / 'disco.bat'
            script_contents = '@echo off\n'
            script_contents+= 'rem This is the DiscoDOS cli wrapper.\n'
            script_contents+= 'setlocal enableextensions\n'
            script_contents+= '"{}" %*\n'.format(self.discodos_root / 'cli.py')
            script_contents+= 'endlocal\n'
            discoshell = self.discodos_root / 'discoshell.bat'
            venv_act = Path(os.getenv('VIRTUAL_ENV')) / 'Scripts' / 'activate.bat'
            discoshell_contents = 'start "DiscoDOS shell" /D "{}" "{}"\n'.format(
                self.discodos_root, venv_act)
        else:
            log.warn("Config.cli: Unknown OS - not creating disco cli wrapper.")
            return True

        if disco_file.is_file(): # install wrappers only if non-existent
            log.info("Config.cli: DiscoDOS cli wrapper is already existing: {}".format(
                disco_file))
        else:
            print_help("\nInstalling DiscoDOS cli wrapper: {}".format(disco_file))
            self._write_textfile(script_contents, disco_file)
            if os.name == "posix":
                disco_file.chmod(0o755)
                print("You can now use the DiscoDOS cli using ./disco")
                self._write_textfile(sysinst_contents, sysinst)
                sysinst.chmod(0o755)
                hlpmsg ="Execute ./{} for systemwide installation".format(sysinst.name)
                hlpmsg+="\n(makes disco command executable from everywhere)."
                print_help(hlpmsg)
            elif os.name == "nt":
                print_help('Installing DiscoDOS shell: {}'.format(discoshell))
                self._write_textfile(discoshell_contents, discoshell)
                hlpshmsg = 'Usage: Double click discoshell.bat to open the "DiscoDOS shell" '
                hlpshmsg+= 'window; Now enter "disco ..." or "setup ..." commands.'
                print_help(hlpshmsg)

    # write a textile (eg. shell script)
    def _write_textfile(self, contents, file):
        """contents expects string, file expects path/file"""
        try:
            with open(file, "w") as f_file:
                f_file.write(contents)
                log.info("File %s successfully written", file)
            return True
        except IOError as errio:
            log.error("IOError: could not write file %s \n\n", file)
            raise errio
        except Exception as err:
            log.error(" trying to write %s \n\n", file)
            raise err
            #raise SystemExit(3)

    def create_conf(self):
        '''creates config.yaml'''
        config = {
            'discogs_token': '',
            'log_level': "WARNING",
            'dropbox_token': '',
            'musicbrainz_user': '',
            'musicbrainz_password': '',
            'webdav_user': '',
            'webdav_password': '',
            'webdav_url': '',
            'discobase_file': 'discobase.db'
        }
        create_msg = '\nCreating config file...'
        log.info(create_msg)
        print(create_msg)
        written = self._write_yaml(config, self.discodos_root / 'config.yaml')
        if written:
            written_msg = 'Now please open the file config.yaml with a '
            written_msg+= 'texteditor and set a value for discogs_token!\n'
            written_msg+= 'Read how to get a Discogs token here: '
            written_msg+= 'https://github.com/JOJ0/discodos#configuring-discogs-api-access\n'
            written_msg+= "Run setup again, when your're done!"
            log.info(written_msg)
            print_help(written_msg)

    def _write_yaml(self, data, yamlfile):
        """data expects dict, yamlfile expects path/file"""
        try:
            with open(yamlfile, "w") as fyamlfile:
                yaml.dump(data, fyamlfile, default_flow_style=False,
                                 allow_unicode=True)
                return True
        except IOError as errio:
            log.error("IOError: could not write file %s \n\n", yamlfile)
            raise errio
        except Exception as err:
            log.error(" trying to write %s \n\n", yamlfile)
            raise err
            raise SystemExit(3)