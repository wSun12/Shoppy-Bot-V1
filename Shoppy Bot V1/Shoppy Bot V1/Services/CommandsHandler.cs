using Discord.Commands;
using Discord.WebSocket;
using Microsoft.Extensions.Configuration;
using System;
using System.Threading.Tasks;
using PoelPospalBot.Modules;

namespace PoelPospalBot.Services
{
    public class CommandsHandler
    {
        private readonly IServiceProvider _provider;
        private readonly DiscordSocketClient _discord;
        private readonly CommandService _commands;
        private readonly IConfigurationRoot _config;

        public CommandsHandler(
            IServiceProvider provider,
            DiscordSocketClient discord,
            CommandService commands,
            IConfigurationRoot config)
        {
            _provider = provider;
            _discord = discord;
            _commands = commands;
            _config = config;

            _discord.MessageReceived += OnMessageReceiveAsync;
        }

        private async Task OnMessageReceiveAsync(SocketMessage sm)
        {
            var msg = sm as SocketUserMessage;
            if (msg == null)
            {
                return;
            }
            if (msg.Author.Id == _discord.CurrentUser.Id)
            {
                return;
            }
            var context = new SocketCommandContext(_discord, msg);
            int argPos = 0;

            await new Emoji().SetEmojiAsync(context); // React with emotion on every message

            if (msg.HasStringPrefix(_config["Discord:Prefix"], ref argPos) || msg.HasMentionPrefix(_discord.CurrentUser, ref argPos))
            {
                var result = await _commands.ExecuteAsync(context, argPos, _provider);
                if (!result.IsSuccess)
                {
                    await new PepeModule().PepeErrorMsgAsync(context, result.ToString());
                }
            }
        }
    }
}
