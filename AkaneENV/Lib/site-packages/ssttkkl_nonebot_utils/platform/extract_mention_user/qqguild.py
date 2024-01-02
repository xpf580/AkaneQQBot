from typing import Optional

from nonebot.adapters.qqguild import MessageSegment


def extract_mention_user(seg: MessageSegment) -> Optional[str]:
    if seg.type == 'mention_user':
        return seg.data['user_id']
    else:
        return None
