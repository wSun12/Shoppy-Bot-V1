using System;
using System.Threading.Tasks;
using Discord;
using Discord.WebSocket;

namespace PoelPospalBot
{
    class Program
    {
        public static Task Main(string[] args)
            => Startup.RunAsync(args);
    }
}
