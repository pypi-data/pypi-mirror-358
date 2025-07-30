#!/usr/bin/env python
# coding: utf-8

"""
prismedia - tool to upload videos to Peertube and Youtube

Usage:
  prismedia --file=<FILE> [options]
  prismedia -f <FILE> --tags=STRING [options]
  prismedia --hearthbeat
  prismedia -h | --help
  prismedia --version

Options:
  -f, --file=STRING Path to the video file to upload. This is the only mandatory option.
  --name=NAME  Name of the video to upload. (default to video filename)
  -d, --description=STRING  Description of the video. (default: default description)
  -t, --tags=STRING  Tags for the video. comma separated.
                     WARN: tags with punctuation (!, ', ", ?, ...)
                           are not supported by Mastodon to be published from Peertube
  -c, --category=STRING  Category for the videos, see below. (default: Films)
  --cca  License should be CreativeCommon Attribution (affects Youtube upload only)
  -p, --privacy=STRING  Choose between public, unlisted or private. (default: private)
  --disable-comments  Disable comments (Peertube only as YT API does not support) (default: comments are enabled)
  --nsfw  Set the video as No Safe For Work (Peertube only as YT API does not support) (default: video is safe)
  --nfo=STRING  Configure a specific nfo file to set options for the video.
                By default Prismedia search a .txt based on the video name and will
                decode the file as UTF-8 (so make sure your nfo file is UTF-8 encoded)
                See nfo_example.txt for more details
  --credentialsdir=STRING  Set directory where to search for secret file.
  --platform=STRING  List of platform(s) to upload to, comma separated.
                     Supported platforms are youtube and peertube (default is both)
  --language=STRING  Specify the default language for video. See below for supported language. (default is English)
  --publishAt=DATE  Publish the video at the given DATE using local server timezone.
                    DATE should be on the form YYYY-MM-DDThh:mm:ss eg: 2018-03-12T19:00:00
                    DATE should be in the future
  --peertubeAt=DATE
  --youtubeAt=DATE  Override publishAt for the corresponding platform. Allow to create preview on specific platform
  --originalDate=DATE  Configure the video as initially recorded at DATE
                        DATE should be on the form YYYY-MM-DDThh:mm:ss eg: 2018-03-12T19:00:00
                        DATE should be in the past
  --auto-originalDate     Automatically use the file modification time as original date
  --thumbnail=STRING    Path to a file to use as a thumbnail for the video.
                        By default, prismedia search for an image based on video name followed by .jpg, .jpeg or .png
  --channel=STRING Set the channel to use for the video (Peertube only)
                    If the channel is not found, spawn an error except if --channelCreate is set.
  --channelCreate  Create the channel if not exists. (Peertube only, default do not create)
                   Only relevant if --channel is set.
  --playlist=STRING Set the playlist to use for the video.
                    If the playlist is not found, spawn an error except if --playlistCreate is set.
  --playlistCreate  Create the playlist if not exists. (default do not create)
                    Only relevant if --playlist is set.
  --progress=STRING Set the progress bar view, one of percentage, bigFile (MB), accurate (KB).

  --hearthbeat  Use some credits to show some activity for you apikey so the platform know it is used and would not put your quota to 0 (only Youtube currently)

  -h --help  Show this help.
  --version  Show version.

Logging options
  -q --quiet        Suppress any log except Critical (alias for --log=critical).
  --log=STRING      Log level, between debug, info, warning, error, critical. Ignored if --quiet is set (default to info)
  -u --url-only     Display generated URL after upload directly on stdout, implies --quiet
  --batch           Display generated URL after upload with platform information for easier parsing. Implies --quiet
                    Be careful --batch and --url-only are mutually exclusives.

Strict options:
  Strict options allow you to force some option to be present when uploading a video. It's useful to be sure you do not
  forget something when uploading a video, for example if you use multiples NFO. You may force the presence of description,
  tags, thumbnail, ...
  All strict option are optionals and are provided only to avoid errors when uploading :-)
  All strict options can be specified in NFO directly, the only strict option mandatory on cli is --withNFO
  All strict options are off by default

  --withNFO         Prevent the upload without a NFO, either specified via cli or found in the directory
  --withThumbnail       Prevent the upload without a thumbnail
  --withName        Prevent the upload if no name are found
  --withDescription     Prevent the upload without description
  --withTags        Prevent the upload without tags
  --withPlaylist    Prevent the upload if no playlist
  --withPublishAt    Prevent the upload if no schedule
  --withOriginalDate    Prevent the upload if no original date configured
  --withPlatform    Prevent the upload if at least one platform is not specified
  --withCategory    Prevent the upload if no category
  --withLanguage    Prevent upload if no language
  --withChannel     Prevent upload if no channel

Categories:
  Category is the type of video you upload. Default is films.
  Here are available categories from Peertube and Youtube:
    music, films, vehicles,
    sports, travels, gaming, people,
    comedy, entertainment, news,
    how to, education, activism, science & technology,
    science, technology, animals

Languages:
  Language of the video (audio track), choose one. Default is English
  Here are available languages from Peertube and Youtube:
    Arabic, English, French, German, Hindi, Italian,
    Japanese, Korean, Mandarin, Portuguese, Punjabi, Russian, Spanish

"""
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import datetime
import logging
logger = logging.getLogger('Prismedia')

from docopt import docopt

from . import yt_upload
from . import pt_upload
from . import utils

try:
    # noinspection PyUnresolvedReferences
    from schema import Schema, And, Or, Optional, SchemaError, Hook, Use
except ImportError:
    logger.critical('This program requires that the `schema` data-validation library'
                  ' is installed: \n'
                  'see https://github.com/halst/schema\n')
    exit(1)

VERSION = "prismedia v0.12.2"

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
VALID_CATEGORIES = (
    "music", "films", "vehicles",
    "sports", "travels", "gaming", "people",
    "comedy", "entertainment", "news",
    "how to", "education", "activism", "science & technology",
    "science", "technology", "animals"
)
VALID_PLATFORM = ('youtube', 'peertube', 'none')
VALID_LANGUAGES = ('arabic', 'english', 'french',
                   'german', 'hindi', 'italian',
                   'japanese', 'korean', 'mandarin',
                   'portuguese', 'punjabi', 'russian', 'spanish')
VALID_PROGRESS = ('percentage', 'bigfile', 'accurate')


def validateCategory(category):
    if category.lower() in VALID_CATEGORIES:
        return True
    else:
        return False


def validatePrivacy(privacy):
    if privacy.lower() in VALID_PRIVACY_STATUSES:
        return True
    else:
        return False


def validatePlatform(platform):
    for plfrm in platform.split(','):
        if plfrm.lower().replace(" ", "") not in VALID_PLATFORM:
            return False

    return True


def validateLanguage(language):
    if language.lower() in VALID_LANGUAGES:
        return True
    else:
        return False


def validatePublishDate(publishDate):
    # Check date format and if date is future
    try:
        now = datetime.datetime.now()
        publishAt = datetime.datetime.strptime(publishDate, '%Y-%m-%dT%H:%M:%S')
        if now >= publishAt:
            return False
    except ValueError:
        return False
    return True


def validateOriginalDate(originalDate):
    # Check date format and if date is past
    try:
        now = datetime.datetime.now()
        originalDate = datetime.datetime.strptime(originalDate, '%Y-%m-%dT%H:%M:%S')
        if now <= originalDate:
            return False
    except ValueError:
        return False
    return True


def validateLogLevel(loglevel):
    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        return False
    return True


def validateProgress(progress):
    for prgs in progress.split(','):
        if prgs.lower().replace(" ", "") not in VALID_PROGRESS:
            return False

    return True


def _optionnalOrStrict(key, scope, error):
    option = key.replace('-', '')
    option = option[0].upper() + option[1:]
    if scope["--with" + option] is True and scope[key] is None:
        logger.critical("Prismedia: you have required the strict presence of " + key + " but none is found")
        exit(1)
    return True


def configureLogs(options):
    if options.get('--batch') and options.get('--url-only'):
        logger.critical("Prismedia: Please use either --batch OR --url-only, not both.")
        exit(1)
    # batch and url-only implies quiet
    if options.get('--batch') or options.get('--url-only'):
        options['--quiet'] = True

    for handler in logger.handlers or logger.parent.handlers:
        if options.get('--quiet'):
            # We need to set both log level in the same time
            logger.setLevel(50)
            handler.setLevel(50)
        elif options.get('--log'):
            numeric_level = getattr(logging, options["--log"], None)
            # We need to set both log level in the same time
            logger.setLevel(numeric_level)
            handler.setLevel(numeric_level)
        elif options.get('--debug'):
            # Deprecated,
            logger.setLevel(10)
            handler.setLevel(10)


def configureStdoutLogs():
    logger_stdout = logging.getLogger('stdoutlogs')
    logger_stdout.setLevel(logging.INFO)
    ch_stdout = logging.StreamHandler(stream=sys.stdout)
    ch_stdout.setLevel(logging.INFO)
    # Default stdout logs is url only
    formatter_stdout = logging.Formatter('%(message)s')
    ch_stdout.setFormatter(formatter_stdout)
    logger_stdout.addHandler(ch_stdout)

def main():
    options = docopt(__doc__, version=VERSION)

    earlyoptionSchema = Schema({
        Optional('--log'): Or(None, And(
                                str,
                                Use(str.upper),
                                validateLogLevel,
                                error="Log level not recognized")
                              ),
        Optional('--quiet', default=False): bool,
        Optional('--debug'): bool,
        Optional('--url-only', default=False): bool,
        Optional('--batch', default=False): bool,
        Optional('--withNFO', default=False): bool,
        Optional('--withThumbnail', default=False): bool,
        Optional('--withName', default=False): bool,
        Optional('--withDescription', default=False): bool,
        Optional('--withTags', default=False): bool,
        Optional('--withPlaylist', default=False): bool,
        Optional('--withPublishAt', default=False): bool,
        Optional('--withOriginalDate', default=False): bool,
        Optional('--withPlatform', default=False): bool,
        Optional('--withCategory', default=False): bool,
        Optional('--withLanguage', default=False): bool,
        Optional('--withChannel', default=False): bool,
        Optional('--credentialsdir'): Or(None, And(str, os.path.exists, error='credentialsdir does not exist')),
        # This allow to return all other options for further use: https://github.com/keleshev/schema#extra-keys
        object: object
    })

    schema = Schema({
        '--file': And(str, os.path.exists, error='file does not exists, please check path'),
        # Strict option checks - at the moment Schema needs to check Hook and Optional separately #
        Hook('--name', handler=_optionnalOrStrict): object,
        Hook('--description', handler=_optionnalOrStrict): object,
        Hook('--tags', handler=_optionnalOrStrict): object,
        Hook('--category', handler=_optionnalOrStrict): object,
        Hook('--language', handler=_optionnalOrStrict): object,
        Hook('--platform', handler=_optionnalOrStrict): object,
        Hook('--publishAt', handler=_optionnalOrStrict): object,
        Hook('--originalDate', handler=_optionnalOrStrict): object,
        Hook('--thumbnail', handler=_optionnalOrStrict): object,
        Hook('--channel', handler=_optionnalOrStrict): object,
        Hook('--playlist', handler=_optionnalOrStrict): object,
        # Validate checks #
        Optional('--name'): Or(None, And(
                                str,
                                lambda x: not x.isdigit(),
                                error="The video name should be a string")
                               ),
        Optional('--description'): Or(None, And(
                                        str,
                                        lambda x: not x.isdigit(),
                                        error="The video description should be a string")
                                      ),
        Optional('--tags'): Or(None, And(
                                    str,
                                    lambda x: not x.isdigit(),
                                    error="Tags should be a string")
                               ),
        Optional('--category'): Or(None, And(
                                    str,
                                    validateCategory,
                                    error="Category not recognized, please see --help")
                                   ),
        Optional('--language'): Or(None, And(
                                    str,
                                    validateLanguage,
                                    error="Language not recognized, please see --help")
                                   ),
        Optional('--privacy'): Or(None, And(
                                    str,
                                    validatePrivacy,
                                    error="Please use recognized privacy between public, unlisted or private")
                                  ),
        Optional('--nfo'): Or(None, str),
        Optional('--platform'): Or(None, And(str, validatePlatform, error="Sorry, upload platform not supported")),
        Optional('--publishAt'): Or(None, And(
                                    str,
                                    validatePublishDate,
                                    error="Publish Date should be the form YYYY-MM-DDThh:mm:ss and has to be in the future")
                                    ),
        Optional('--peertubeAt'): Or(None, And(
                                    str,
                                    validatePublishDate,
                                    error="Publish Date should be the form YYYY-MM-DDThh:mm:ss and has to be in the future")
                                    ),
        Optional('--youtubeAt'): Or(None, And(
                                    str,
                                    validatePublishDate,
                                    error="Publish Date should be the form YYYY-MM-DDThh:mm:ss and has to be in the future")
                                    ),
        Optional('--originalDate'): Or(None, And(
                                    str,
                                    validateOriginalDate,
                                    error="Original date should be the form YYYY-MM-DDThh:mm:ss and has to be in the past")
                                    ),
        Optional('--auto-originalDate'): bool,
        Optional('--cca'): bool,
        Optional('--disable-comments'): bool,
        Optional('--nsfw'): bool,
        Optional('--thumbnail'): Or(None, And(
                                    str, os.path.exists, error='Thumbnail does not exists, please check the path.'),
                                    ),
        Optional('--channel'): Or(None, str),
        Optional('--channelCreate'): bool,
        Optional('--playlist'): Or(None, str),
        Optional('--playlistCreate'): bool,
        Optional('--progress'): Or(None, And(str, validateProgress, error="Sorry, progress visualisation not supported")),
        '--hearthbeat': bool,
        '--help': bool,
        '--version': bool,
        # This allow to return all other options for further use: https://github.com/keleshev/schema#extra-keys
        object: object
    })

    if options.get('--hearthbeat'):
        yt_upload.hearthbeat()
        exit(0)

    # We need to validate early options first as withNFO and logs options should be prioritized
    try:
        options = earlyoptionSchema.validate(options)
        configureLogs(options)
    except SchemaError as e:
        logger.critical(e)
        exit(1)

    if options.get('--url-only') or options.get('--batch'):
        configureStdoutLogs()

    options = utils.parseNFO(options)

    # If after loading NFO we still has no original date and --auto-originalDate is enabled,
    # then we need to search from the file
    # We need to do that before the strict validation in case --withOriginalDate is enabled
    if not options.get('--originalDate') and options.get('--auto-originalDate'):
        options['--originalDate'] = utils.searchOriginalDate(options)

    # Once NFO are loaded, we need to revalidate strict options in case some were in NFO
    try:
        options = earlyoptionSchema.validate(options)
    except SchemaError as e:
        logger.critical(e)
        exit(1)

    if not options.get('--thumbnail'):
        options = utils.searchThumbnail(options)

    try:
        options = schema.validate(options)
    except SchemaError as e:
        logger.critical(e)
        exit(1)

    logger.debug("Python " + sys.version)
    logger.debug(options)

    if options.get('--platform') is None or "peertube" in options.get('--platform'):
        pt_upload.run(options)
    if options.get('--platform') is None or "youtube" in options.get('--platform'):
        yt_upload.run(options)


if __name__ == '__main__':
    logger.warning("DEPRECATION: use 'python -m prismedia', not 'python -m prismedia.upload'")
    main()
