using System;
using System.Linq;
using System.Threading.Tasks;
using System.Timers;
using Discord;
using Discord.Commands;
using Discord.WebSocket;
using Microsoft.Extensions.Configuration;

namespace PoelPospalBot.Services
{
    public class UserIntendService
    {
        private readonly DiscordSocketClient _discord;
        private readonly IConfigurationRoot _config;
        private Timer SheduleUpdateTimer;

        public UserIntendService(
            DiscordSocketClient discord,
            IConfigurationRoot config)
        {
            _discord = discord;
            _config = config;

            _discord.Ready += OncePerDayOnRestart;

            //SheduleUpdateTimer = new System.Timers.Timer(50); //calculate six hours in milliseconds
            //SheduleUpdateTimer.Elapsed += new ElapsedEventHandler(Check);
            //SheduleUpdateTimer.Start();
        }

        private void Check(object sender, ElapsedEventArgs e)
        {
            try
            {
                Console.WriteLine("I'll just check myself!");
                OncePerDayOnRestart();
            }
            catch (Exception ex)
            {
                throw new Exception($"Check exception: {ex.Message}");
            }
        }

        private async Task OncePerDayOnRestart()
        {
            var unixTimestamp = (ulong) DateTime.UtcNow.Subtract(new DateTime(1970, 1, 1)).TotalSeconds;

            if (_config["Herotimer"] == null || _config["Herotimer"] == "")
            {
                _config.GetSection("Herotimer").Value = "0";
            }
            var nextDayUnixTimeStamp = ulong.Parse(_config["Herotimer"]) + 76400;
            if (nextDayUnixTimeStamp <= unixTimestamp)
            {
                Console.WriteLine("It's hero time!");
            }
            else
            {
                Console.WriteLine("One hero per day!");
                return;
            }

            ulong guildID = Convert.ToUInt64(_config["Guild:id"]);
            var guild = _discord.GetGuild(guildID);

            ulong channelId = Convert.ToUInt64(_config["Guild:channel"]);
            var channel = _discord.GetChannel(channelId) as IMessageChannel;

            //await channel.SendMessageAsync("I'm alive.");
            await guild.DownloadUsersAsync();

            var takeUser = guild.Users.ElementAt((new Random().Next(1, guild.Users.Count)));
            var builder = new EmbedBuilder()
            {
                Title = "У нас новый герой!",
                Color = Color.Red,
                Description = $"{takeUser.Mention} ты был избран!",
            };
            builder.WithThumbnailUrl(takeUser.GetAvatarUrl());
            builder.WithCurrentTimestamp();

            _config.GetSection("Herotimer").Value = unixTimestamp.ToString();

            await channel.SendMessageAsync(null, false, builder.Build());
        }
    }
}
