
using Discord;
using Discord.Commands;
using Discord.WebSocket;
using System.Linq;
using System.Threading.Tasks;

namespace PoelPospalBot.Modules
{
    class Emoji : ModuleBase<SocketCommandContext>
    {
        public async Task SetEmojiAsync(SocketCommandContext Context)
        {
            if (Context.Message == null) return;
            IEmote emote = Emote.Parse("<:maddyking:856531445966831666>");

            await Context.Message.AddReactionAsync(emote);
        }
    }
}
