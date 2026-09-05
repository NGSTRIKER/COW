import discord


class ConfirmView(discord.ui.View):
    def __init__(
        self,
        author: discord.Member,
        timeout: float = 60,
    ):
        super().__init__(timeout=timeout)

        self.author = author
        self.value = None
        self.message: discord.Message | None = None

    async def interaction_check(
        self,
        interaction: discord.Interaction,
    ) -> bool:

        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Only the person who ran this command can use these buttons.",
                ephemeral=True,
            )
            return False

        return True

    @discord.ui.button(
        label="Confirm",
        emoji="✅",
        style=discord.ButtonStyle.green,
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.value = True

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            view=self
        )

        self.stop()

    @discord.ui.button(
        label="Cancel",
        emoji="❌",
        style=discord.ButtonStyle.red,
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.value = False

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            view=self
        )

        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass