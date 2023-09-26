from application.utils import send_email_notification
from db.postgre_managers import TwitchRelationalManager

from twitch.service import TwitchParser


async def get_live_subscribed_streams(db: TwitchRelationalManager, parser: TwitchParser) -> None:
    followed_users = await db.get_followed_users()
    followed_users = followed_users[:200]
    batched_followed_users = [
        list(map(lambda user: user.twitch_user_id, followed_users[i : i + 100]))
        for i in range(0, len(followed_users), 100)
    ]
    for batch in batched_followed_users:
        query_params = {
            "user_id": batch,
            "type": "live",
        }
        counter = 0
        for stream in parser.get_streams(query_params=query_params, streams_amount=len(batch)):
            counter += 1
            if not (await db.check_stream_notifications(stream)):
                followers = await db.get_users_followed_to_streamer(stream.user.twitch_user_id)
                followers_emails = list(map(lambda user: user.email, followers))
                email_body = f"Streamer {stream.user.display_name} has just started translation {stream.stream_title}"
                await send_email_notification(followers_emails, email_body)
                await db.save_notifications(followers, stream)
