class ContextActions:
    """static class to run actions related to the Discord's API context."""
    ctx = ""  # Context object related to discord's channel and user's message.
    author_object = ""  # Depends on each context

    @staticmethod
    def set_ctx(new_ctx):
        """Store a new context."""
        ContextActions.ctx = new_ctx
        ContextActions.author_object = ContextActions.ctx.message.author

    @staticmethod
    async def send_message(message):
        await ContextActions.ctx.send(message)

    @staticmethod
    async def send_mention_message(message):
        await ContextActions.ctx.send(f"{ContextActions.author_object.mention} : {message}")

    @staticmethod
    async def send_warning(message):
        my_id = '326766231845601281'
        user = ContextActions.ctx.get_member(my_id)
        await user.send(message)


