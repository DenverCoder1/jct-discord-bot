insert into channel_messages
(message, referenced_channel, host_channel)
values
(%(message_id)s, %(referenced_channel_id)s, %(host_channel_id)s)