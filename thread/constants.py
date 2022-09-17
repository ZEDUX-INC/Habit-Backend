MUSIC_THREAD = 0
PHOTO_THREAD = 1
POST_THREAD = 2
THREAD_TYPES = (
    (MUSIC_THREAD, "Music Thread"),
    (PHOTO_THREAD, "Photo Thread"),
    (POST_THREAD, "Post Thread"),
)

ALLOW_REPLY_FROM_ALL = 0
ALLOW_REPLY_FROM_FOLLOWERS = 1
ALLOW_REPLY_FROM_MENTIONED = 2
THREAD_REPLY_SETTINGS = (
    (ALLOW_REPLY_FROM_ALL, "Allow all user to reply"),
    (ALLOW_REPLY_FROM_FOLLOWERS, "Allow only followers to reply"),
    (ALLOW_REPLY_FROM_MENTIONED, "Allow only mentiond users to reply"),
)

BYTE_PER_MB = 1048576
