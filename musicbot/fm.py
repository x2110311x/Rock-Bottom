import pylast
import time
import logging

import datetime

from .config import Config, ConfigDefaults

log = logging.getLogger(__name__)

class EmptyTrackException(Exception):
    pass

class EmptyArtistException(Exception):
    pass

class EmptyTrackArtistException(Exception):
    pass

class FM:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = ConfigDefaults.options_file

        self.config= Config(config_file)
        try:
            self.LFMNet = pylast.LastFMNetwork(
                api_key = self.config.lastfmkey,
                api_secret = self.config.lastfmsecret,
                username = self.config.lastfmusername,
                password_hash = pylast.md5(self.config.lastfmpassword)
            )
            log.info("Successfully authenticated with Last.FM")
        except Exception as e:
            log.error(f"Unable to login to FM - {e}")

    def split_artist_track(self, artist_track):
        artist_track = artist_track.replace(" – ", " - ")
        artist_track = artist_track.replace("“", '"')
        artist_track = artist_track.replace("”", '"')

        TRACK_SEPARATOR = " - "
        (artist, track) = artist_track.split(TRACK_SEPARATOR)
        artist = artist.strip() 
        track = track.strip()
        log.info("Artist:\t\t'" + artist + "'")
        log.info("Track:\t\t'" + track + "'")

        # Validate
        if len(artist) == 0 and len(track) == 0:
            raise EmptyTrackArtistException
        if len(artist) == 0:
            raise EmptyArtistException
        if len(track) == 0:
            raise EmptyTrackException
        return (artist, track)
    
    def now_playing(self, artist_track):
        try:
            (artist, track) = self.split_artist_track(artist_track)
            self.LFMNet.update_now_playing(artist=artist, title=track)
            log.info(f"Sent Now Playing to FM - {track} by {artist}")
        except EmptyArtistException:
            log.error("No artist in the current playing. Can't mark as now playing")
        except EmptyTrackException:
            log.error("No track name in the current playing. Can't mark as now playing")
        except EmptyTrackArtistException:
            log.error("Both the track and artist names are blank. Can't mark as now playing")
        except Exception as e:
            log.error(f"Could not mark as now playing - {e}")

    def scrobble(self, artist_track):
        try:
            (artist, track) = self.split_artist_track(artist_track)
            unix_timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
            self.LFMNet.scrobble(artist=artist, title=track, timestamp=unix_timestamp)
            log.info(f"Scrobbled to FM - {track} by {artist}")
        except EmptyArtistException:
            log.error("No artist in the current playing. Can't scrobble")
        except EmptyTrackException:
            log.error("No track name in the current playing. Can't scrobble")
        except EmptyTrackArtistException:
            log.error("Both the track and artist names are blank. Can't scrobble")
        except Exception as e:
            log.error(f"Could not scrobble - {e}")
        