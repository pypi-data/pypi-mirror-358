from aiogram import Bot as BaseBot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import UpdateType
from tortoise.backends.asyncpg import AsyncpgDBClient


class Bot(BaseBot):
    dp: Dispatcher
    wh: str = None
    au: list[str] = [
        UpdateType.MESSAGE,
        UpdateType.EDITED_MESSAGE,
        UpdateType.CHANNEL_POST,
        UpdateType.EDITED_CHANNEL_POST,
        UpdateType.BUSINESS_CONNECTION,
        UpdateType.BUSINESS_MESSAGE,
        UpdateType.EDITED_BUSINESS_MESSAGE,
        UpdateType.DELETED_BUSINESS_MESSAGES,
        UpdateType.MESSAGE_REACTION,
        UpdateType.MESSAGE_REACTION_COUNT,
        UpdateType.INLINE_QUERY,
        UpdateType.CHOSEN_INLINE_RESULT,
        UpdateType.CALLBACK_QUERY,
        UpdateType.SHIPPING_QUERY,
        UpdateType.PRE_CHECKOUT_QUERY,
        UpdateType.PURCHASED_PAID_MEDIA,
        UpdateType.POLL,
        UpdateType.POLL_ANSWER,
        UpdateType.MY_CHAT_MEMBER,
        UpdateType.CHAT_MEMBER,
        UpdateType.CHAT_JOIN_REQUEST,
        UpdateType.CHAT_BOOST,
        UpdateType.REMOVED_CHAT_BOOST,
    ]

    def __init__(
        self,
        token: str,
        routers: list[Router] = None,
        cn: AsyncpgDBClient = None,
        api_host: str = None,
        app_host: str = None,
        session: BaseSession = None,
        default: DefaultBotProperties = None,
        **kwargs,
    ) -> None:
        self.cn = cn
        self.wh = api_host
        self.app_host = app_host
        super().__init__(token, session, default, **kwargs)
        self.dp = Dispatcher()
        if routers:
            self.dp.include_routers(*routers)
        self.dp.shutdown.register(self.stop)

    async def start(self):
        webhook_info = await self.get_webhook_info()
        if not self.wh:
            if webhook_info.url:
                await self.delete_webhook(True)
            await self.dp.start_polling(self, polling_timeout=300, allowed_updates=self.au)
            return
        """ WEBHOOK SETUP """
        if webhook_info.url != self.wh:
            await self.set_webhook(
                url=self.wh,
                drop_pending_updates=True,
                allowed_updates=self.au,
                secret_token=self.token.split(":")[1],
                request_timeout=300,
            )

    async def stop(self) -> None:
        """CLOSE BOT SESSION"""
        await self.delete_webhook(drop_pending_updates=True)
        await self.session.close()
