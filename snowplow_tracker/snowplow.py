# """
#     snowplow.py

#     Copyright (c) 2013-2022 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.

#     Authors: Jack Keene, Anuj More, Alex Dean, Fred Blundun, Paul Boocock
#     Copyright: Copyright (c) 2013-2022 Snowplow Analytics Ltd
#     License: Apache License Version 2.0
# """
import logging
from typing import  Optional
from snowplow_tracker import Tracker, Emitter, subject, EmitterConfiguration
from snowplow_tracker.typing import JsonEncoderFunction

# Logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
    

"""
Snowplow Class
"""
class Snowplow:
    trackers = {}

    @staticmethod
    def create_tracker( 
                namespace: str,
                endpoint: str,
                emitter_config: EmitterConfiguration = EmitterConfiguration(), 
                app_id = None,
                subject: Optional[subject.Subject] = None,
                encode_base64: bool = None,
                json_encoder: Optional[JsonEncoderFunction] = None
            ):
        """
            Create a Snowplow tracker with a tracker_namespace and collector URL

            :param  namespace:          Name of the tracker
            :type   namespace:          String
            :param  endpoint:           The collector URL
            :type   endpoint:           String | None
            :param  emitter_config:     Emitter configuration
            :type   emitter_config:     EmitterConfiguration | None
            :param  appId:              Application ID
            :type   appId:              String | None 
        """
        if endpoint is None:
            raise TypeError("Emitter or Collector URL must be provided")     
        
        emitter = Emitter(
            endpoint, 
            buffer_size=emitter_config.buffer_size, 
            on_success=emitter_config.on_success, 
            on_failure=emitter_config.on_failure, 
            byte_limit=emitter_config.byte_limit,
            request_timeout=emitter_config.request_timeout
        )     

        tracker = Tracker(
            emitter, 
            namespace = namespace, 
            app_id=app_id, 
            subject=subject, 
            encode_base64=encode_base64, 
            json_encoder=json_encoder
        )

        Snowplow.add_tracker(tracker)
    
    @classmethod
    def add_tracker(cls, tracker: Tracker):
        """
            Add a Snowplow tracker to the Snowplow object

            :param  tracker:  Tracker object to add to Snowplow
            :type   tracker:  Tracker
        """
        tracker_name = cls.get_tracker_name(tracker)
        
        if tracker_name in cls.trackers.keys():
            raise TypeError("Tracker with this namespace already exists")      
        
        cls.trackers[tracker_name] = tracker
        logger.info("Tracker with namespace: '" + tracker_name + "' added to Snowplow")

    @classmethod
    def remove_tracker(cls, tracker: Tracker=None, tracker_name:str = None):
        """
            Remove a Snowplow tracker from the Snowplow object if it exists

            :param  tracker:        Tracker object to remove from Snowplow
            :type   tracker:        Tracker | None
            :param  tracker_name:   Tracker namespace to remove from Snowplow
            :type   tracker:        String | None
        """
        if tracker is not None:
            tracker_name = tracker.standard_nv_pairs['tna']
        cls.trackers.pop(tracker_name)
        logger.info("Tracker with namespace: '" + tracker_name + "' removed from Snowplow")

    @classmethod
    def reset(cls):
        cls.trackers = {}

    @classmethod
    def get_tracker_name(cls, tracker: Tracker):
        return tracker.standard_nv_pairs['tna']
        
    @classmethod
    def get_tracker(cls, tracker_name: str):
        return cls.trackers[tracker_name]