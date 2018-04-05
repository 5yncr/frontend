import datetime
import os

import bencode

HANDLE_FRONTEND_REQUEST = 'handle_frontend_request'
FILENAME = 'communication.txt'
TIMEOUT = 10.0


class Communicator:
    """
    Communicator class writes and reads to a file
    that is used to communicate with the backend
    of the 5yncr system
    """

    cached_timestamp = None

    def __init__(self):
        self.cached_timestamp = datetime.datetime.fromtimestamp(
            os.stat(os.path.join(os.pardir, FILENAME)).st_mtime,
        )

    def send_message(self, msg):
        """
        Writes specified message to file that will be read by backend
        :param msg: dictionary of info to be sent to backend
        :return:
        """

        written = None

        with open(os.path.join(os.pardir, FILENAME), 'w') as file:

            msg['request_type'] = HANDLE_FRONTEND_REQUEST

            # Convert dictionary to send-able type
            data_string = bencode.encode(msg)

            # Send data to backend
            written = file.write(data_string)

            # Update stored timestamp
            self.cached_timestamp = datetime.datetime.fromtimestamp(
                os.stat(os.path.join(os.pardir, FILENAME)).st_mtime,
            )

        # Check if write was successful
        if written is not None:
            return None
        else:
            return 'Backend Communication Error - error sending'

    def receive_message(self):
        """
        Listen for file to be updated by backend before reading
        response in from file. If file is not updated within set
        interval, returns error message to frontend
        :return:
        """

        data_string = None

        with open(os.path.join(os.pardir, FILENAME), 'w') as file:
            # Get current modified timestamp
            timestamp = datetime.datetime.fromtimestamp(
                os.stat(os.path.join(os.pardir, FILENAME)).st_mtime,
            )

            # Set up timeout
            start_time = datetime.datetime.now()
            time_passed = 0

            # Wait for file change or until set interval passes
            while self.cached_timestamp == timestamp and time_passed < TIMEOUT:
                timestamp = datetime.datetime.fromtimestamp(
                    os.stat(os.path.join(os.pardir, FILENAME)).st_mtime,
                )
                time_passed = (
                    datetime.datetime.now() -
                    start_time
                ).total_seconds()

            if time_passed >= TIMEOUT:
                return 'Backend Communication Error - timeout'

            # Read updated file
            data_string = file.read()

        if data_string is None:
            return 'Backend Communication Error - error receiving'

        # Decode data
        response = bencode.decode(data_string)

        # Example response for initial UI setup
        # response = {
        #     'drop_id': message.get('drop_id'),
        #     'drop_name': message.get('drop_name'),
        #     'file_name': message.get('file_name'),
        #     'file_path': message.get('file_path'),
        #     'action': message.get('action'),
        #     'message': "Generic Message For " + message.get('action'),
        #     'success': True,
        #     'requested_drops': (
        #         {
        #             'drop_id': 'o1',
        #             'name': 'O_Drop_1',
        #             'version': None,
        #             'previous_versions': [],
        #             'primary_owner': 'p_owner_id',
        #             'other_owners': ["owner1", "owner2"],
        #             'signed_by': 'owner_id',
        #             'files': [
        #                 {'name': 'FileOne'},
        #                 {'name': 'FileTwo'},
        #                 {'name': 'FileThree'},
        #                 {'name': 'FileFour'},
        #                 {'name': 'Folder'},
        #             ],
        #         },
        #         {
        #             'drop_id': 'o2',
        #             'name': 'O_Drop_2',
        #             'version': None,
        #             'previous_versions': [],
        #             'primary_owner': 'owner_id',
        #             'other_owners': [],
        #             'signed_by': 'owner_id',
        #             'files': [],
        #         },
        #     ),
        # }

        return response
