# Telegram bot on Vercel

This bot uses Telegram webhooks on Vercel. Its FSM state is stored in Redis so
conversation state survives separate serverless function invocations.

## Deploy

1. Import this GitHub repository into Vercel and deploy it.
2. Add these environment variables to the Vercel project:
   - `BOT_TOKEN`: the bot token from BotFather.
   - `WEBHOOK_SECRET`: a random 1-256 character string containing only letters,
     digits, `_`, or `-`.
   - `REDIS_URL`: the Redis connection URL (`redis://` or `rediss://`) from an
     Upstash Redis database.
3. Ensure **System Environment Variables** are enabled for the project.
4. Redeploy after saving the environment variables.
5. Open the production deployment URL once. On its first request, the app
   registers the Telegram webhook using Vercel's production URL automatically.

The webhook endpoint is `/webhook`. The root URL returns a small health check.
